"""Offline invariants plus opt-in SELECT-only MySQL integration checks."""
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services/core-api-backend"))
from src.services.reporting_scope import job_period_predicate, worker_batch
from src.services.grounded_skill_extraction import validate_skills


class IntegrityTests(unittest.TestCase):
    def test_period_requires_explicit_batch_not_job_id(self):
        for period in ("2026_Q2", "2026_Q3", "2026_Q4"):
            predicate = job_period_predicate(period)
            self.assertIn(worker_batch(period), predicate)
            self.assertNotIn("<= 1000", predicate)
        self.assertIn("quality_gate_passed=1", job_period_predicate("2026_ALL"))
        with self.assertRaises(ValueError):
            job_period_predicate("2026_Q2' OR 1=1")

    def test_grounding_excludes_locations_benefits_and_invented_evidence(self):
        source = "Yêu cầu biết Python và kiểm thử phần mềm."
        items = [
            {"name": "Python", "type": "HARD", "evidence": "biết Python và kiểm thử"},
            {"name": "Hải Dương", "type": "HARD", "evidence": source},
            {"name": "Du lịch hàng năm", "type": "HARD", "evidence": source},
            {"name": "Docker", "type": "TOOL", "evidence": "Có kinh nghiệm Docker"},
        ]
        self.assertEqual([s["name"] for s in validate_skills(items, source)], ["Python"])

    def test_software_testing_and_language_are_not_blanket_banned(self):
        source = "Must report test findings clearly and have clear pronunciation."
        items = [
            {"name": "report test findings", "type": "HARD", "evidence": "report test findings clearly"},
            {"name": "Phát âm chuẩn", "type": "LANGUAGE", "evidence": "have clear pronunciation"},
        ]
        self.assertEqual(len(validate_skills(items, source)), 2)


@unittest.skipUnless(os.getenv("RUN_CRAWLER_READONLY_TESTS") == "1", "requires local MySQL SELECT access")
class LiveReadOnlyTests(unittest.TestCase):
    def test_api_contract_matches_scoped_sql(self):
        from src.services.crawler_data_source import CrawlerDataSource
        from sqlalchemy import text
        source = CrawlerDataSource()
        payload = source.analytics(period="2026_Q2")
        locations = source.dashboard_locations(period="2026_Q2")
        self.assertEqual(locations[0]["job_count"], payload["kpi"]["total_jobs"])
        self.assertTrue(any(x["name"] == "Hà Nội" for x in locations))
        with source.connection() as conn:
            for key, ind_id in [("IT", 1), ("tourism", 2), ("logistics", 3), ("economics", 4)]:
                expected = conn.execute(text("SELECT COUNT(DISTINCT j.job_id) FROM jobs j JOIN positions pos ON pos.position_id=j.position_id WHERE j.status='active' AND pos.industry_id=:ind AND " + job_period_predicate("2026_Q2")), {"ind": ind_id}).scalar_one()
                detail = payload["industries_detail"][key]
                self.assertEqual(detail["jobs"], expected)
                for skill in detail["skills"]:
                    self.assertEqual(skill["demand_denom"], expected)
                    self.assertLessEqual(skill["demand_count"], expected)
                    self.assertEqual(skill["demand"], round(skill["demand_count"] * 100 / expected, 1))
                    if not detail["has_survey_data"]:
                        self.assertIsNone(skill["supply"])
                        self.assertIsNone(skill["gap"])
        self.assertEqual(payload["kpi"]["total_jobs"], sum(x["jobs"] for x in payload["industries_detail"].values()))
        pending = source.analytics(period="2026_Q3")
        self.assertEqual(pending["status"], "CLEANED_PREVIEW")
        self.assertFalse(pending["is_published"])
        self.assertEqual(pending["reporting_period"]["period_id"], "2026_Q3")
        with source.connection() as conn:
            expected_q3 = conn.execute(text("SELECT COUNT(DISTINCT j.job_id) FROM jobs j WHERE j.status='active' AND " + job_period_predicate("2026_Q3"))).scalar_one()
        self.assertEqual(pending["kpi"]["total_jobs"], expected_q3)


if __name__ == "__main__":
    unittest.main()

"""Formula invariants; fixtures exercise calculation only, never feed the dashboard."""
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services/core-api-backend'))
from src.services.skill_metrics import measure_skills, skill_types
from src.services.grounded_skill_extraction import validate_skills, redact_contacts
from src.services.grounded_skill_extraction import extract_grounded_skills


class SkillMetricsTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {i: {'skill_id': i, 'skill': str(i), 'skill_type': t}
                        for i, t in enumerate(['HARD', 'TOOL', 'SOFT', 'LANGUAGE', 'KNOWLEDGE', 'CERTIFICATION'], 1)}

    def test_union_shortage_surplus_balanced_and_dedup(self):
        rows = measure_skills(self.catalog, {1: {1, 2}, 2: {1}, 3: {1}},
                              {2: {10}, 3: {10, 11}, 4: {10}}, {1, 2}, {10, 11}, True)
        by_id = {r['skill_id']: r for r in rows}
        self.assertEqual(set(by_id), {1, 2, 3, 4})
        self.assertEqual((by_id[1]['supply'], by_id[1]['gap_state']), (0, 'shortage'))
        self.assertEqual((by_id[2]['gap'], by_id[2]['gap_state']), (0, 'balanced'))
        self.assertEqual((by_id[3]['gap'], by_id[3]['gap_state']), (-50, 'surplus'))
        self.assertEqual((by_id[4]['demand'], by_id[4]['gap']), (0, -50))

    def test_scope_intersection_and_type_do_not_change_denominators(self):
        row = measure_skills(self.catalog, {1: {1, 3}}, {1: {10, 12}},
                             {1, 2}, {10, 11}, True, 'HARD')[0]
        self.assertEqual((row['demand'], row['supply']), (50, 50))
        self.assertEqual((row['demand_denom'], row['supply_denom']), (2, 2))
        self.assertEqual(skill_types('MAIN_HARD'), {'HARD', 'TOOL', 'KNOWLEDGE', 'CERTIFICATION'})
        with self.assertRaises(ValueError):
            skill_types('INVALID')

    def test_unknown_extraction_is_not_zero_supply(self):
        row = measure_skills(self.catalog, {1: {1}}, {}, {1}, {10}, False)[0]
        self.assertIsNone(row['supply'])
        self.assertIsNone(row['gap'])
        self.assertEqual(row['gap_state'], 'insufficient')
        row = measure_skills(self.catalog, {}, {1: {10}}, set(), {10}, True)[0]
        self.assertIsNone(row['demand'])
        self.assertIsNone(row['gap'])

    def test_short_evidence_valid_and_mentions_not_skills(self):
        source = 'Required SQL and Git. B2B software sales.'
        values = [{'name': 'SQL', 'type': 'HARD', 'evidence': 'SQL', 'relation': 'required'},
                  {'name': 'Git', 'type': 'TOOL', 'evidence': 'Git', 'relation': 'preferred'},
                  {'name': 'B2B', 'type': 'HARD', 'evidence': 'B2B', 'relation': 'domain'}]
        self.assertEqual([s['name'] for s in validate_skills(values, source)], ['SQL', 'Git'])
        clean = redact_contacts('Contact sample@example.org or +84 901 234 567; SQL')
        self.assertNotIn('example.org', clean)
        self.assertNotIn('901', clean)
        self.assertIn('SQL', clean)

    @patch.dict('os.environ', {'GROQ_API_KEY':'local-test-placeholder','CRAWLER_EXTRACTION_MODEL':'test-model'})
    def test_provider_error_never_becomes_success(self):
        client = MagicMock()
        client.__enter__.return_value.post.return_value.status_code = 401
        with patch('src.services.grounded_skill_extraction.httpx.Client', return_value=client):
            with self.assertRaisesRegex(RuntimeError, 'HTTP 401'):
                extract_grounded_skills('Developer','SQL','IT')

    @patch.dict('os.environ', {'GROQ_API_KEY':'local-test-placeholder','CRAWLER_EXTRACTION_MODEL':'test-model'})
    def test_invalid_parser_never_becomes_success(self):
        client = MagicMock()
        resp = client.__enter__.return_value.post.return_value
        resp.status_code = 200
        resp.json.return_value = {'choices':[{'message':{'content':'not JSON'}}]}
        with patch('src.services.grounded_skill_extraction.httpx.Client', return_value=client):
            with self.assertRaisesRegex(ValueError,'invalid structured output'):
                extract_grounded_skills('Developer','SQL','IT')


if __name__ == '__main__':
    unittest.main()

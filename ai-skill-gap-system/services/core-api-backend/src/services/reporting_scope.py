"""Shared cohort predicates. Reporting batches are not posting-date quarters."""
import re


def job_period_predicate(period: str) -> str:
    if not re.fullmatch(r"2026_(?:Q[1-4]|ALL)", period):
        raise ValueError("Unsupported crawler reporting period")
    batch = {
        "2026_Q2": "BATCH_2026_Q2_VERIFIED",
        "2026_Q3": "BATCH_2026_Q3_RAW",
        "2026_Q4": "BATCH_2026_Q4_INGEST",
    }.get(period)
    if not batch:
        # ALL includes only published, quality-gated cohorts, never all jobs.
        return ("EXISTS (SELECT 1 FROM jobs_raw period_raw "
                "JOIN crawler_batches cb ON cb.batch_code=period_raw.batch_id "
                "JOIN reporting_datasets rd ON rd.dataset_id=cb.period_code "
                "WHERE period_raw.job_id=j.raw_job_id AND rd.is_published=1 "
                "AND cb.quality_gate_passed=1 AND cb.published_to_dashboard=1 "
                "AND cb.period_code LIKE '2026_Q%')") if period.endswith("ALL") else "1=0"
    clean_filter = " AND period_raw.llm_processed=1" if period == "2026_Q3" else ""
    return ("EXISTS (SELECT 1 FROM jobs_raw period_raw WHERE "
            f"period_raw.job_id=j.raw_job_id AND period_raw.batch_id='{batch}'{clean_filter})")


def worker_batch(period: str) -> str:
    if period not in ("2026_Q2", "2026_Q3", "2026_Q4"):
        raise ValueError("No verified worker cohort for this period")
    return {"2026_Q2": "BATCH_2026_Q2_VERIFIED", "2026_Q3": "BATCH_2026_Q3_RAW",
            "2026_Q4": "BATCH_2026_Q4_INGEST"}[period]

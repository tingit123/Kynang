from src.models.evidence import AnalysisRun, ApplicationEvidence
from src.models.quick_hire import FilterProfile
from src.services.evidence_matcher import digest, requirements_for, requirements_hash
from src.services.filter_counts import calculate


def application_skills(db, job_id, applications):
    """Bulk-read saved evidence, using the same active filter as quick recruitment."""
    if not applications:
        return {}
    profile = db.query(FilterProfile).filter_by(job_id=job_id).first()
    labels = requirements_for(db, job_id) if not profile else []
    items = profile.items if profile else [{"label": name, "kind": "skill", "level": "nice"} for name in labels]
    ids = [a.id for a in applications]
    runs = db.query(AnalysisRun).filter(AnalysisRun.application_id.in_(ids))
    if profile: runs = runs.filter_by(filter_profile_hash=profile.profile_hash)
    else: runs = runs.filter_by(filter_profile_hash=None, requirements_hash=requirements_hash(labels))
    latest = {}
    for run in runs.order_by(AnalysisRun.id.desc()).all():
        latest.setdefault(run.application_id, run)
    evidence = {}
    run_ids = [run.id for run in latest.values()]
    if run_ids:
        for row in db.query(ApplicationEvidence).filter(ApplicationEvidence.run_id.in_(run_ids)).all():
            evidence.setdefault(row.run_id, []).append({"requirement_name": row.requirement_name, "result": row.result, "review_result": row.review_result})
    result = {}
    for application in applications:
        run = latest.get(application.id)
        fresh = run is not None and run.cv_hash == digest(application.cv_snapshot_text or "")
        value = calculate(items, evidence.get(run.id, []) if run else [], run.status if fresh else None)
        result[application.id] = {"skill_states": value["skill_states"], "skills_assessed": value["x"] is not None}
    return result

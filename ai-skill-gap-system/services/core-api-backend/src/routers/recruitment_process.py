"""Internal applicant workflow. Sending messages never advances these stages."""
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy.orm import Session
from src.database import get_db
from src.core.security import require_role
from src.models.user import User
from src.models.job import JobApplication
from src.models.recruitment_process import ApplicationProcess, ApplicationProcessEvent
from src.routers.quick_hire import contact_fields, contact_history, owned_job
from src.routers.application_evidence import owned_application
from src.models.evidence import AnalysisRun, ApplicationEvidence
from src.services.evidence_matcher import digest, keyword_match, requirements_for, requirements_hash
from src.services.filter_counts import calculate, contact_states

router = APIRouter()
allowed = require_role(["employer", "admin"])
STAGES = [
    {"id": "new", "label": "Mới nhận"},
    {"id": "screening", "label": "Sàng lọc"},
    {"id": "interviewing", "label": "Đang phỏng vấn"},
    {"id": "offer", "label": "Đề nghị nhận việc"},
    {"id": "hired", "label": "Đã nhận việc"},
    {"id": "rejected", "label": "Không tiếp tục"},
]
Stage = Literal["new", "screening", "interviewing", "offer", "hired", "rejected"]
LEGACY_INTERVIEW_STAGES = {"interview_1", "interview_2"}


class ProcessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=0)
    stage: Stage | None = None
    reason: str = Field(min_length=5, max_length=2000)

    @field_validator("reason")
    @classmethod
    def reason_valid(cls, value):
        if len(value.strip()) < 5: raise ValueError("Hãy ghi lý do có ít nhất 5 ký tự")
        return value.strip()


class NoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    note: str = Field(min_length=1, max_length=2000)

    @field_validator("note")
    @classmethod
    def note_not_blank(cls, value):
        if not value.strip(): raise ValueError("Ghi chú không được rỗng")
        return value.strip()


def state_data(process):
    stage = process.stage if process else "new"
    if stage in LEGACY_INTERVIEW_STAGES:
        stage = "interviewing"
    return {"stage": stage, "version": process.version if process else 0, "updated_at": process.updated_at if process else None}


def detail_data(db, application, job, user):
    process = db.get(ApplicationProcess, application.id)
    query = db.query(ApplicationProcessEvent).filter_by(application_id=application.id)
    total = query.count()
    events = query.order_by(ApplicationProcessEvent.id.desc()).limit(200).all()[::-1]
    return {"application_id": application.id, "job_id": job.id, **state_data(process), "stages": STAGES,
            "applied_at": application.applied_at, "event_count": total,
            "events": [{key: getattr(e, key) for key in ("id", "actor_id", "actor_name", "event_type", "details", "reason", "created_at")} for e in events]}


@router.get("/jobs/{job_id}/pipeline")
def pipeline(
    job_id: int,
    priority_skills: list[str] | None = Query(None, max_length=12),
    db: Session = Depends(get_db),
    user: User = Depends(allowed),
):
    job = owned_job(db, job_id, user)
    priorities = {}
    for value in priority_skills or []:
        label = " ".join(value.split())
        if not label or len(label) > 100:
            raise HTTPException(422, "Tên kỹ năng phải có từ 1 đến 100 ký tự")
        priorities.setdefault(label.casefold(), label)
    pairs = db.query(JobApplication, User).join(User, JobApplication.candidate_id == User.id).filter(JobApplication.job_id == job_id).order_by(JobApplication.id.desc()).all()
    processes = {p.application_id: p for p in db.query(ApplicationProcess).join(JobApplication, JobApplication.id == ApplicationProcess.application_id).filter(JobApplication.job_id == job_id).all()}
    skills = application_skills(db, job_id, [a for a, _ in pairs], priorities)
    history = contact_history(db, job_id)
    applications = [{"id": a.id, "candidate_name": u.full_name, "candidate_email": u.email,
                     "applied_at": a.applied_at, "communication_status": a.status,
                     "is_demo": u.email.lower().endswith(("@demo.local", ".demo.local")),
                     "contact_states": contact_states(contact_fields(a, history.get(a.id))),
                     **state_data(processes.get(a.id)), **skills[a.id]} for a, u in pairs]
    return {"job_id": job_id, "industry": job.industry, "stages": STAGES, "applications": applications,
            "counts": {s["id"]: sum(a["stage"] == s["id"] for a in applications) for s in STAGES},
            "managed_by": {"id": job.employer_id or user.id}}


def application_skills(db, job_id, applications, priorities):
    """Read job evidence and match extra priorities without using the quick-hire profile."""
    labels = requirements_for(db, job_id)
    items = [{"label": name, "kind": "skill", "level": "nice"} for name in labels]
    ids = [a.id for a in applications]
    runs = db.query(AnalysisRun).filter(AnalysisRun.application_id.in_(ids))
    runs = runs.filter_by(filter_profile_hash=None, requirements_hash=requirements_hash(labels))
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
        states = value["skill_states"]
        if priorities:
            saved = {skill["label"].casefold(): skill for skill in states}
            cv = " ".join((application.cv_snapshot_text or "").split())
            readable = len(cv.replace(" ", "")) >= 40
            selected = []
            for key, label in priorities.items():
                existing = saved.get(key)
                if existing and existing["result"] != "unassessed":
                    selected.append({**existing, "label": label})
                    continue
                match = readable and keyword_match(cv, label)
                state = ("supported" if match else "not_found") if readable else "unreadable"
                selected.append({"label": label, "result": state, "source": "keyword"})
            states = selected + [skill for skill in states if skill["label"].casefold() not in priorities]
        result[application.id] = {"skill_states": states, "skills_assessed": value["x"] is not None}
    return result


@router.get("/applications/{application_id}/process")
def get_process(application_id: int, db: Session = Depends(get_db), user: User = Depends(allowed)):
    application, job = owned_application(db, application_id, user)
    return detail_data(db, application, job, user)


@router.patch("/applications/{application_id}/process")
def update_process(application_id: int, payload: ProcessRequest, db: Session = Depends(get_db), user: User = Depends(allowed)):
    application, job = owned_application(db, application_id, user)
    # Lock the application even when no process row exists yet.
    db.query(JobApplication).filter_by(id=application_id).populate_existing().with_for_update().one()
    process = db.query(ApplicationProcess).filter_by(application_id=application_id).populate_existing().first()
    previous = state_data(process)
    if previous["version"] != payload.expected_version:
        raise HTTPException(409, "Tiến trình đã được cập nhật ở nơi khác. Tải lại trước khi lưu.")
    stage = payload.stage if payload.stage is not None else previous["stage"]
    details = {}
    if stage != previous["stage"]: details["stage"] = {"from": previous["stage"], "to": stage}
    if not details: raise HTTPException(422, "Chưa có thay đổi về trạng thái")
    if process is None:
        process = ApplicationProcess(application_id=application_id)
        db.add(process)
    process.stage = stage
    process.version = previous["version"] + 1
    process.updated_at = datetime.utcnow()
    db.add(ApplicationProcessEvent(application_id=application_id, actor_id=user.id,
        actor_name=user.full_name or user.email, event_type="process_updated", details=details, reason=payload.reason))
    db.commit()
    return detail_data(db, application, job, user)


@router.post("/applications/{application_id}/process/notes", status_code=201)
def add_note(application_id: int, payload: NoteRequest, db: Session = Depends(get_db), user: User = Depends(allowed)):
    application, job = owned_application(db, application_id, user)
    db.add(ApplicationProcessEvent(application_id=application_id, actor_id=user.id,
        actor_name=user.full_name or user.email, event_type="note", details={}, reason=payload.note))
    db.commit()
    return detail_data(db, application, job, user)

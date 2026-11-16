import json
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.security import require_role
from src.database import get_db
from src.models.job import JobApplication, JobPosting
from src.models.user import User
from src.models.evidence import AnalysisRun, ApplicationEvidence
from src.services import evidence_matcher as matcher

router = APIRouter()
allowed_user = require_role(["employer", "admin"])


def owned_application(db, application_id, user):
    application = db.get(JobApplication, application_id)
    if not application:
        raise HTTPException(404, "Không tìm thấy hồ sơ ứng tuyển")
    job = db.get(JobPosting, application.job_id)
    if not job or (user.role != "admin" and job.employer_id != user.id):
        raise HTTPException(403, "Bạn không có quyền xem hồ sơ này")
    return application, job


def current_requirements(db, run, job):
    if run.filter_profile_hash:
        from src.models.quick_hire import FilterProfile
        profile = db.query(FilterProfile).filter_by(job_id=job.id).first()
        return ([item["label"] for item in profile.items] if profile else [],
                not profile or profile.profile_hash != run.filter_profile_hash)
    return matcher.requirements_for(db, job.id), False


@router.get("/applications/{application_id}/original-cv")
def original_cv(application_id: int, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    application, _ = owned_application(db, application_id, user)
    if application.cv_original_text is None and application.cv_original_blob is None:
        raise HTTPException(404, "Hồ sơ cũ chưa lưu tệp CV gốc; chỉ có bản chụp nội dung đã nộp")
    candidate = db.get(User, application.candidate_id)
    import hashlib
    content = application.cv_original_blob if application.cv_original_blob is not None else (application.cv_original_text or "").encode("utf-8")
    return {"filename": application.cv_original_filename or "CV.txt", "content": application.cv_original_text if not application.cv_original_blob else None,
            "is_demo": bool(candidate and candidate.email.lower().endswith(("@demo.local", ".demo.local"))),
            "content_type": application.cv_original_mime or "text/plain; charset=utf-8", "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content), "file_url": f"/applications/{application_id}/original-cv/file"}


@router.get("/applications/{application_id}/original-cv/file")
def original_cv_file(application_id: int, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    application, _ = owned_application(db, application_id, user)
    if application.cv_original_blob is None and application.cv_original_text is None: raise HTTPException(404, "Chưa có CV gốc")
    content = application.cv_original_blob if application.cv_original_blob is not None else application.cv_original_text.encode("utf-8")
    from urllib.parse import quote
    return Response(content=content, media_type=application.cv_original_mime or "text/plain; charset=utf-8",
                    headers={"Content-Disposition": "inline; filename*=UTF-8''" + quote(application.cv_original_filename or "CV.txt", safe=""),
                             "X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"})


@router.put("/applications/{application_id}/original-cv")
async def upload_original_cv(application_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    application, _ = owned_application(db, application_id, user)
    from src.services.cv_original import MAX_BYTES, validate_extract
    from starlette.concurrency import run_in_threadpool
    content = await file.read(MAX_BYTES + 1)
    await file.close()
    filename, mime, text = await run_in_threadpool(validate_extract, file.filename, content)
    application.cv_original_filename, application.cv_original_mime = filename, mime
    application.cv_original_blob = content
    application.cv_original_text = text if mime == "text/plain" else None
    application.cv_snapshot_text = text
    db.commit()
    return {"filename": filename, "content_type": mime, "size": len(content),
            "extraction_status": "ready" if len("".join(text.split())) >= 40 else "unreadable"}


def serialize_run(db, run, application, job):
    current, profile_stale = current_requirements(db, run, job)
    candidate = db.get(User, application.candidate_id)
    data = {key: getattr(run, key) for key in ("id", "application_id", "requirements_hash", "cv_hash", "provider", "status", "error_code", "created_at")}
    data.update(requirements_snapshot=json.loads(run.requirements_snapshot),
                filter_profile_hash=run.filter_profile_hash,
                stale=profile_stale or matcher.requirements_hash(current) != run.requirements_hash,
                cv_stale=matcher.digest(application.cv_snapshot_text or "") != run.cv_hash,
                is_demo=bool(candidate and candidate.email.lower().endswith(("@demo.local", ".demo.local"))),
                cv_text=application.cv_snapshot_text or "", evidence=[])
    for row in db.query(ApplicationEvidence).filter(ApplicationEvidence.run_id == run.id).order_by(ApplicationEvidence.id).all():
        item = {key: getattr(row, key) for key in ("id", "requirement_name", "result", "quote", "source_start", "source_end", "ai_result_original", "reviewer_id", "review_result", "review_reason", "reviewed_at")}
        reviewer = db.get(User, row.reviewer_id) if row.reviewer_id else None
        item["reviewer_name"] = reviewer.full_name if reviewer else None
        data["evidence"].append(item)
    return data


def persist_analysis(db, application, requirements, profile_hash=None):
    cv = application.cv_snapshot_text or ""
    result = matcher.analyse(cv, requirements)
    run = AnalysisRun(application_id=application.id, requirements_hash=matcher.requirements_hash(requirements),
        filter_profile_hash=profile_hash,
        requirements_snapshot=json.dumps(requirements, ensure_ascii=False), cv_hash=matcher.digest(cv),
        provider=result["provider"], status=result["status"], error_code=result["error_code"])
    db.add(run)
    db.flush()
    for row in result["rows"]:
        db.add(ApplicationEvidence(run_id=run.id, **row))
    return run


@router.post("/applications/{application_id}/analyses", status_code=201)
def create_analysis(application_id: int, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    application, job = owned_application(db, application_id, user)
    run = persist_analysis(db, application, matcher.requirements_for(db, job.id))
    db.commit()
    db.refresh(run)
    return serialize_run(db, run, application, job)


@router.get("/applications/{application_id}/evidence")
def latest_evidence(application_id: int, profile_hash: str | None = Query(None, max_length=64), db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    application, job = owned_application(db, application_id, user)
    run = db.query(AnalysisRun).filter(AnalysisRun.application_id == application_id, AnalysisRun.filter_profile_hash == profile_hash).order_by(AnalysisRun.id.desc()).first()
    if not run:
        candidate = db.get(User, application.candidate_id)
        return {"run": None, "stale": False, "evidence": [], "cv_text": application.cv_snapshot_text or "",
                "is_demo": bool(candidate and candidate.email.lower().endswith(("@demo.local", ".demo.local")))}
    return serialize_run(db, run, application, job)


class ReviewRequest(BaseModel):
    review_result: Literal["supported", "not_found", "unreadable", "needs_review"]
    review_reason: str = Field(default="", max_length=4000)


@router.patch("/evidence/{evidence_id}/review")
def review_evidence(evidence_id: int, payload: ReviewRequest, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    row = db.get(ApplicationEvidence, evidence_id)
    if not row:
        raise HTTPException(404, "Không tìm thấy dẫn chứng")
    run = db.get(AnalysisRun, row.run_id)
    application, job = owned_application(db, run.application_id, user)
    # Serialize review edits with quick-hire, profile saves and undo for this job.
    db.query(JobPosting).filter_by(id=job.id).with_for_update().first()
    db.refresh(row)
    current, profile_stale = current_requirements(db, run, job)
    if profile_stale or run.requirements_hash != matcher.requirements_hash(current) or run.cv_hash != matcher.digest(application.cv_snapshot_text or ""):
        raise HTTPException(409, "Dữ liệu đã thay đổi. Hãy chạy đối chiếu lại trước khi xác nhận.")
    reason = payload.review_reason.strip()
    if payload.review_result != row.result and not reason:
        raise HTTPException(422, "Bắt buộc ghi lý do khi sửa nhận định")
    row.review_result = payload.review_result
    row.review_reason = reason
    row.reviewer_id = user.id
    row.reviewed_at = datetime.utcnow()
    db.commit()
    return serialize_run(db, run, application, job)

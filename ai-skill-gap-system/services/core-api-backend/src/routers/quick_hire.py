"""Employer CV item filters. Historical internal-selection routes are retired."""
import json
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, StrictInt, field_validator, ConfigDict
from sqlalchemy.orm import Session
from src.core.security import require_role
from src.database import get_db
from src.models.job import JobPosting, JobApplication
from src.models.user import User
from src.models.evidence import AnalysisRun, ApplicationEvidence
from src.models.quick_hire import FilterProfile
from src.models.notification import NotificationRecipient
from src.services.evidence_matcher import digest, requirements_for
from src.services.filter_counts import calculate, select_results
from src.routers.application_evidence import persist_analysis

router = APIRouter()
allowed_user = require_role(["employer", "admin"])

class FilterItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=100)
    kind: Literal["skill", "criterion"] = "skill"
    level: Literal["must", "nice"] = "nice"
    @field_validator("label")
    @classmethod
    def clean(cls, value):
        if not value.strip(): raise ValueError("Nội dung mục không được rỗng")
        return value.strip()

class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="Bộ lọc tuyển dụng", min_length=1, max_length=150)
    items: list[FilterItem] = Field(min_length=1, max_length=30)
    @field_validator("items")
    @classmethod
    def unique(cls, items):
        if len({i.label.casefold() for i in items}) != len(items): raise ValueError("Không được trùng tên mục")
        return items
    @field_validator("name")
    @classmethod
    def clean(cls, value):
        if not value.strip(): raise ValueError("Tên không được rỗng")
        return value.strip()

class EvaluationRequest(BaseModel):
    application_ids: list[StrictInt] | None = Field(default=None,max_length=50)

def owned_job(db,job_id,user,lock=False):
    query=db.query(JobPosting).filter_by(id=job_id)
    job=(query.populate_existing().with_for_update() if lock else query).first()
    if not job: raise HTTPException(404,"Không tìm thấy tin tuyển dụng")
    if user.role != "admin" and job.employer_id != user.id: raise HTTPException(403,"Bạn không có quyền với tin tuyển dụng này")
    return job

def saved_profile(db,job_id,lock=False):
    query=db.query(FilterProfile).filter_by(job_id=job_id)
    profile=(query.populate_existing().with_for_update() if lock else query).first()
    if not profile: raise HTTPException(409,"Hãy lưu bộ lọc trước")
    return profile

def profile_data(profile):
    return {"id":profile.id,"job_id":profile.job_id,"name":profile.name,"items":profile.items,
            "profile_hash":profile.profile_hash,"updated_at":profile.updated_at,"saved":True}

def latest_run(db,application,profile,lock=False):
    query=db.query(AnalysisRun).filter_by(application_id=application.id,filter_profile_hash=profile.profile_hash).order_by(AnalysisRun.id.desc())
    return (query.populate_existing().with_for_update() if lock else query).first()

def application_result(db,application,profile,lock=False):
    run=latest_run(db,application,profile,lock)
    query=db.query(ApplicationEvidence).filter_by(run_id=run.id).order_by(ApplicationEvidence.id) if run else None
    rows=(query.populate_existing().with_for_update() if lock else query).all() if query is not None else []
    evidence=[{k:getattr(row,k) for k in ("requirement_name","result","review_result")} for row in rows]
    cv_hash=digest(application.cv_snapshot_text or "")
    fresh=bool(run and run.cv_hash==cv_hash)
    value=calculate(profile.items,evidence,run.status if fresh else None)
    candidate=db.get(User,application.candidate_id)
    delivery=db.query(NotificationRecipient).filter_by(application_id=application.id).order_by(NotificationRecipient.updated_at.desc(),NotificationRecipient.id.desc()).first()
    return {**value,"application_id":application.id,"candidate_name":candidate.full_name if candidate else "",
            "candidate_email":candidate.email if candidate else "","is_demo":bool(candidate and (candidate.email.lower().endswith("@demo.local") or candidate.email.lower().endswith(".demo.local"))),
            "status":application.status,"applied_at":application.applied_at,"run_id":run.id if run else None,
            "provider":run.provider if run else None,"error_code":run.error_code if run else None,
            "evaluation_fingerprint":digest(json.dumps({"run":run.id if run else None,"cv":cv_hash,"rows":evidence,"state":run.status if run else None},sort_keys=True)),
            "needs_evaluation":not fresh or (run is not None and run.status=="error"),
            "last_delivery":({"status":delivery.status,"channel":delivery.channel,"last_error":delivery.last_error,"batch_id":delivery.batch_id} if delivery else None)}

def all_results(db,job_id,profile,lock=False):
    query=db.query(JobApplication).filter_by(job_id=job_id)
    applications=(query.populate_existing().with_for_update() if lock else query).all()
    return [application_result(db,a,profile,lock) for a in applications]

@router.get("/jobs/{job_id}/filter-profile")
def get_profile(job_id:int,db:Session=Depends(get_db),user:User=Depends(allowed_user)):
    owned_job(db,job_id,user)
    profile=db.query(FilterProfile).filter_by(job_id=job_id).first()
    return profile_data(profile) if profile else {"saved":False,"name":"Bộ lọc tuyển dụng","profile_hash":None,
        "items":[{"label":name,"kind":"skill","level":"nice"} for name in requirements_for(db,job_id)]}

@router.put("/jobs/{job_id}/filter-profile")
@router.post("/jobs/{job_id}/filter-profile/apply")
def put_profile(job_id:int,payload:ProfileRequest,db:Session=Depends(get_db),user:User=Depends(allowed_user)):
    job=owned_job(db,job_id,user,True)
    profile=db.query(FilterProfile).filter_by(job_id=job_id).populate_existing().with_for_update().first()
    if not profile:
        profile=FilterProfile(job_id=job_id,owner_user_id=job.employer_id or user.id)
        db.add(profile)
    data=payload.model_dump()
    profile.name=data["name"];profile.items=data["items"]
    profile.profile_hash=digest(json.dumps(data,ensure_ascii=False,sort_keys=True));profile.updated_at=datetime.utcnow()
    db.commit()
    return profile_data(profile)

@router.post("/jobs/{job_id}/filter-profile/evaluate")
def evaluate(job_id: int, payload: EvaluationRequest = EvaluationRequest(), db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    owned_job(db, job_id, user, lock=True)
    profile = saved_profile(db, job_id, lock=True)
    items = profile.items
    applications = db.query(JobApplication).filter_by(job_id=job_id).order_by(JobApplication.applied_at, JobApplication.id).all()
    by_id = {application.id: application for application in applications}
    requested = list(dict.fromkeys(payload.application_ids)) if payload.application_ids is not None else [a.id for a in applications if application_result(db, a, profile)["needs_evaluation"]][:50]
    results = []
    for application_id in requested:
        application = by_id.get(application_id)
        if not application:
            results.append({"application_id": application_id, "status": "error", "error_code": "NOT_IN_JOB"})
            continue
        current = application_result(db, application, profile)
        if not current["needs_evaluation"]:
            results.append({"application_id": application_id, "status": "cached", "run_id": current["run_id"]})
            continue
        try:
            with db.begin_nested():
                run = persist_analysis(db, application, [item["label"] for item in items], profile.profile_hash)
                db.flush()
            results.append({"application_id": application_id, "status": run.status, "error_code": run.error_code, "run_id": run.id})
        except Exception:
            results.append({"application_id": application_id, "status": "error", "error_code": "EVALUATION_ERROR"})
    db.commit()
    return {"profile_hash": profile.profile_hash, "processed": len(results), "total_requested": len(requested),
            "results": results, "remaining": sum(bool(application_result(db, a, profile)["needs_evaluation"]) for a in applications)}



@router.get("/jobs/{job_id}/filter-results")
def get_results(job_id:int,xs:list[int]|None=Query(None),min_x:int|None=Query(None,ge=0),
                missing_must:bool=False,unassessed:bool=False,page:int=Query(1,ge=1),
                priority_skills:list[str]|None=Query(None),
                db:Session=Depends(get_db),user:User=Depends(allowed_user)):
    owned_job(db,job_id,user)
    profile=saved_profile(db,job_id)
    values=all_results(db,job_id,profile)
    y=len(profile.items)
    if any(x<0 or x>y for x in (xs or [])) or (min_x is not None and min_x>y): raise HTTPException(422,"Số mục đạt nằm ngoài bộ lọc")
    if len(priority_skills or []) > 30 or any(label not in {item["label"] for item in profile.items} for label in (priority_skills or [])):
        raise HTTPException(422,"Kỹ năng ưu tiên phải thuộc các kỹ năng đã dùng để lọc")
    filtered=select_results(values,xs,min_x,missing_must,unassessed,priority_skills)
    return {"profile":profile_data(profile),"y":y,"items":profile.items,
            "counts_by_x":{str(x):sum(r["x"]==x for r in values) for x in range(y+1)},
            "unassessed_count":sum(r["x"] is None for r in values),
            "missing_must_count":sum(bool(r["missing_must"]) for r in values),
            "pending_count":sum(bool(r["needs_evaluation"]) for r in values),
            "pending_ids":[r["application_id"] for r in values if r["needs_evaluation"]],
            "total":len(filtered),"page":page,"page_size":10,"applications":filtered[(page-1)*10:page*10],
            "matching_ids":[r["application_id"] for r in filtered]}

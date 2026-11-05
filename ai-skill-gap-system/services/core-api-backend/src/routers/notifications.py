import json
from datetime import datetime, timedelta, timezone
from typing import Literal
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jose import jwt, JWTError
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.core.security import get_current_user, require_role, SECRET_KEY, ALGORITHM
from src.models.user import User
from src.models.job import JobApplication
from src.models.notification import NotificationBatch, NotificationRecipient, UserNotification, NotificationTemplate
from src.routers.quick_hire import owned_job, saved_profile, profile_data, all_results
from src.services.filter_counts import select_results
from src.services.evidence_matcher import digest
from src.services import notification_delivery as delivery

router = APIRouter()
allowed_user = require_role(["employer", "admin"])
worker_user = require_role(["worker", "candidate"])
PREVIEW_KEY = digest(SECRET_KEY + ":notification-preview")
DEFAULT_MESSAGES = {
    "acknowledge": {"title_template": "Xác nhận hồ sơ — {{job_title}}", "body_template": "Chào {{candidate_name}},\n{{company_name}} đã nhận hồ sơ của bạn cho vị trí {{job_title}}."},
    "invite": {"title_template": "Mời phỏng vấn — {{job_title}}", "body_template": "Chào {{candidate_name}},\n{{company_name}} mời bạn phỏng vấn vị trí {{job_title}}.\nThời gian: {{interview_time}}\nĐịa điểm/đường dẫn: {{interview_location}}\nLiên hệ phản hồi: {{reply_contact}}"},
}


class TemplateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    action_type: Literal["acknowledge", "invite"]
    title_template: str = Field(min_length=1, max_length=300)
    body_template: str = Field(min_length=1, max_length=6000)


def template_data(row):
    return {key: getattr(row, key) for key in ("id", "name", "action_type", "title_template", "body_template", "updated_at")}


@router.get("/notification-templates")
def list_templates(db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    return {"defaults": DEFAULT_MESSAGES, "templates": [template_data(row) for row in db.query(NotificationTemplate).filter_by(owner_id=user.id).order_by(NotificationTemplate.updated_at.desc(), NotificationTemplate.id.desc()).all()]}


@router.post("/notification-templates")
def save_template(payload: TemplateRequest, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    import re
    data = payload.model_dump()
    for field in ("name", "title_template", "body_template"):
        data[field] = data[field].strip()
        if not data[field]: raise HTTPException(422, "Tên mẫu, tiêu đề và nội dung không được rỗng")
    if "\n" in data["title_template"] or "\r" in data["title_template"]:
        raise HTTPException(422, "Tiêu đề chỉ được có một dòng")
    allowed = {"candidate_name", "job_title", "company_name", "interview_time", "interview_location", "reply_contact"}
    for field in ("title_template", "body_template"):
        for match in re.finditer(r"\{\{\s*(\w+)\s*\}\}", data[field]):
            if match.group(1) not in allowed: raise HTTPException(422, "Mẫu có biến cá nhân hóa không được hỗ trợ")
        remainder = re.sub(r"\{\{\s*(\w+)\s*\}\}", "", data[field])
        if "{{" in remainder or "}}" in remainder: raise HTTPException(422, "Cú pháp biến cá nhân hóa chưa hợp lệ")
    # Serialize writes per owner; a saved message is never sent by this endpoint.
    db.query(User).filter_by(id=user.id).with_for_update().first()
    row = db.query(NotificationTemplate).filter_by(owner_id=user.id, action_type=payload.action_type, name=data["name"]).first()
    if not row:
        if db.query(NotificationTemplate).filter_by(owner_id=user.id).count() >= 40:
            raise HTTPException(422, "Mỗi tài khoản được lưu tối đa 40 mẫu thông báo")
        row = NotificationTemplate(owner_id=user.id, **data)
        db.add(row)
    else:
        row.title_template, row.body_template = data["title_template"], data["body_template"]
        row.updated_at = datetime.utcnow()
    db.commit(); db.refresh(row)
    return template_data(row)


class Filters(BaseModel):
    xs: list[StrictInt] = Field(default_factory=list, max_length=31)
    min_x: int | None = Field(default=None, ge=0)
    missing_must: bool = False
    unassessed: bool = False
    priority_skills: list[str] = Field(default_factory=list, max_length=30)


class MessageFields(BaseModel):
    interview_time: str = Field(default="", max_length=300)
    interview_location: str = Field(default="", max_length=1000)
    reply_contact: str = Field(default="", max_length=300)


class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    application_ids: list[StrictInt] = Field(default_factory=list, max_length=100)
    all_matching: bool = False
    exclude_ids: list[StrictInt] = Field(default_factory=list, max_length=100)
    filters: Filters = Field(default_factory=Filters)
    profile_hash: str | None = Field(default=None, min_length=64, max_length=64)
    direct_application: bool = False
    action_type: Literal["acknowledge", "invite"]
    channels: list[Literal["in_app", "email"]] = Field(min_length=1, max_length=2)
    fields: MessageFields = Field(default_factory=MessageFields)
    title_template: str | None = Field(default=None, max_length=300)
    body_template: str | None = Field(default=None, max_length=6000)


class BatchRequest(PreviewRequest):
    expected_x: dict[str, StrictInt | None]
    preview_token: str = Field(min_length=1, max_length=600000)
    idempotency_key: str = Field(min_length=8, max_length=100)


class RetryRequest(BaseModel):
    include_unknown: bool = False


def content_data(payload):
    return {key: getattr(payload, key) if key != "fields" else payload.fields.model_dump()
            for key in ("action_type", "channels", "fields", "title_template", "body_template", "direct_application")}


def render_message(job, row, payload):
    import re
    if payload.action_type == "invite" and not all(value.strip() for value in payload.fields.model_dump().values()):
        raise HTTPException(422, "Mời phỏng vấn cần thời gian, địa điểm/đường dẫn và liên hệ phản hồi")
    values = {"candidate_name": row["candidate_name"], "job_title": job.title, "company_name": job.company,
              **payload.fields.model_dump()}
    if payload.title_template is not None and not payload.title_template.strip(): raise HTTPException(422, "Tiêu đề không được rỗng")
    if payload.body_template is not None and not payload.body_template.strip(): raise HTTPException(422, "Nội dung không được rỗng")
    title = payload.title_template if payload.title_template is not None else DEFAULT_MESSAGES[payload.action_type]["title_template"]
    body = payload.body_template if payload.body_template is not None else DEFAULT_MESSAGES[payload.action_type]["body_template"]
    def replace(match):
        value = values.get(match.group(1))
        if not value:
            raise HTTPException(422, "Còn biến chưa được thay hoặc thiếu thông tin cá nhân hóa")
        return str(value)
    title, body = [re.sub(r"\{\{\s*(\w+)\s*\}\}", replace, text) for text in (title, body)]
    if any(marker in title + body for marker in ("{{", "}}")) or "\r" in title or "\n" in title:
        raise HTTPException(422, "Nội dung còn biến chưa thay hoặc tiêu đề không hợp lệ")
    if len(title) > 300:
        if payload.title_template:
            raise HTTPException(422, "Tiêu đề sau cá nhân hóa vượt 300 ký tự")
        title = title[:299] + "…"
    if len(body.encode("utf-8")) > 60000:
        raise HTTPException(422, "Nội dung thông báo quá dài")
    return title, body


def prepare(db, job, payload, lock=False):
    if payload.direct_application:
        from types import SimpleNamespace
        if payload.all_matching or len(payload.application_ids) != 1 or payload.exclude_ids:
            raise HTTPException(422, "Tuyển dụng trực tiếp chỉ áp dụng cho một hồ sơ đang xem")
        profile = SimpleNamespace(id=None, job_id=job.id, name="Liên hệ trực tiếp ứng viên", items=[],
                                  profile_hash=digest(f"direct-notification:{job.id}"), updated_at=None)
    else:
        profile = saved_profile(db, job.id, lock)
    if payload.profile_hash != profile.profile_hash and not (payload.direct_application and payload.profile_hash is None):
        raise HTTPException(409, "Bộ lọc đã thay đổi. Hãy xem trước lại.")
    if "email" in payload.channels and not delivery.smtp_enabled():
        raise HTTPException(422, "Chưa cấu hình SMTP")
    values = all_results(db, job.id, profile, lock)
    lookup = {row["application_id"]: row for row in values}
    if payload.all_matching:
        if any(label not in {item["label"] for item in profile.items} for label in payload.filters.priority_skills):
            raise HTTPException(422, "Kỹ năng ưu tiên phải thuộc các kỹ năng đã dùng để lọc")
        if any(x < 0 or x > len(profile.items) for x in payload.filters.xs) or (payload.filters.min_x is not None and payload.filters.min_x > len(profile.items)):
            raise HTTPException(422, "Số mục đạt nằm ngoài bộ lọc")
        chosen = select_results(values, payload.filters.xs, payload.filters.min_x, payload.filters.missing_must, payload.filters.unassessed, payload.filters.priority_skills)
        ids = [row["application_id"] for row in chosen if row["application_id"] not in payload.exclude_ids]
    else:
        ids = list(dict.fromkeys(payload.application_ids))
    if not ids or len(ids) > 100:
        raise HTTPException(422, "Mỗi lượt gửi cần chọn từ 1 đến 100 hồ sơ; hãy thu hẹp bộ lọc hoặc chia thành nhiều đợt")
    if any(application_id not in lookup for application_id in ids):
        raise HTTPException(400, "Danh sách có hồ sơ không thuộc tin tuyển dụng")
    prepared = []
    for application_id in ids:
        row = lookup[application_id]
        application = db.get(JobApplication, application_id)
        candidate = db.get(User, application.candidate_id)
        title, body = render_message(job, row, payload)
        active = bool(candidate and candidate.is_active and not candidate.is_deleted)
        duplicate = db.query(NotificationRecipient).join(NotificationBatch).filter(
            NotificationRecipient.application_id == application_id, NotificationBatch.action_type == payload.action_type,
            NotificationRecipient.status.in_(["sent", "read", "unknown", "queued", "sending"])).count() > 0
        signature = digest(json.dumps([row["evaluation_fingerprint"], row["x"], row["y"], title, body,
                                      candidate.email if candidate else None, application.candidate_id, active, duplicate]))
        prepared.append({"application_id": application_id, "candidate_name": row["candidate_name"], "is_demo": row["is_demo"],
            "x": row["x"], "y": row["y"], "missing_must": row["missing_must"], "counts": row["counts"],
            "title": title, "body": body, "address": candidate.email if candidate else None,
            "user_id": candidate.id if active else None, "missing_in_app": not active,
            "missing_email": not delivery.valid_email(candidate.email if candidate else None),
            "already_notified": duplicate, "signature": signature})
    return profile, prepared


def serialize_batch(db, batch, detailed=True):
    recipients = db.query(NotificationRecipient).filter_by(batch_id=batch.id).order_by(NotificationRecipient.id).all()
    counts = {state: sum(row.status == state for row in recipients) for state in ("queued", "sending", "sent", "read", "failed", "unknown", "missing_contact")}
    data = {"id": batch.id, "job_id": batch.job_id, "action_type": batch.action_type, "channels": batch.channels,
            "status": batch.status, "created_at": batch.created_at, "simulated": batch.simulated, "counts": counts,
            "total": len(recipients), "application_count": len({row.application_id for row in recipients}),
            "processed": sum(counts[s] for s in delivery.TERMINAL)}
    if detailed:
        data["recipients"] = [{key: getattr(row, key) for key in ("id", "application_id", "candidate_name", "channel", "status", "attempt_count", "last_error", "error_kind", "retryable", "updated_at", "title", "body")} for row in recipients]
    return data


@router.get("/notifications/capabilities")
def capabilities(user: User = Depends(allowed_user)):
    return {"email_enabled": delivery.smtp_enabled(), "in_app_enabled": True, "simulated": delivery.simulated()}


@router.post("/jobs/{job_id}/notification-batches/preview")
def preview(job_id: int, payload: PreviewRequest, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    job = owned_job(db, job_id, user)
    profile, rows = prepare(db, job, payload)
    content_hash = digest(json.dumps(content_data(payload), sort_keys=True, ensure_ascii=False))
    token = jwt.encode({"purpose": "notification-preview", "sub": str(user.id), "job_id": job.id,
                       "profile_hash": profile.profile_hash, "content_hash": content_hash,
                       "rows": {str(row["application_id"]): row["signature"] for row in rows},
                       "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}, PREVIEW_KEY, algorithm=ALGORITHM)
    return {"profile": profile_data(profile), "applications": rows, "preview_token": token,
            "simulated": delivery.simulated(), "warnings": {
                "missing_contact": sum((row["missing_in_app"] and "in_app" in payload.channels) or (row["missing_email"] and "email" in payload.channels) for row in rows),
                "already_notified": sum(row["already_notified"] for row in rows)}}


@router.post("/jobs/{job_id}/notification-batches", status_code=202)
def create_batch(job_id: int, payload: BatchRequest, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    job = owned_job(db, job_id, user, True)
    if payload.all_matching:
        raise HTTPException(422, "Xác nhận phải dùng danh sách id cụ thể của bản xem trước")
    request_hash = digest(json.dumps([job_id, payload.profile_hash, sorted(set(payload.application_ids)), payload.expected_x, content_data(payload)], sort_keys=True, ensure_ascii=False))
    existing = db.query(NotificationBatch).filter_by(idempotency_key=payload.idempotency_key).first()
    if existing:
        if existing.actor_id != user.id or existing.request_hash != request_hash:
            raise HTTPException(409, "Mã chống gửi lặp đã dùng cho yêu cầu khác")
        return serialize_batch(db, existing)
    try:
        claims = jwt.decode(payload.preview_token, PREVIEW_KEY, algorithms=[ALGORITHM])
        if claims.get("purpose") != "notification-preview" or claims.get("sub") != str(user.id) or claims.get("job_id") != job_id or claims.get("profile_hash") != payload.profile_hash:
            raise ValueError()
    except (JWTError, ValueError):
        raise HTTPException(409, "Bản xem trước không hợp lệ hoặc hết hạn")
    profile, rows = prepare(db, job, payload, True)
    content_hash = digest(json.dumps(content_data(payload), sort_keys=True, ensure_ascii=False))
    if content_hash != claims.get("content_hash"):
        raise HTTPException(409, "Nội dung đã thay đổi. Hãy xem trước lại.")
    changed = [row["application_id"] for row in rows if payload.expected_x.get(str(row["application_id"]), "absent") != row["x"]
               or claims.get("rows", {}).get(str(row["application_id"])) != row["signature"]]
    if changed:
        raise HTTPException(409, {"message": "Số mục đạt hoặc dữ liệu hồ sơ đã đổi sau xem trước. Chưa gửi; hãy xem trước lại.", "changed_application_ids": changed})
    batch = NotificationBatch(job_id=job.id, actor_id=user.id, action_type=payload.action_type, channels=list(dict.fromkeys(payload.channels)),
        content={"message": content_data(payload), "profile": {k: v for k, v in profile_data(profile).items() if k != "updated_at"},
                 "selection": {str(row["application_id"]): {"x": row["x"], "y": row["y"]} for row in rows}},
        status="processing", idempotency_key=payload.idempotency_key, request_hash=request_hash, simulated=delivery.simulated())
    db.add(batch)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.query(NotificationBatch).filter_by(idempotency_key=payload.idempotency_key).first()
        if not existing or existing.actor_id != user.id or existing.request_hash != request_hash:
            raise HTTPException(409, "Mã chống gửi lặp đã dùng")
        return serialize_batch(db, existing)
    for row in rows:
        for channel in batch.channels:
            missing = row["missing_in_app"] if channel == "in_app" else row["missing_email"]
            db.add(NotificationRecipient(batch_id=batch.id, application_id=row["application_id"], channel=channel,
                user_id=row["user_id"], address=row["address"], candidate_name=row["candidate_name"], title=row["title"], body=row["body"],
                status="missing_contact" if missing else "queued", last_error="Thiếu thông tin liên hệ" if missing else None,
                error_kind="input" if missing else None, retryable=False))
    db.commit()
    result = serialize_batch(db, batch)
    background.add_task(delivery.process_batch, batch.id)
    return result


@router.get("/notification-batches/{batch_id}")
def get_batch(batch_id: int, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    batch = db.get(NotificationBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Không tìm thấy lượt gửi")
    owned_job(db, batch.job_id, user)
    return serialize_batch(db, batch)


@router.get("/jobs/{job_id}/notification-batches")
def history(job_id: int, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    owned_job(db, job_id, user)
    return {"batches": [serialize_batch(db, batch, False) for batch in db.query(NotificationBatch).filter_by(job_id=job_id).order_by(NotificationBatch.id.desc()).limit(50)]}


@router.post("/notification-batches/{batch_id}/retry", status_code=202)
def retry(batch_id: int, payload: RetryRequest, background: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(allowed_user)):
    batch = db.get(NotificationBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Không tìm thấy lượt gửi")
    owned_job(db, batch.job_id, user, True)
    db.refresh(batch)
    if batch.status == "processing":
        raise HTTPException(409, "Lượt gửi đang xử lý. Hãy chờ xong trước khi thử lại.")
    targets = db.query(NotificationRecipient).filter_by(batch_id=batch.id).populate_existing().with_for_update().all()
    for row in targets:
        if (row.status == "failed" and row.retryable) or (row.status == "unknown" and payload.include_unknown):
            row.status, row.last_error = "queued", None
    db.flush()
    delivery.finalize(db, batch)
    db.commit()
    result = serialize_batch(db, batch)
    background.add_task(delivery.process_batch, batch.id)
    return result


@router.get("/me/notifications")
def worker_notifications(db: Session = Depends(get_db), user: User = Depends(worker_user)):
    rows = db.query(UserNotification).filter_by(user_id=user.id).order_by(UserNotification.id.desc()).limit(100).all()
    return {"notifications": [{key: getattr(row, key) for key in ("id", "title", "body", "created_at", "read_at", "simulated")} for row in rows],
            "unread_count": db.query(UserNotification).filter_by(user_id=user.id, read_at=None).count()}


@router.post("/me/notifications/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(worker_user)):
    row = db.query(UserNotification).filter_by(id=notification_id, user_id=user.id).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy thông báo")
    if row.read_at is None:
        row.read_at = datetime.utcnow()
        recipient = db.get(NotificationRecipient, row.recipient_id)
        if recipient and recipient.status == "sent":
            recipient.status = "read"
        db.commit()
    return {"id": row.id, "read_at": row.read_at}

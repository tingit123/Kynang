from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from src.database import get_db
from src.core.security import require_role
from src.models.user import User
from src.models.notification import Notification

router = APIRouter()


class NotificationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10000)

    @field_validator('title', 'content')
    @classmethod
    def require_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Tiêu đề và nội dung không được để trống')
        return value


class NotificationOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    model_config = {'from_attributes': True}

    @field_validator('created_at')
    @classmethod
    def utc_timestamp(cls, value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class NotificationList(BaseModel):
    items: list[NotificationOut]
    total: int
    limit: int
    offset: int


@router.get('/', response_model=NotificationList)
def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    return NotificationList(items=query.order_by(Notification.id.desc()).offset(offset).limit(limit).all(), total=query.count(), limit=limit, offset=offset)


@router.post('/', response_model=NotificationOut, status_code=201)
def publish_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role('admin')),
):
    notification = Notification(**payload.model_dump(), author_id=admin.id)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

"""Account management restored from Kynang-main, using Tin authentication and DB."""
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.security import get_password_hash, require_role
from src.database import get_db
from src.models.user import User

router = APIRouter()
Role = Literal['admin', 'candidate', 'employer', 'provider']


class AccountOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {'from_attributes': True}


class AccountCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=6, max_length=72)
    role: Role = 'candidate'
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=200)
    is_active: bool = True


class AccountUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    role: Optional[Role] = None
    phone: Optional[str] = Field(None, max_length=30)
    company_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


def save_account(db: Session, user: User):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Email này đã được sử dụng')
    db.refresh(user)
    return user


def find_account(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(404, 'Không tìm thấy tài khoản')
    return user


@router.get('/', response_model=list[AccountOut])
def list_accounts(
    q: Optional[str] = None,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role('admin')),
):
    query = db.query(User).filter(User.is_deleted == False)
    if q:
        term = f'%{q}%'
        query = query.filter(or_(User.full_name.ilike(term), User.email.ilike(term), User.company_name.ilike(term)))
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.id.desc()).offset(offset).limit(limit).all()


@router.post('/', response_model=AccountOut, status_code=201)
def create_account(
    payload: AccountCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role('admin')),
):
    data = payload.model_dump(exclude={'password'})
    data['email'] = str(payload.email).lower()
    user = User(**data, password_hash=get_password_hash(payload.password))
    db.add(user)
    return save_account(db, user)


@router.put('/{user_id}', response_model=AccountOut)
def update_account(
    user_id: int,
    payload: AccountUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role('admin')),
):
    user = find_account(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    if any(data.get(key) is None for key in ('email', 'full_name', 'role', 'is_active') if key in data):
        raise HTTPException(422, 'Thông tin bắt buộc không được để trống')
    if user.id == admin.id and (data.get('is_active') is False or data.get('role', 'admin') != 'admin'):
        raise HTTPException(400, 'Không thể khóa hoặc hạ quyền tài khoản đang đăng nhập')
    password = data.pop('password', None)
    if password:
        user.password_hash = get_password_hash(password)
    if 'email' in data:
        data['email'] = str(data['email']).lower()
    for key, value in data.items():
        setattr(user, key, value)
    return save_account(db, user)


@router.delete('/{user_id}')
def delete_account(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role('admin')),
):
    user = find_account(db, user_id)
    if user.id == admin.id:
        raise HTTPException(400, 'Không thể xóa tài khoản đang đăng nhập')
    user.is_deleted = True
    db.commit()
    return {'message': 'Đã xóa tài khoản', 'id': user.id}

"""
Router: Xác Thực Người Dùng & Phân Quyền (Authentication & RBAC)
Bao gồm: Đăng ký (3 vai trò), Đăng nhập (Set Cookie HttpOnly), Đăng xuất, Lấy thông tin /me.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User, Employer, Worker
from src.core.security import get_current_user
from src.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserMeResponse
from src.controllers.auth_controller import AuthController
from pydantic import BaseModel, Field

logger = logging.getLogger("auth_router")
router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    company_name: Optional[str] = Field(default=None, max_length=200)
    company_logo_url: Optional[str] = Field(default=None, max_length=500)
    company_description: Optional[str] = Field(default=None, max_length=10000)


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    if not payload.full_name.strip():
        raise HTTPException(422, "Vui lòng nhập họ tên")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    if user.role == "employer":
        employer = db.query(Employer).filter_by(user_id=user.id).first()
        if employer:
            employer.contact_name = payload.full_name
    elif user.role in ("worker", "candidate"):
        worker = db.query(Worker).filter_by(user_id=user.id).first()
        if worker:
            worker.full_name = payload.full_name
    db.commit()
    return {"full_name": user.full_name, "company_name": user.company_name,
            "company_logo_url": user.company_logo_url,
            "company_description": user.company_description}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới:
    - worker: Người lao động
    - employer: Nhà tuyển dụng
    - course_provider: Đơn vị đào tạo
    (Tuyệt đối không cho phép đăng ký admin qua API)
    """
    return AuthController.register(payload, db)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    response: Response,
    payload: Optional[LoginRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Đăng nhập hệ thống:
    - Nhận email + password (hỗ trợ cả JSON body lẫn form data của Swagger)
    - Kiểm tra rate limit (5 lần sai trong 15 phút)
    - Gắn Cookie HttpOnly access_token (hết hạn 8 giờ)
    - Trả về { role, display_name, is_verified, access_token }
    """
    # Nếu client gửi JSON body
    if payload and payload.email and payload.password:
        return AuthController.login(payload, request, response, db)

    # Nếu gửi qua form data hoặc JSON raw
    email = None
    password = None
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            email = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp email và mật khẩu",
        )

    req = LoginRequest(email=email, password=password)
    return AuthController.login(req, request, response, db)


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Đăng xuất: Xóa cookie HttpOnly và đưa token vào blacklist.
    """
    return AuthController.logout(request, response, db)


@router.get("/me", response_model=UserMeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy thông tin người dùng đang đăng nhập:
    Trả về { user_id, email, role, display_name, is_verified }
    """
    return AuthController.get_me(current_user, db)

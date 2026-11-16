"""
Router: Xác Thực Người Dùng & Phân Quyền (Authentication & RBAC)
Bao gồm: Đăng ký (3 vai trò), Đăng nhập (Set Cookie HttpOnly), Đăng xuất, Lấy thông tin /me.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.core.security import get_current_user
from src.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserMeResponse
from src.controllers.auth_controller import AuthController

logger = logging.getLogger("auth_router")
router = APIRouter()


@router.post("/demo/employer", response_model=AuthResponse)
def demo_employer_login(request: Request, response: Response, db: Session = Depends(get_db)):
    """Explicitly enabled local demo entry; never chooses an arbitrary user or admin."""
    import os
    from datetime import datetime
    from src.core.security import create_access_token, COOKIE_SECURE
    if os.getenv("DEMO_EMPLOYER_LOGIN", "0") != "1":
        raise HTTPException(404, "Đăng nhập employer demo chưa được bật")
    if request.url.hostname not in {"localhost", "127.0.0.1", "::1"} or request.headers.get("origin") not in {
        "http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8081", "http://127.0.0.1:8081"
    }:
        raise HTTPException(403, "Đăng nhập demo chỉ dành cho giao diện localhost")
    user = db.query(User).filter_by(email="evidence.employer@demo.local").first()
    if not user or user.role != "employer" or user.is_deleted or not user.is_active:
        raise HTTPException(409, "Tài khoản employer demo chưa sẵn sàng; hãy chạy seed demo")
    from src.models.user import Employer
    employer = db.query(Employer).filter_by(user_id=user.id).first()
    if not employer or not employer.is_verified:
        raise HTTPException(403, "Tài khoản employer demo chưa được duyệt")
    profile = AuthController.get_me(user, db)
    if not profile.is_verified:
        raise HTTPException(403, "Tài khoản employer demo chưa được duyệt")
    user.last_login_at = datetime.utcnow()
    token = create_access_token({"sub": str(user.id), "role": "employer", "name": profile.display_name})
    db.commit()
    response.set_cookie("access_token", token, max_age=28800, expires=28800, path="/", httponly=True, samesite="lax", secure=COOKIE_SECURE)
    return AuthResponse(role="employer", display_name=profile.display_name, is_verified=True, access_token=token,
                        user_id=user.id, email=user.email,
                        user={"id": user.id, "user_id": user.id, "email": user.email, "role": "employer",
                              "full_name": user.full_name, "company_name": user.company_name, "is_verified": True})


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

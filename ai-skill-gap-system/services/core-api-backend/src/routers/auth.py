"""
Router: Xác Thực Người Dùng & Quản Lý Quyền (Authentication & RBAC)
Bổ sung: Đăng xuất (Token Blacklist), Gia hạn phiên (Refresh Token HttpOnly), Quên & Đặt lại mật khẩu.
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User, UserRole, TokenBlacklist
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    is_token_blacklisted,
    get_current_user,
    oauth2_scheme,
)

logger = logging.getLogger("auth_router")
router = APIRouter()

# Bộ nhớ lưu OTP quên mật khẩu tạm thời: email -> {"otp": "123456", "expires_at": datetime}
RESET_OTP_STORE: dict = {}


# ── Pydantic Schemas ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[Literal["candidate", "employer", "provider"]] = "candidate"
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    phone: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_description: Optional[str] = None


class UserOut(BaseModel):
    phone: Optional[str] = None
    id: int
    email: str
    full_name: str
    role: str
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_description: Optional[str] = None
    latest_cv_analysis: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    user: UserOut


# ── Endpoints ────────────────────────────────────────────────────
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản người dùng mới:
    - candidate: Người lao động / Sinh viên
    - employer: Nhà tuyển dụng
    - provider: Đơn vị đào tạo / Bán khóa học
    """
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng trong hệ thống",
        )

    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu phải chứa ít nhất 6 ký tự",
        )

    hashed_password = get_password_hash(payload.password)

    new_user = User(
        email=payload.email.lower(),
        password_hash=hashed_password,
        full_name=payload.full_name,
        role=payload.role or "candidate",
        company_name=payload.company_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Đăng nhập lấy JWT access_token và refresh_token (HttpOnly Cookie).
    Hỗ trợ cả JSON body lẫn Form data cho Swagger UI OAuth2.
    """
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

    input_str = str(email).strip().lower()
    from sqlalchemy import or_
    user = (
        db.query(User)
        .filter(
            or_(
                User.email == input_str,
                User.email == f"{input_str}@skillgap.local"
            )
        )
        .first()
    )
    if not user or getattr(user, "is_deleted", False) or not user.is_active or not verify_password(str(password), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_str = str(user.role.value if hasattr(user.role, "value") else user.role)
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": role_str,
        "name": user.full_name,
    }

    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)

    # Đặt Refresh Token vào HttpOnly Cookie (sống 7 ngày)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 3600,
        samesite="lax",
        secure=False,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    body: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Tự động gia hạn phiên: Nhận Refresh Token từ HttpOnly Cookie hoặc request body,
    cấp lại Access Token mới.
    """
    token_str = (
        (body.refresh_token if body else None)
        or request.cookies.get("refresh_token")
    )

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy refresh token trong phiên làm việc",
        )

    if is_token_blacklisted(token_str, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token đã bị vô hiệu hóa (vui lòng đăng nhập lại)",
        )

    payload = decode_access_token(token_str)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
        )

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(401, "Refresh token không hợp lệ")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or getattr(user, "is_deleted", False) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị khóa",
        )

    role_str = str(user.role.value if hasattr(user.role, "value") else user.role)
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": role_str,
        "name": user.full_name,
    }

    new_access_token = create_access_token(data=token_payload)
    new_refresh_token = create_refresh_token(data=token_payload)

    # Đưa refresh token cũ vào blacklist để chống replay attack
    try:
        db.add(TokenBlacklist(token=token_str))
        db.commit()
    except Exception:
        db.rollback()

    # Cập nhật Cookie mới
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=7 * 24 * 3600,
        samesite="lax",
        secure=False,
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Đăng xuất: Đưa JWT token hiện tại và Refresh Token vào Blacklist,
    xóa Cookie HttpOnly trên trình duyệt.
    """
    # 1. Blacklist Access Token
    if token:
        try:
            if not is_token_blacklisted(token, db):
                db.add(TokenBlacklist(token=token))
                db.commit()
        except Exception:
            db.rollback()

    # 2. Blacklist Refresh Token từ Cookie
    cookie_refresh = request.cookies.get("refresh_token")
    if cookie_refresh:
        try:
            if not is_token_blacklisted(cookie_refresh, db):
                db.add(TokenBlacklist(token=cookie_refresh))
                db.commit()
        except Exception:
            db.rollback()

    # 3. Xóa Cookie
    response.delete_cookie(key="refresh_token")

    return {"message": "Đăng xuất thành công, phiên làm việc đã được hủy"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Quên mật khẩu: Tạo mã OTP xác thực 6 số (lưu bộ nhớ và log ra console).
    """
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        # Bảo mật: không báo rõ email chưa tồn tại
        return {"message": "Nếu email tồn tại, mã OTP đặt lại mật khẩu đã được gửi.", "email": email_clean}

    # Sinh mã OTP 6 số
    otp = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now() + timedelta(minutes=15)
    RESET_OTP_STORE[email_clean] = {"otp": otp, "expires_at": expires_at, "attempts": 0}

    # Log nổi bật ra console server
    print("\n" + "=" * 60)
    print(f"🔑 [AUTH FORGOT PASSWORD] Yêu cầu từ: {email_clean}")
    print(f"👉 MÃ OTP XÁC THỰC: 【 {otp} 】")
    print(f"⏱️  Hiệu lực: 15 phút (Hết hạn lúc: {expires_at.strftime('%H:%M:%S')})")
    print("=" * 60 + "\n")

    return {"message": "Nếu email tồn tại, mã OTP đặt lại mật khẩu đã được gửi.", "email": email_clean}



@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Đặt lại mật khẩu với mã OTP hợp lệ.
    """
    email_clean = payload.email.lower().strip()
    stored = RESET_OTP_STORE.get(email_clean)

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chưa có yêu cầu đặt lại mật khẩu hoặc mã OTP đã hết hạn",
        )

    if datetime.now() > stored["expires_at"]:
        RESET_OTP_STORE.pop(email_clean, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP đã hết hạn, vui lòng yêu cầu mã mới",
        )

    if stored["otp"] != payload.otp.strip():
        stored['attempts'] = stored.get('attempts', 0) + 1
        if stored['attempts'] >= 5:
            RESET_OTP_STORE.pop(email_clean, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP không chính xác",
        )

    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có ít nhất 6 ký tự",
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user.password_hash = get_password_hash(payload.new_password)
    db.commit()

    # Xóa OTP sau khi đổi thành công
    RESET_OTP_STORE.pop(email_clean, None)

    return {"message": "Đặt lại mật khẩu thành công! Bạn có thể đăng nhập bằng mật khẩu mới."}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản hiện tại qua Bearer token."""
    return UserOut.model_validate(current_user)


@router.put("/profile", response_model=UserOut)
def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cập nhật thông tin hồ sơ người dùng / công ty."""
    if payload.new_password is not None:
        if not payload.old_password or not verify_password(payload.old_password, current_user.password_hash):
            raise HTTPException(400, "Current password is incorrect")
        if len(payload.new_password) < 6:
            raise HTTPException(422, "Password must contain at least 6 characters")
        current_user.password_hash = get_password_hash(payload.new_password)
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.full_name:
        current_user.full_name = payload.full_name
    if payload.company_name is not None:
        current_user.company_name = payload.company_name
    if payload.company_logo_url is not None:
        current_user.company_logo_url = payload.company_logo_url
    if payload.company_description is not None:
        current_user.company_description = payload.company_description

    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)

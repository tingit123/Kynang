"""
Core Security Module: JWT Token Management, Cookie Auth & Role-Based Access Control (RBAC)
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt

from src.database import get_db
from src.models.user import User, TokenBlacklist

# Cấu hình bảo mật & JWT
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-halloween-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 giờ
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# In-memory lưu các lần đăng nhập sai: (email, ip) -> [datetime, ...]
FAILED_ATTEMPTS: dict[tuple[str, str], list[datetime]] = {}


def check_login_rate_limit(email: str, ip: str):
    """Giới hạn 5 lần đăng nhập sai trong 15 phút theo email + IP."""
    key = (email.strip().lower(), ip)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=15)
    attempts = [t for t in FAILED_ATTEMPTS.get(key, []) if t > cutoff]
    FAILED_ATTEMPTS[key] = attempts
    if len(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đã đăng nhập sai quá 5 lần. Vui lòng thử lại sau 15 phút.",
        )


def record_failed_attempt(email: str, ip: str):
    """Ghi nhận một lần đăng nhập thất bại."""
    key = (email.strip().lower(), ip)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=15)
    attempts = [t for t in FAILED_ATTEMPTS.get(key, []) if t > cutoff]
    attempts.append(now)
    FAILED_ATTEMPTS[key] = attempts


def reset_failed_attempts(email: str, ip: str):
    """Xóa lịch sử đăng nhập sai sau khi đăng nhập thành công."""
    key = (email.strip().lower(), ip)
    FAILED_ATTEMPTS.pop(key, None)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu người dùng với chuỗi băm bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Tạo chuỗi băm bcrypt an toàn cho mật khẩu."""
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token chứa thông tin định danh và vai trò người dùng (hết hạn 8 giờ)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Giải mã JWT token và trả về payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def is_token_blacklisted(token: str, db: Session) -> bool:
    """Kiểm tra token có nằm trong danh sách đen (đã logout) hay không."""
    if not token:
        return False
    try:
        found = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        return found is not None
    except Exception:
        return False


def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Dependency lấy User hiện tại nếu có token hợp lệ trong Cookie hoặc Header."""
    auth_token = request.cookies.get("access_token") or token
    if not auth_token:
        return None

    if is_token_blacklisted(auth_token, db):
        return None

    payload = decode_access_token(auth_token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user = db.query(User).filter(User.id == int(user_id), User.is_deleted == False).first()
        if user and not user.is_active:
            return None
        return user
    except Exception:
        return None


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency bắt buộc người dùng phải đăng nhập hợp lệ qua Cookie HttpOnly hoặc Bearer header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_token = request.cookies.get("access_token") or token
    if not auth_token:
        raise credentials_exception

    if is_token_blacklisted(auth_token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã kết thúc",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(auth_token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or getattr(user, "is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khoá",
        )

    return user


def require_role(roles: Union[List[str], str]):
    """
    Factory dependency phân quyền RBAC:
    Kiểm tra người dùng hiện tại có nằm trong danh sách quyền cho phép hay không.
    """
    allowed_roles = [roles] if isinstance(roles, str) else list(roles)

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = str(current_user.role)
        # Hỗ trợ cả trường hợp candidate/worker hoặc provider/course_provider
        matched = False
        if user_role in allowed_roles:
            matched = True
        elif user_role in ("worker", "candidate") and ("worker" in allowed_roles or "candidate" in allowed_roles):
            matched = True
        elif user_role in ("course_provider", "provider") and ("course_provider" in allowed_roles or "provider" in allowed_roles):
            matched = True

        if not matched:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Quyền truy cập bị từ chối. Yêu cầu một trong các vai trò: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker

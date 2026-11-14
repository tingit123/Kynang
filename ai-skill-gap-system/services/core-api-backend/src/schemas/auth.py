"""
Pydantic Schemas cho Xác thực & Phân quyền (Authentication & RBAC)
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    role: str = Field(..., description="Chức vụ: worker, employer, course_provider")
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., min_length=8, description="Mật khẩu tối thiểu 8 ký tự")
    
    # Dành cho Worker (Người lao động)
    full_name: Optional[str] = None
    
    # Dành cho Employer (Nhà tuyển dụng)
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Dành cho Course Provider (Đơn vị đào tạo)
    provider_name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email hoặc tên đăng nhập")
    password: str = Field(..., description="Mật khẩu")


class AuthResponse(BaseModel):
    role: str
    display_name: str
    is_verified: bool = True
    access_token: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    user: Optional[dict] = None


class UserMeResponse(BaseModel):
    user_id: int
    email: str
    role: str
    display_name: str
    is_verified: bool = True

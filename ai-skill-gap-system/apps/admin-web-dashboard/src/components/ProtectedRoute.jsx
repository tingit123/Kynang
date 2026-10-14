import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * Component bảo vệ Route theo Role (Role-Based Access Control - RBAC)
 * @param {Array<string>} allowedRoles - Danh sách role được phép truy cập (vd: ['admin'], ['employer'])
 * @param {React.ReactNode} children - Component con được render nếu thỏa mãn quyền
 */
export default function ProtectedRoute({ allowedRoles = [], children }) {
  const location = useLocation();

  // Đọc thông tin xác thực từ localStorage (đồng bộ với API backend)
  let currentUser = null;
  const token = localStorage.getItem('access_token');
  try {
    const rawUser = localStorage.getItem('current_user');
    if (rawUser) currentUser = JSON.parse(rawUser);
  } catch (e) {
    currentUser = null;
  }

  // 1. Chưa đăng nhập -> Điều hướng về trang đăng nhập với state quay lại
  if (!token || !currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 2. Không đúng quyền hạn -> Chuyển hướng về trang tương ứng với quyền của họ
  if (allowedRoles.length > 0 && !allowedRoles.includes(currentUser.role)) {
    if (currentUser.role === 'admin') return <Navigate to="/admin" replace />;
    if (currentUser.role === 'employer') return <Navigate to="/employer" replace />;
    if (currentUser.role === 'provider') return <Navigate to="/provider" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
}

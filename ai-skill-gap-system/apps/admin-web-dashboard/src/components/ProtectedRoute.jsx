import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * Component bảo vệ Route theo Role (Role-Based Access Control - RBAC)
 * @param {Array<string>} allowedRoles - Danh sách role được phép truy cập (vd: ['admin'], ['employer'])
 * @param {React.ReactNode} children - Component con được render nếu thỏa mãn quyền
 *
 * Lưu ý quan trọng: role được chuẩn hóa về lowercase + trim() trước khi so sánh
 * để tránh lỗi bouncing do backend trả về Enum dạng UserRole.EMPLOYER hoặc "Employer".
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

  // 2. Chuẩn hóa role: chuyển về chữ thường, cắt khoảng trắng,
  //    loại bỏ prefix "userrole." nếu backend Python trả về dạng Enum
  const userRole = String(currentUser.role || '')
    .toLowerCase()
    .trim()
    .replace(/^userrole\./, '');

  const normalizedAllowedRoles = allowedRoles.map(r =>
    String(r).toLowerCase().trim().replace(/^userrole\./, '')
  );

  // 3. Không đúng quyền hạn -> Chuyển hướng về đúng portal của role họ
  if (normalizedAllowedRoles.length > 0 && !normalizedAllowedRoles.includes(userRole)) {
    if (userRole === 'admin')    return <Navigate to="/admin/dashboard"         replace />;
    if (userRole === 'employer') return <Navigate to="/employer/dashboard"      replace />;
    if (userRole === 'provider') return <Navigate to="/provider/gap-analytics"  replace />;
    return <Navigate to="/" replace />;
  }

  return children;
}

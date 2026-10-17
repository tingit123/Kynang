import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * AuthGuard - Người gác cổng đa năng (Role-Based Access Control)
 * - Kiểm tra trạng thái đăng nhập (token + current_user).
 * - Chuẩn hóa role (lowercase, trim, loại bỏ tiền tố Python Enum 'userrole.').
 * - Nếu không đủ quyền hạn: Dùng switch-case đẩy user về đúng "Nhà" của họ.
 *
 * @param {Array<string>} allowedRoles - Danh sách role được phép truy cập (vd: ['admin'], ['employer', 'admin'])
 * @param {React.ReactNode} children - Component con được render nếu thỏa mãn điều kiện
 */
export default function AuthGuard({ allowedRoles = [], children }) {
  const location = useLocation();

  // 1. Đọc access_token và current_user từ localStorage
  const token = localStorage.getItem('access_token');
  let currentUser = null;

  try {
    const rawUser = localStorage.getItem('current_user');
    if (rawUser) currentUser = JSON.parse(rawUser);
  } catch (error) {
    console.error('[AuthGuard] Lỗi phân tích current_user:', error);
    currentUser = null;
  }

  // 2. Chưa đăng nhập -> Đẩy về trang /login và lưu lại location định truy cập
  if (!token || !currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 3. Chuẩn hóa chuỗi Role của người dùng
  const userRole = String(currentUser?.role || '')
    .toLowerCase()
    .trim()
    .replace('userrole.', '');

  // Chuẩn hóa danh sách allowedRoles truyền vào
  const normalizedAllowedRoles = allowedRoles.map(role =>
    String(role).toLowerCase().trim().replace('userrole.', '')
  );

  // 4. Kiểm tra phân quyền: Nếu Route yêu cầu roles cụ thể mà user không có
  if (normalizedAllowedRoles.length > 0 && !normalizedAllowedRoles.includes(userRole)) {
    // Đẩy về đúng "Nhà" của từng role thay vì đẩy mù quáng về '/'
    switch (userRole) {
      case 'admin':
        return <Navigate to="/admin/dashboard" replace />;
      case 'employer':
        return <Navigate to="/employer/dashboard" replace />;
      case 'provider':
        return <Navigate to="/provider/gap-analytics" replace />;
      case 'candidate':
      default:
        return <Navigate to="/" replace />;
    }
  }

  // 5. Thỏa mãn quyền truy cập -> Render nội dung bên trong
  return children;
}

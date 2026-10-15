import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * GuestGuard - Bảo vệ các trang Candidate & Public khỏi các role quản trị
 * - Cho phép: Người dùng chưa đăng nhập (khách) HOẶC người dùng có role là 'candidate'.
 * - Chặn: Nếu user đã đăng nhập mà có role là Doanh nghiệp, Admin, hoặc Trung tâm đào tạo,
 *   NGAY LẬP TỨC đá họ về đúng trang quản trị tương ứng (sử dụng switch-case).
 *
 * @param {React.ReactNode} children - Component con (CandidateLayout)
 */
export default function GuestGuard({ children }) {
  const token = localStorage.getItem('access_token');
  let currentUser = null;

  try {
    const rawUser = localStorage.getItem('current_user');
    if (rawUser) currentUser = JSON.parse(rawUser);
  } catch (error) {
    console.error('[GuestGuard] Lỗi phân tích current_user:', error);
    currentUser = null;
  }

  // Nếu người dùng đã đăng nhập, kiểm tra vai trò (role)
  if (token && currentUser) {
    const userRole = String(currentUser?.role || '')
      .toLowerCase()
      .trim()
      .replace('userrole.', '');

    // Nếu role khác 'candidate' (ví dụ employer, admin, provider)
    if (userRole && userRole !== 'candidate') {
      switch (userRole) {
        case 'admin':
          return <Navigate to="/admin/dashboard" replace />;
        case 'employer':
          return <Navigate to="/employer/dashboard" replace />;
        case 'provider':
          return <Navigate to="/provider/gap-analytics" replace />;
        default:
          break;
      }
    }
  }

  // Khách chưa đăng nhập HOẶC Ứng viên (candidate) -> Cho phép truy cập bình thường
  return children;
}

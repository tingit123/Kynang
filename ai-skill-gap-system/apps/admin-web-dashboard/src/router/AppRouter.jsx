import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// ── 1. LAYOUTS ──
import CandidateLayout from '../layouts/CandidateLayout';
import AdminLayout from '../layouts/AdminLayout';
import EmployerLayout from '../layouts/EmployerLayout';
import ProviderLayout from '../layouts/ProviderLayout';

// ── 2. CANDIDATE PAGES (3 Trang Bóc Tách Chuyên Biệt) ──
import AiDiagnosisPage from '../pages/candidate/AiDiagnosisPage';
import IndustryExplorePage from '../pages/candidate/IndustryExplorePage';
import SoftSkillsGuidePage from '../pages/candidate/SoftSkillsGuidePage';

// ── 3. ROLE PROTECTION GUARD ──
import ProtectedRoute from '../components/ProtectedRoute';

export default function AppRouter() {
  return (
    <Routes>
      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* 1. CANDIDATE PORTAL (Route: /)                                    */}
      {/* Giao diện Top Navbar ngang dành riêng cho Người Lao Động/Sinh Viên */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route path="/" element={<CandidateLayout />}>
        {/* Trang 1: Chẩn đoán AI & Lộ trình (Trang chủ ứng viên) */}
        <Route index element={<AiDiagnosisPage />} />
        <Route path="ai-diagnosis" element={<AiDiagnosisPage />} />

        {/* Trang 2: Khám Phá Ngành Nghề (Lương & Kỹ năng yêu cầu) */}
        <Route path="explore-industries" element={<IndustryExplorePage />} />

        {/* Trang 3: Cẩm Nang Kỹ Năng Mềm (Top 10 Soft Skills & Biểu đồ Gap) */}
        <Route path="soft-skills" element={<SoftSkillsGuidePage />} />
      </Route>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* 2. ADMIN PORTAL (Route: /admin/*)                                  */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<div className="p-6 bg-white rounded-xl shadow-xs">📊 Bảng Điều Khiển Tổng Quan KPI</div>} />
        <Route path="skills" element={<div className="p-6 bg-white rounded-xl shadow-xs">🧠 Kỹ Năng Mềm &amp; Theo Ngành</div>} />
        <Route path="workers" element={<div className="p-6 bg-white rounded-xl shadow-xs">👥 Quản Lý Người Lao Động</div>} />
        <Route path="employers" element={<div className="p-6 bg-white rounded-xl shadow-xs">🏢 Quản Lý Nhà Tuyển Dụng</div>} />
        <Route path="courses" element={<div className="p-6 bg-white rounded-xl shadow-xs">📚 Quản Lý Khóa Học</div>} />
        <Route path="crawler" element={<div className="p-6 bg-white rounded-xl shadow-xs">🕷️ Quản Lý Crawler Dữ Liệu</div>} />
      </Route>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* 3. EMPLOYER PORTAL (Route: /employer/*)                            */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/employer"
        element={
          <ProtectedRoute allowedRoles={['employer', 'admin']}>
            <EmployerLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/employer/dashboard" replace />} />
        <Route path="dashboard" element={<div className="p-6 bg-white rounded-xl shadow-xs">📈 Tổng Quan Tuyển Dụng Doanh Nghiệp</div>} />
        <Route path="market-skills" element={<div className="p-6 bg-white rounded-xl shadow-xs">🌐 Kỹ Năng Thị Trường Theo Ngành</div>} />
        <Route path="jobs" element={<div className="p-6 bg-white rounded-xl shadow-xs">📝 Quản Lý Tin Tuyển Dụng</div>} />
        <Route path="candidates" element={<div className="p-6 bg-white rounded-xl shadow-xs">📑 Quản Lý Ứng Viên Ứng Tuyển</div>} />
        <Route path="profile" element={<div className="p-6 bg-white rounded-xl shadow-xs">🏛️ Hồ Sơ Công Ty</div>} />
      </Route>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* 4. PROVIDER PORTAL (Route: /provider/*)                            */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/provider"
        element={
          <ProtectedRoute allowedRoles={['provider', 'admin']}>
            <ProviderLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/provider/gap-analytics" replace />} />
        <Route path="gap-analytics" element={<div className="p-6 bg-white rounded-xl shadow-xs">🔍 Phân Tích Kỹ Năng Thiếu Hụt</div>} />
        <Route path="courses" element={<div className="p-6 bg-white rounded-xl shadow-xs">🎓 Quản Lý Khóa Học Trung Tâm</div>} />
        <Route path="analytics" element={<div className="p-6 bg-white rounded-xl shadow-xs">🖱️ Thống Kê Lượt Click &amp; Quan Tâm</div>} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

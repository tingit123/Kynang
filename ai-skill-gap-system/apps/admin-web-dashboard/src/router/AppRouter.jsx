import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// ── 0. PUBLIC AUTH PAGES ──
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';

// ── 1. LAYOUTS ──
import CandidateLayout from '../layouts/CandidateLayout';
import AdminLayout from '../layouts/AdminLayout';
import EmployerLayout from '../layouts/EmployerLayout';
import ProviderLayout from '../layouts/ProviderLayout';

// ── 2. CANDIDATE PAGES (Các trang chức năng Ứng viên / Sinh viên) ──
import AiDiagnosisPage from '../pages/candidate/AiDiagnosisPage';
import IndustryExplorePage from '../pages/candidate/IndustryExplorePage';
import SoftSkillsGuidePage from '../pages/candidate/SoftSkillsGuidePage';

// ── 3. EMPLOYER PAGES (Cổng Nhà Tuyển Dụng) ──
import EmployerDashboardPage from '../pages/employer/EmployerDashboardPage';
import EmployerMarketSkillsPage from '../pages/employer/EmployerMarketSkillsPage';
import EmployerJobsPage from '../pages/employer/EmployerJobsPage';
import EmployerCandidatesPage from '../pages/employer/EmployerCandidatesPage';
import EmployerProfilePage from '../pages/employer/EmployerProfilePage';

// ── 4. PROVIDER PAGES (Cổng Đơn Vị Đào Tạo / Trung Tâm Khóa Học) ──
import ProviderGapAnalyticsPage from '../pages/provider/ProviderGapAnalyticsPage';
import ProviderCoursesPage from '../pages/provider/ProviderCoursesPage';
import ProviderAnalyticsPage from '../pages/provider/ProviderAnalyticsPage';

// ── 5. ROUTE GUARDS (Bộ lọc phân quyền thông minh) ──
import AuthGuard from '../components/guards/AuthGuard';
import GuestGuard from '../components/guards/GuestGuard';

export default function AppRouter() {
  return (
    <Routes>
      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* CỤM 1: PUBLIC AUTH ROUTES (Không bị bọc bởi bất kỳ Guard nào)      */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* CỤM 2: CANDIDATE PORTAL (Dành cho Sinh viên/Người lao động/Khách)  */}
      {/* Bọc bởi GuestGuard: Nếu Admin/Employer/Provider cố tình truy cập   */}
      {/* sẽ lập tức bị đá về đúng Dashboard của họ                          */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/"
        element={
          <GuestGuard>
            <CandidateLayout />
          </GuestGuard>
        }
      >
        <Route index element={<AiDiagnosisPage />} />
        <Route path="ai-diagnosis" element={<AiDiagnosisPage />} />
        <Route path="explore-industries" element={<IndustryExplorePage />} />
        <Route path="soft-skills" element={<SoftSkillsGuidePage />} />
      </Route>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* CỤM 3: EMPLOYER PORTAL (Route: /employer/*)                        */}
      {/* Bọc bởi AuthGuard: Chỉ cho phép role 'employer' (hoặc 'admin')     */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/employer"
        element={
          <AuthGuard allowedRoles={['employer', 'admin']}>
            <EmployerLayout />
          </AuthGuard>
        }
      >
        <Route index element={<Navigate to="/employer/dashboard" replace />} />
        <Route path="dashboard" element={<EmployerDashboardPage />} />
        <Route path="market-skills" element={<EmployerMarketSkillsPage />} />
        <Route path="jobs" element={<EmployerJobsPage />} />
        <Route path="candidates" element={<EmployerCandidatesPage />} />
        <Route path="profile" element={<EmployerProfilePage />} />
      </Route>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* CỤM 4: ADMIN PORTAL (Route: /admin/*)                              */}
      {/* Bọc bởi AuthGuard: Chỉ cho phép duy nhất role 'admin'              */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/admin"
        element={
          <AuthGuard allowedRoles={['admin']}>
            <AdminLayout />
          </AuthGuard>
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
      {/* CỤM 5: PROVIDER PORTAL (Route: /provider/*)                        */}
      {/* Bọc bởi AuthGuard: Chỉ cho phép role 'provider' (hoặc 'admin')     */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <Route
        path="/provider"
        element={
          <AuthGuard allowedRoles={['provider', 'admin']}>
            <ProviderLayout />
          </AuthGuard>
        }
      >
        <Route index element={<Navigate to="/provider/gap-analytics" replace />} />
        <Route path="gap-analytics" element={<ProviderGapAnalyticsPage />} />
        <Route path="courses" element={<ProviderCoursesPage />} />
        <Route path="analytics" element={<ProviderAnalyticsPage />} />
      </Route>

      {/* Fallback điều hướng về trang chủ */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

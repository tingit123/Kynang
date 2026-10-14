import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import HeaderUserMenu from '../components/HeaderUserMenu';

/**
 * Layout 3: Giao Diện Dành Cho Doanh Nghiệp / Nhà Tuyển Dụng (Route: /employer/*)
 * Đặc điểm: Sidebar thu gọn chuyên dụng, chỉ hiển thị dữ liệu thuộc quyền sở hữu của công ty mình.
 */
export default function EmployerLayout() {
  const sidebarLinkStyle = ({ isActive }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '11px 14px',
    borderRadius: '8px',
    fontSize: '13.5px',
    fontWeight: 600,
    textDecoration: 'none',
    color: isActive ? '#0284c7' : '#475569',
    backgroundColor: isActive ? '#e0f2fe' : 'transparent',
    borderLeft: isActive ? '3px solid #0284c7' : '3px solid transparent',
    transition: 'all 0.15s ease',
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f1f5f9', color: '#0f172a' }}>
      {/* ── SIDEBAR DOANH NGHIỆP (Thu gọn theo nghiệp vụ Employer) ── */}
      <aside style={{
        width: '250px',
        backgroundColor: '#ffffff',
        borderRight: '1px solid #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        height: '100vh',
      }}>
        {/* Logo Employer */}
        <div style={{ padding: '20px 18px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            backgroundColor: '#0284c7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 21h18" />
              <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16" />
              <path d="M9 9h1" />
              <path d="M9 13h1" />
              <path d="M9 17h1" />
              <path d="M14 9h1" />
              <path d="M14 13h1" />
              <path d="M14 17h1" />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a' }}>
              SkillGap<span style={{ color: '#0284c7' }}> Recruiter</span>
            </div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Cổng Nhà Tuyển Dụng</div>
          </div>
        </div>

        {/* Menu Điều Hướng Employer (Yêu cầu 2: EmployerLayout) */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <NavLink to="/employer/dashboard" style={sidebarLinkStyle}>
            📈 Tổng Quan Tuyển Dụng
          </NavLink>
          <NavLink to="/employer/market-skills" style={sidebarLinkStyle}>
            🌐 Kỹ Năng Theo Ngành (Thị trường)
          </NavLink>
          <NavLink to="/employer/jobs" style={sidebarLinkStyle}>
            📝 Quản Lý Tin Tuyển Dụng
          </NavLink>
          <NavLink to="/employer/candidates" style={sidebarLinkStyle}>
            📑 Quản Lý Ứng Viên (Hồ sơ nộp)
          </NavLink>
          <NavLink to="/employer/profile" style={sidebarLinkStyle}>
            🏛️ Hồ Sơ Công Ty
          </NavLink>
        </nav>

        {/* Ghi chú bảo mật dữ liệu */}
        <div style={{ padding: '12px 14px', margin: '12px', backgroundColor: '#f0f9ff', borderRadius: '8px', border: '1px solid #bae6fd', fontSize: '11.5px', color: '#0369a1', lineHeight: 1.5 }}>
          🔒 Dữ liệu ứng viên và tin đăng được phân quyền bảo mật riêng cho công ty của bạn.
        </div>
      </aside>

      {/* ── KHU VỰC NỘI DUNG CHÍNH ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Header Employer */}
        <header style={{
          height: '64px',
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 900,
        }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: '#475569' }}>
            <span>Doanh Nghiệp</span> / <span style={{ color: '#0284c7' }}>Trung Tâm Tuyển Dụng</span>
          </div>

          {/* Cụm Avatar + Đăng Xuất (Không có nút đăng nhập/đăng ký) */}
          <HeaderUserMenu roleBadgeText="🏢 Nhà Tuyển Dụng" defaultName="Doanh Nghiệp" />
        </header>

        {/* Nội dung trang con (Outlet) */}
        <main style={{ flex: 1, padding: '24px', minWidth: 0 }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import HeaderUserMenu from '../components/HeaderUserMenu';

/**
 * Layout 4: Giao Diện Dành Cho Trung Tâm Đào Tạo / Đối Tác Khóa Học (Route: /provider/*)
 * Đặc điểm: Sidebar thu gọn tập trung vào phân tích kỹ năng thiếu hụt và tối ưu khóa học.
 */
export default function ProviderLayout() {
  const sidebarLinkStyle = ({ isActive }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '11px 14px',
    borderRadius: '8px',
    fontSize: '13.5px',
    fontWeight: 600,
    textDecoration: 'none',
    color: isActive ? '#7c3aed' : '#475569',
    backgroundColor: isActive ? '#f3e8ff' : 'transparent',
    borderLeft: isActive ? '3px solid #7c3aed' : '3px solid transparent',
    transition: 'all 0.15s ease',
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#faf5ff', color: '#0f172a' }}>
      {/* ── SIDEBAR ĐƠN VỊ ĐÀO TẠO (Thu gọn theo nghiệp vụ Provider) ── */}
      <aside style={{
        width: '250px',
        backgroundColor: '#ffffff',
        borderRight: '1px solid #e9d5ff',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        height: '100vh',
      }}>
        {/* Logo Provider */}
        <div style={{ padding: '20px 18px', borderBottom: '1px solid #faf5ff', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            backgroundColor: '#7c3aed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h10" />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a' }}>
              SkillGap<span style={{ color: '#7c3aed' }}> Edu</span>
            </div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Cổng Đơn Vị Đào Tạo</div>
          </div>
        </div>

        {/* Menu Điều Hướng Provider (Yêu cầu 2: ProviderLayout) */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <NavLink to="/provider/gap-analytics" style={sidebarLinkStyle}>
            🔍 Phân Tích Kỹ Năng Thiếu Hụt
          </NavLink>
          <NavLink to="/provider/courses" style={sidebarLinkStyle}>
            🎓 Quản Lý Khóa Học
          </NavLink>
          <NavLink to="/provider/analytics" style={sidebarLinkStyle}>
            🖱️ Thống Kê Lượt Click &amp; Quan Tâm
          </NavLink>
        </nav>

        {/* Mẹo tối ưu khóa học */}
        <div style={{ padding: '12px 14px', margin: '12px', backgroundColor: '#f5f3ff', borderRadius: '8px', border: '1px solid #ddd6fe', fontSize: '11.5px', color: '#6d28d9', lineHeight: 1.5 }}>
          💡 <strong>Gợi ý AI:</strong> Tạo các khóa học bám sát chỉ số Gap cao nhất tại Cần Thơ để tiếp cận lượng học viên lớn nhất.
        </div>
      </aside>

      {/* ── KHU VỰC NỘI DUNG CHÍNH ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, backgroundColor: '#f8fafc' }}>
        {/* Header Provider */}
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
            <span>Đơn Vị Đào Tạo</span> / <span style={{ color: '#7c3aed' }}>Quản Trị Khóa Học</span>
          </div>

          {/* Cụm Avatar + Đăng Xuất (Không có nút đăng nhập/đăng ký) */}
          <HeaderUserMenu roleBadgeText="📚 Trung Tâm Đào Tạo" defaultName="Đơn Vị Đào Tạo" />
        </header>

        {/* Nội dung trang con (Outlet) */}
        <main style={{ flex: 1, padding: '24px', minWidth: 0 }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

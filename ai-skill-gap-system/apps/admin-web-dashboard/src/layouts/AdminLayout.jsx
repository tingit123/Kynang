import React from 'react';
import { NavLink, Outlet, Link } from 'react-router-dom';
import HeaderUserMenu from '../components/HeaderUserMenu';

/**
 * Layout 2: Giao Diện Quản Trị Hệ Thống (Route: /admin/*)
 * Đặc điểm: Sidebar quản trị đầy đủ, Header có Avatar và nút Đăng xuất (Không có nút Đăng nhập/Đăng ký).
 */
export default function AdminLayout() {
  const sidebarLinkStyle = ({ isActive }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    borderRadius: '8px',
    fontSize: '13.5px',
    fontWeight: 600,
    textDecoration: 'none',
    color: isActive ? '#0fa39e' : '#cbd5e1',
    backgroundColor: isActive ? 'rgba(15,163,158,0.15)' : 'transparent',
    borderLeft: isActive ? '3px solid #0fa39e' : '3px solid transparent',
    transition: 'all 0.15s ease',
  });

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc' }}>
      {/* ── SIDEBAR QUẢN TRỊ (Full Sidebar) ── */}
      <aside style={{
        width: '260px',
        backgroundColor: '#1e293b',
        borderRight: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        height: '100vh',
      }}>
        {/* Logo Admin */}
        <div style={{ padding: '20px 18px', borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            backgroundColor: '#0fa39e',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <rect x="3" y="3" width="7" height="7" />
              <rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 800, color: '#ffffff' }}>
              SkillGap<span style={{ color: '#0fa39e' }}> Admin</span>
            </div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>Quản Trị Hệ Thống Toàn Quyền</div>
          </div>
        </div>

        {/* Menu Điều Hướng Admin (Yêu cầu 2: AdminLayout) */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', padding: '6px 10px', textTransform: 'uppercase' }}>
            Phân Tích &amp; Giám Sát
          </div>
          <NavLink to="/admin/dashboard" style={sidebarLinkStyle}>
            📊 Tổng Quan KPI
          </NavLink>
          <NavLink to="/admin/skills" style={sidebarLinkStyle}>
            🧠 Kỹ Năng Mềm &amp; Theo Ngành
          </NavLink>

          <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', padding: '12px 10px 6px', textTransform: 'uppercase' }}>
            Quản Lý Thực Thể
          </div>
          <NavLink to="/admin/workers" style={sidebarLinkStyle}>
            👥 Quản Lý Người Lao Động
          </NavLink>
          <NavLink to="/admin/employers" style={sidebarLinkStyle}>
            🏢 Quản Lý Nhà Tuyển Dụng
          </NavLink>
          <NavLink to="/admin/courses" style={sidebarLinkStyle}>
            📚 Quản Lý Khóa Học
          </NavLink>

          <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', padding: '12px 10px 6px', textTransform: 'uppercase' }}>
            Hệ Thống Dữ Liệu
          </div>
          <NavLink to="/admin/crawler" style={sidebarLinkStyle}>
            🕷️ Quản Lý Crawler
          </NavLink>
        </nav>

        {/* Footer Sidebar */}
        <div style={{ padding: '14px 16px', borderTop: '1px solid #334155', fontSize: '12px', color: '#94a3b8' }}>
          Phiên bản: <strong style={{ color: '#0fa39e' }}>v1.0.0 (2026)</strong>
        </div>
      </aside>

      {/* ── KHU VỰC NỘI DUNG CHÍNH ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, backgroundColor: '#f8fafc' }}>
        {/* Header Admin */}
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
          {/* Breadcrumb / Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#475569', fontWeight: 600 }}>
            <span>Hệ Thống Quản Trị</span>
            <span>/</span>
            <span style={{ color: '#0fa39e' }}>Bảng Điều Khiển</span>
          </div>

          {/* Cụm Avatar + Đăng Xuất (Không có nút đăng nhập/đăng ký) */}
          <HeaderUserMenu roleBadgeText="👑 Super Administrator" defaultName="Admin Hệ Thống" />
        </header>

        {/* Nội dung trang con (Outlet) */}
        <main style={{ flex: 1, padding: '24px', minWidth: 0 }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

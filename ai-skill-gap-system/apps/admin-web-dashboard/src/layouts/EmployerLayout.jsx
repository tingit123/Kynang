import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

/**
 * EmployerLayout.jsx - Giao diện Độc Lập Dành Cho Cổng Doanh Nghiệp (Employer Portal)
 * - Sidebar trái cố định (Tông màu xanh Blue #0284c7), chứa Logo công ty, thông tin nhà tuyển dụng & 5 menu.
 * - Header trên: Thông báo & Nút Đăng xuất (xóa localStorage và chuyển về trang chủ / của sinh viên).
 * - Content phải: Render các trang nghiệp vụ con thông qua <Outlet />.
 */
export default function EmployerLayout() {
  const navigate = useNavigate();

  // Đọc thông tin Doanh nghiệp từ localStorage
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('current_user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  });

  useEffect(() => {
    try {
      const raw = localStorage.getItem('current_user');
      if (raw) setUser(JSON.parse(raw));
    } catch (e) {}
  }, []);

  // Xử lý Đăng xuất: Xóa token & current_user -> Chuyển về trang chủ của sinh viên (/)
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    navigate('/');
  };

  // 5 Menu chức năng cốt lõi của Cổng Doanh Nghiệp
  const navItems = [
    {
      to: '/employer/dashboard',
      label: 'Tổng Quan Tuyển Dụng',
      icon: (
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    },
    {
      to: '/employer/jobs',
      label: 'Quản Lý Tin Tuyển Dụng',
      icon: (
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    },
    {
      to: '/employer/candidates',
      label: 'Quản Lý Ứng Viên',
      icon: (
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      )
    },
    {
      to: '/employer/market-skills',
      label: 'Kỹ Năng Theo Ngành',
      icon: (
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      )
    },
    {
      to: '/employer/profile',
      label: 'Hồ Sơ Doanh Nghiệp',
      icon: (
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      )
    }
  ];

  return (
    <div className="min-h-screen flex bg-slate-50 font-sans text-slate-800 antialiased">
      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 1. SIDEBAR TRÁI CỐ ĐỊNH (Tone Blue #0284c7) ──         */}
      {/* ══════════════════════════════════════════════════════════ */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 sticky top-0 h-screen z-40 shadow-xs">
        {/* Brand / Logo */}
        <div className="p-5 border-b border-slate-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-linear-to-br from-[#0284c7] to-[#0369a1] text-white flex items-center justify-center shadow-md shadow-sky-500/20">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <div className="text-base font-black tracking-tight text-slate-900 leading-tight">
              SkillGap <span className="text-[#0284c7]">Recruiter</span>
            </div>
            <div className="text-[11px] font-semibold text-sky-700 tracking-wide uppercase mt-0.5">
              Cổng Doanh Nghiệp
            </div>
          </div>
        </div>

        {/* Thẻ thông tin Nhà tuyển dụng */}
        <div className="p-4 mx-3 my-3 bg-linear-to-r from-sky-50/80 to-blue-50/50 border border-sky-100 rounded-2xl flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0284c7] text-white font-bold text-sm flex items-center justify-center shrink-0 shadow-xs">
            {(user?.company_name || user?.full_name || 'E').charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-black text-slate-800 truncate" title={user?.company_name || 'Doanh nghiệp'}>
              {user?.company_name || 'Doanh nghiệp'}
            </div>
            <div className="text-[11px] text-slate-500 truncate" title={user?.email || ''}>
              {user?.full_name || user?.email || 'Nhà tuyển dụng'}
            </div>
          </div>
        </div>

        {/* 5 Menu Điều Hướng */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all duration-150 ${
                  isActive
                    ? 'bg-[#0284c7] text-white shadow-md shadow-sky-600/20'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer Sidebar: Phân quyền bảo mật */}
        <div className="p-4 border-t border-slate-100 text-[11px] text-slate-400 bg-slate-50/50">
          <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
            <span>🔒</span> Dữ liệu phân quyền riêng biệt
          </div>
          <p className="text-[10px] text-slate-400 leading-relaxed">
            Hồ sơ ứng viên và tin đăng chỉ hiển thị cho tài khoản công ty của bạn.
          </p>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 2. KHU VỰC CHÍNH (HEADER + CONTENT PHẢI) ──            */}
      {/* ══════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header trên */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-6 sm:px-8 flex items-center justify-between sticky top-0 z-30 shadow-2xs backdrop-blur-md">
          {/* Tiêu đề & Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span className="font-semibold text-slate-400">Doanh nghiệp</span>
            <span>/</span>
            <span className="font-extrabold text-[#0284c7]">Trung Tâm Quản Lý Tuyển Dụng</span>
          </div>

          {/* Cụm Thông Báo & Nút Đăng Xuất */}
          <div className="flex items-center gap-4">
            {/* Thông báo chào mừng */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-sky-50 text-sky-700 text-xs font-bold rounded-lg border border-sky-100">
              <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
              <span>Hệ thống AI Tuyển Dụng đang hoạt động</span>
            </div>

            {/* Nút Đăng Xuất -> Xóa token & current_user -> Chuyển về trang chủ (/) */}
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-rose-200 text-rose-600 hover:bg-rose-50 hover:border-rose-300 font-bold text-xs transition-colors cursor-pointer"
              title="Đăng xuất khỏi Cổng Doanh Nghiệp"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Đăng xuất</span>
            </button>
          </div>
        </header>

        {/* Content Phải: Nơi render các chức năng thông qua Outlet */}
        <main className="flex-1 p-6 sm:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

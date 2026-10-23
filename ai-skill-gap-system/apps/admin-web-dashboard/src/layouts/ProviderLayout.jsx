import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';

/**
 * ProviderLayout.jsx - Cổng Quản Lý Dành Cho Đơn Vị Đào Tạo (Khớp 100% Mockup Mới)
 * - Nút toggle sidebar ở góc trên bên trái: ICON ONLY (BỎ chữ Menu).
 * - Khi bấm nút sẽ trượt ra Drawer Sidebar gồm 4 chức năng:
 *   1. Thị trường khóa học (Xem khóa học công khai của mọi đơn vị)
 *   2. Khóa học của tôi (Thêm, sửa, xóa khóa học bạn đăng)
 *   3. Phân tích kỹ năng (Kỹ năng đang thiếu để thiết kế khóa học)
 *   4. Thống kê lượt click (Mức độ quan tâm tới khóa học của bạn)
 * - Nút đóng trong drawer: ICON ONLY (BỎ chữ Đóng).
 * - Cụm Dropdown tài khoản trên Top Header:
 *   - Thông tin trung tâm (Logo, tên, giới thiệu trung tâm)
 *   - Hồ sơ cá nhân (Tên người đại diện, email, mật khẩu)
 *   - Đăng xuất
 */
export default function ProviderLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Đọc thông tin user từ localStorage
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

  // Đóng dropdown khi click ra ngoài
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('#providerUserDropdownArea')) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Xử lý Đăng xuất
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');
    navigate('/');
  };

  const providerName = user?.company_name || user?.organization || 'Mekong Skills';
  const contactName = user?.full_name || 'Trần Thanh Hải';
  const email = user?.email || 'contact@mekongskills.vn';
  const initialLetter = providerName.charAt(0).toUpperCase() || 'M';

  // 4 Chức năng chính theo đúng Mockup
  const navItems = [
    {
      to: '/provider/market',
      title: 'Thị trường khóa học',
      desc: 'Xem khóa học công khai của mọi đơn vị!'
    },
    {
      to: '/provider/courses',
      title: 'Khóa học của tôi',
      desc: 'Thêm, sửa, xóa khóa học bạn đăng'
    },
    {
      to: '/provider/gap-analytics',
      title: 'Phân tích kỹ năng',
      desc: 'Kỹ năng đang thiếu để thiết kế khóa học'
    },
    {
      to: '/provider/analytics',
      title: 'Thống kê lượt click',
      desc: 'Mức độ quan tâm tới khóa học của bạn'
    }
  ];

  // Tiêu đề phụ breadcrumb tương ứng theo đường dẫn
  const getSubtitle = () => {
    const p = location.pathname;
    if (p.includes('/provider/market')) return 'Thị trường khóa học';
    if (p.includes('/provider/courses')) return 'Khóa học của tôi';
    if (p.includes('/provider/gap-analytics')) return 'Phân tích kỹ năng';
    if (p.includes('/provider/analytics')) return 'Thống kê lượt click';
    if (p.includes('/provider/center-info')) return 'Tài khoản > Thông tin trung tâm';
    if (p.includes('/provider/profile')) return 'Tài khoản > Hồ sơ cá nhân';
    return 'Cổng đơn vị đào tạo';
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc] font-sans text-slate-800 antialiased relative">
      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 1. TOP HEADER (Khớp Mockup 1: BỎ chữ Menu) ──          */}
      {/* ══════════════════════════════════════════════════════════ */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 px-6 sm:px-8 py-3.5 flex items-center justify-between shadow-2xs">
        {/* Cụm Trái: Nút Icon Sidebar (BỎ chữ Menu) + Brand + Subtitle */}
        <div className="flex items-center gap-4">
          {/* Nút icon mở drawer (Không chữ Menu) */}
          <button
            onClick={() => setDrawerOpen(true)}
            type="button"
            className="w-10 h-10 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 flex items-center justify-center text-[#0a5146] transition-colors cursor-pointer outline-none"
            title="Mở menu chức năng"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>

          {/* Brand */}
          <div className="flex flex-col leading-tight select-none">
            <div className="text-xl font-black text-[#0a5146] tracking-tight">
              SkillGap<span className="text-[#0d9488]">AI</span>
            </div>
            <div className="text-[9px] font-extrabold text-slate-400 tracking-wider uppercase">
              TRUNG TÂM KHÓA HỌC
            </div>
          </div>

          <div className="h-6 w-px bg-slate-200 mx-1 hidden sm:block"></div>
          <span className="text-xs font-semibold text-slate-500 hidden sm:block">
            {getSubtitle()}
          </span>
        </div>

        {/* Cụm Phải: Nút Dropdown Tài Khoản */}
        <div id="providerUserDropdownArea" className="relative">
          <button
            type="button"
            onClick={() => setDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full border border-slate-200 bg-white hover:border-slate-300 transition-colors cursor-pointer outline-none"
          >
            <div className="w-8 h-8 rounded-full bg-[#0d9488] text-white flex items-center justify-center font-extrabold text-xs shrink-0">
              {initialLetter}
            </div>
            <div className="text-left hidden sm:block leading-tight">
              <div className="text-xs font-extrabold text-slate-900 truncate max-w-[140px]">{providerName}</div>
              <div className="text-[11px] text-slate-500 truncate max-w-[140px]">{contactName}</div>
            </div>
            <span className="text-[10px] text-slate-400">▼</span>
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-2xl border border-slate-200 shadow-xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
              {/* User box */}
              <div className="flex items-center gap-3 p-3 border-b border-slate-100 mb-1">
                <div className="w-10 h-10 rounded-full bg-[#0d9488] text-white flex items-center justify-center font-black text-sm shrink-0">
                  {initialLetter}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-black text-slate-900 truncate">{providerName}</div>
                  <div className="text-[11px] text-slate-500 truncate">{email}</div>
                </div>
              </div>

              {/* Item 1: Thông tin trung tâm */}
              <button
                type="button"
                onClick={() => {
                  setDropdownOpen(false);
                  navigate('/provider/center-info');
                }}
                className="w-full text-left p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group"
              >
                <div className="text-xs font-bold text-slate-900 group-hover:text-[#0a5146]">
                  Thông tin trung tâm
                </div>
                <div className="text-[11px] text-slate-400">Logo, tên, giới thiệu trung tâm</div>
              </button>

              {/* Item 2: Hồ sơ cá nhân */}
              <button
                type="button"
                onClick={() => {
                  setDropdownOpen(false);
                  navigate('/provider/profile');
                }}
                className="w-full text-left p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group"
              >
                <div className="text-xs font-bold text-slate-900 group-hover:text-[#0a5146]">
                  Hồ sơ cá nhân
                </div>
                <div className="text-[11px] text-slate-400">Tên người đại diện, email, mật khẩu</div>
              </button>

              <div className="h-px bg-slate-100 my-1"></div>

              {/* Item 3: Đăng xuất */}
              <button
                type="button"
                onClick={handleLogout}
                className="w-full text-left px-3 py-2.5 rounded-xl text-rose-600 hover:bg-rose-50 text-xs font-bold transition-colors cursor-pointer"
              >
                Đăng xuất
              </button>
            </div>
          )}
        </div>
      </header>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 2. OFF-CANVAS DRAWER SIDEBAR (BỎ chữ Đóng) ──           */}
      {/* ══════════════════════════════════════════════════════════ */}
      {/* Backdrop */}
      {drawerOpen && (
        <div
          onClick={() => setDrawerOpen(false)}
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 transition-opacity"
        />
      )}

      {/* Drawer Panel */}
      <aside
        className={`fixed top-0 left-0 bottom-0 w-72 max-w-[85vw] bg-[#073d35] text-white z-50 flex flex-col p-6 shadow-2xl transition-transform duration-250 ease-out ${
          drawerOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Drawer Header: Logo + Nút Icon Đóng (BỎ chữ Đóng) */}
        <div className="flex items-center justify-between pb-6 mb-6 border-b border-white/10">
          <div>
            <div className="text-2xl font-black text-white tracking-tight">
              SkillGap<span className="text-[#5eead4]">AI</span>
            </div>
            <div className="text-[9px] font-extrabold text-[#5eead4] tracking-widest uppercase mt-0.5">
              TRUNG TÂM KHÓA HỌC
            </div>
          </div>

          {/* Nút icon đóng: ICON ONLY, BỎ CHỮ ĐÓNG */}
          <button
            onClick={() => setDrawerOpen(false)}
            type="button"
            className="w-9 h-9 rounded-xl border border-white/20 bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors cursor-pointer outline-none"
            title="Đóng menu"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Section title */}
        <div className="text-[10px] font-black text-[#5eead4] uppercase tracking-wider mb-3 px-1">
          CHỨC NĂNG
        </div>

        {/* 4 Chức năng chính */}
        <nav className="flex-1 space-y-2.5 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setDrawerOpen(false)}
              className={({ isActive }) =>
                `block p-4 rounded-2xl transition-all ${
                  isActive
                    ? 'bg-[#0a5146] border border-[#14b8a6] text-white shadow-xs'
                    : 'bg-white/5 border border-white/10 text-teal-100 hover:bg-white/10'
                }`
              }
            >
              <div className="text-sm font-extrabold text-white mb-0.5">{item.title}</div>
              <div className="text-[11px] text-teal-200/70 leading-snug">{item.desc}</div>
            </NavLink>
          ))}
        </nav>

        {/* Bottom Profile card */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-[#5eead4] text-[#0a5146] font-black flex items-center justify-center text-xs shrink-0">
              {initialLetter}
            </div>
            <div className="min-w-0">
              <div className="font-extrabold text-white truncate max-w-[120px]">{providerName}</div>
              <div className="text-[10px] text-teal-200/70">Đơn vị đào tạo</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-rose-400 hover:text-rose-300 font-extrabold text-xs cursor-pointer"
          >
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 3. KHU VỰC NỘI DUNG CHÍNH (OUTLET) ──                  */}
      {/* ══════════════════════════════════════════════════════════ */}
      <main className="flex-1 p-6 sm:p-10 max-w-7xl w-full mx-auto">
        <Outlet />
      </main>
    </div>
  );
}

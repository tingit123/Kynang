import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

/**
 * ProviderLayout.jsx - Giao diện Độc Lập Dành Cho Đơn Vị Đào Tạo / Trung Tâm Khóa Học
 * Khớp chuẩn thiết kế theo hình ảnh mẫu (media_1792213850085_09b78eb3.png):
 * - Sidebar trái cố định tông màu Dark Teal (#0a5146) với logo SkillGapAI (AI màu mint).
 * - Subtitle: TRUNG TÂM KHÓA HỌC.
 * - 3 Menu chính dạng pill bo góc: Phân tích kỹ năng, Quản lý khóa học, Thống kê lượt click.
 * - Profile card đáy Sidebar: Khung bo góc tối màu, Avatar mint chữ cái đầu, Tên Đơn vị, Tên đại diện và Nút ĐĂNG XUẤT mint bo tròn.
 * - Content phải: Nền sáng xám nhẹ (#f8fafc), hiển thị trực tiếp nội dung không có topbar rườm rà.
 */
export default function ProviderLayout() {
  const navigate = useNavigate();

  // Đọc thông tin Đơn vị đào tạo từ localStorage
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

  // 3 Menu chức năng cốt lõi theo đúng thiết kế mẫu
  const navItems = [
    { to: '/provider/gap-analytics', label: 'Phân tích kỹ năng' },
    { to: '/provider/courses', label: 'Quản lý khóa học' },
    { to: '/provider/analytics', label: 'Thống kê lượt click' }
  ];

  const providerName = user?.company_name || 'Mekong Skills';
  const contactName = user?.full_name || 'Trần Thanh Hải';
  const initialLetter = providerName.charAt(0).toUpperCase() || 'M';

  return (
    <div className="min-h-screen flex bg-[#f8fafc] font-sans text-slate-800 antialiased">
      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 1. SIDEBAR TRÁI CỐ ĐỊNH (Dark Teal #0a5146) ──         */}
      {/* ══════════════════════════════════════════════════════════ */}
      <aside className="w-64 bg-[#0a5146] text-white flex flex-col shrink-0 sticky top-0 h-screen z-40 select-none shadow-md">
        {/* Brand / Logo */}
        <div className="pt-8 px-6 pb-6">
          <div className="text-2xl font-black tracking-tight text-white flex items-center">
            SkillGap<span className="text-[#5eead4]">AI</span>
          </div>
          <div className="text-[11px] font-bold text-teal-200/80 tracking-widest uppercase mt-1">
            TRUNG TÂM KHÓA HỌC
          </div>
        </div>

        {/* 3 Menu Điều Hướng (Pill style theo mockup) */}
        <nav className="flex-1 px-4 py-2 space-y-2 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block px-4 py-3 rounded-2xl text-sm font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-[#136659] text-white shadow-xs'
                    : 'text-teal-100/80 hover:text-white hover:bg-white/10'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Thẻ thông tin Đơn vị đào tạo ở đáy Sidebar */}
        <div className="p-4 mx-4 mb-6 bg-[#063830] rounded-2xl shadow-inner border border-teal-900/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#5eead4] text-[#0a5146] font-black text-base flex items-center justify-center shrink-0 shadow-sm">
              {initialLetter}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-bold text-white truncate" title={providerName}>
                {providerName}
              </div>
              <div className="text-xs text-teal-200/80 truncate" title={contactName}>
                {contactName}
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full mt-3.5 py-2 px-3 rounded-full bg-[#5eead4] hover:bg-[#2dd4bf] text-[#063830] text-xs font-black tracking-wider uppercase transition-colors shadow-xs cursor-pointer"
          >
            ĐĂNG XUẤT
          </button>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 2. KHU VỰC NỘI DUNG CHÍNH (OUTLET) ──                  */}
      {/* ══════════════════════════════════════════════════════════ */}
      <main className="flex-1 p-8 sm:p-10 min-w-0 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

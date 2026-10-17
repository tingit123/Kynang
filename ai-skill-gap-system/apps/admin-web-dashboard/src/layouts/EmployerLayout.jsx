import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

/**
 * EmployerLayout.jsx - Giao diện Độc Lập Dành Cho Cổng Doanh Nghiệp (Employer Portal)
 * Khớp chuẩn thiết kế theo hình ảnh mẫu (media_1792211014925_68f88b53.png):
 * - Sidebar trái cố định tông màu Dark Teal (#0a5146) với logo SkillGapAI (AI màu mint).
 * - 5 Menu chính dạng pill bo góc: Tổng quan, Tin tuyển dụng, Ứng viên, Kỹ năng thị trường, Hồ sơ công ty.
 * - Profile card đáy Sidebar: Khung bo góc tối màu, Avatar mint chữ cái đầu, Tên Công ty, Tên đại diện và Nút ĐĂNG XUẤT mint bo tròn.
 * - Content phải: Nền sáng xám nhẹ (#f8fafc), hiển thị trực tiếp nội dung không có header bar cồng kềnh.
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

  // 5 Menu chức năng cốt lõi theo đúng thiết kế mẫu
  const navItems = [
    { to: '/employer/dashboard', label: 'Tổng quan' },
    { to: '/employer/jobs', label: 'Tin tuyển dụng' },
    { to: '/employer/candidates', label: 'Ứng viên' },
    { to: '/employer/market-skills', label: 'Kỹ năng thị trường' },
    { to: '/employer/profile', label: 'Hồ sơ công ty' }
  ];

  const companyName = user?.company_name || 'Mekong Tech';
  const contactName = user?.full_name || 'Nguyễn Minh Khoa';
  const initialLetter = companyName.charAt(0).toUpperCase() || 'M';

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
            NHÀ TUYỂN DỤNG
          </div>
        </div>

        {/* 5 Menu Điều Hướng (Pill style theo mockup) */}
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

        {/* Thẻ thông tin Nhà tuyển dụng ở đáy Sidebar (Khớp mockup) */}
        <div className="p-4 mx-4 mb-6 bg-[#063830] rounded-2xl shadow-inner border border-teal-900/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#5eead4] text-[#0a5146] font-black text-base flex items-center justify-center shrink-0 shadow-sm">
              {initialLetter}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-bold text-white truncate" title={companyName}>
                {companyName}
              </div>
              <div className="text-xs text-teal-200/80 truncate" title={contactName}>
                {contactName}
              </div>
            </div>
          </div>

          {/* Nút Đăng Xuất Mint Pill */}
          <button
            onClick={handleLogout}
            className="w-full mt-3.5 py-2.5 px-4 bg-[#5eead4] hover:bg-[#4ade80] text-[#0a5146] font-extrabold text-xs tracking-wider uppercase rounded-full shadow-xs transition-all duration-200 cursor-pointer text-center block"
            title="Đăng xuất khỏi Cổng Doanh Nghiệp"
          >
            ĐĂNG XUẤT
          </button>
        </div>
      </aside>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 2. KHU VỰC CHÍNH (CONTENT PHẢI) ──                      */}
      {/* ══════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <main className="flex-1 p-8 sm:p-10 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

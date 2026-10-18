import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, Link, useNavigate } from 'react-router-dom';

/**
 * Layout chuyên biệt cho Người Lao Động / Sinh Viên (Candidate Portal)
 * - Loại bỏ 100% Sidebar xanh lá cây.
 * - Sử dụng Top Navbar nằm ngang cố định trên cùng.
 * - Header có Logo SkillGap, 3 Menu điều hướng ngang chính và Cụm Auth (Avatar hoặc Đăng nhập/Đăng ký).
 */
export default function CandidateLayout() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const raw = localStorage.getItem('current_user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  });
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('current_user');
      if (raw) setCurrentUser(JSON.parse(raw));
    } catch (e) {
      setCurrentUser(null);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    setCurrentUser(null);
    setUserDropdownOpen(false);
    navigate('/');
  };

  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center gap-2 px-4.5 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
      isActive
        ? 'bg-white text-[#042f2e] font-bold shadow-md border border-white'
        : 'text-white bg-white/10 border border-white/20 hover:bg-white/20'
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-[#094741] text-white antialiased" style={{ background: 'radial-gradient(ellipse at 50% 0%, #0d6e64 0%, #0a564e 35%, #073b36 70%, #052c28 100%)', backgroundAttachment: 'fixed', fontFamily: "'Be Vietnam Pro', system-ui, sans-serif" }}>
      {/* ══════════════════════════════════════════════════════ */}
      {/* ── TOP NAVBAR NẰM NGANG 2 DÒNG (Bỏ hoàn toàn Sidebar cũ) ── */}
      {/* ══════════════════════════════════════════════════════ */}
      <header className="sticky top-0 z-50 bg-[#083e38]/95 backdrop-blur-md border-b border-white/10 shadow-lg flex flex-col">
        {/* DÒNG 1: LOGO VÀ AUTH / TÁC VỤ */}
        <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex items-center justify-between gap-4">
          
          {/* CỤM TRÁI: LOGO "SkillGapAI" */}
          <Link to="/" className="flex items-center gap-2 text-decoration-none group">
            <span className="text-2xl font-black tracking-tight text-white">
              SkillGap<span className="text-[#5eead4]">AI</span>
            </span>
          </Link>

          {/* CỤM PHẢI: AVATAR / ĐĂNG NHẬP / VIỆC ĐÃ ỨNG TUYỂN (KHỚP ẢNH MẪU) */}
          <div className="flex items-center gap-3">
            {currentUser ? (
              <div className="flex items-center gap-2.5">
                {/* Nút VIỆC ĐÃ ỨNG TUYỂN */}
                <Link
                  to="/jobs"
                  className="px-4 py-1.5 rounded-full text-xs font-medium bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all shadow-xs"
                >
                  Việc đã ứng tuyển
                </Link>

                {/* Nút ĐĂNG TUYỂN & TÌM HỒ SƠ */}
                <Link
                  to="/employer/dashboard"
                  className="px-4 py-1.5 rounded-full text-xs font-medium bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all shadow-xs"
                >
                  Đăng tuyển &amp; tìm hồ sơ
                </Link>

                {/* USER CHIP: NGUYỄN VĂN AN (A) */}
                <div className="relative">
                  <button
                    onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                    className="flex items-center gap-2.5 py-1 px-1 pl-4 rounded-full bg-white text-[#042f2e] font-bold shadow-sm hover:shadow-md transition-all cursor-pointer"
                  >
                    <span className="text-xs font-bold text-[#042f2e] hidden sm:inline-block">
                      {currentUser.full_name || 'Nguyễn Văn An'}
                    </span>
                    <div className="w-7 h-7 rounded-full bg-[#094741] text-white font-extrabold text-xs flex items-center justify-center">
                      {(currentUser.full_name || 'A').charAt(0).toUpperCase()}
                    </div>
                  </button>

                  {/* Dropdown Menu */}
                  {userDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-2xl border border-slate-100 py-1.5 z-50 text-slate-800">
                      <div className="px-4 py-2 border-b border-slate-100">
                        <div className="text-xs font-bold text-slate-800">{currentUser.full_name || 'Nguyễn Văn An'}</div>
                        <div className="text-[11px] text-slate-400">{currentUser.email || 'sinhvien@ctu.edu.vn'}</div>
                      </div>
                      {currentUser.role === 'admin' && (
                        <Link
                          to="/admin"
                          className="block px-4 py-2 text-xs font-semibold text-teal-700 hover:bg-teal-50"
                          onClick={() => setUserDropdownOpen(false)}
                        >
                          👑 Vào Trang Quản Trị (/admin)
                        </Link>
                      )}
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 flex items-center gap-2 cursor-pointer"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Đăng xuất
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2.5">
                <Link
                  to="/jobs"
                  className="px-4 py-1.5 rounded-full text-xs font-medium bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all shadow-xs"
                >
                  Việc đã ứng tuyển
                </Link>
                <Link
                  to="/employer/dashboard"
                  className="px-4 py-1.5 rounded-full text-xs font-medium bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all shadow-xs"
                >
                  Đăng tuyển &amp; tìm hồ sơ
                </Link>
                <Link
                  to="/login"
                  className="px-4 py-1.5 rounded-full text-xs font-bold bg-white text-[#094741] hover:bg-teal-50 transition-colors shadow-xs"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-1.5 rounded-full text-xs font-bold bg-white/10 text-white border border-white/30 hover:bg-white/20 transition-colors shadow-xs"
                >
                  Đăng ký
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* DÒNG 2: CÁC MENU ĐIỀU HƯỚNG NGANG DÀNH CHO ỨNG VIÊN (7 CHỨC NĂNG CĂN GIỮA, CHIA ĐỀU) */}
        <div className="w-full border-t border-white/10 py-2 bg-black/15 flex items-center justify-center">
          <nav className="flex items-center justify-center gap-2.5 flex-wrap">
            {/* Menu 1: Tổng quan (Mặc định) */}
            <NavLink to="/" end className={navLinkClass}>
              <span>Tổng quan</span>
            </NavLink>

            {/* Menu 2: Chẩn đoán AI & Lộ trình */}
            <NavLink to="/ai-diagnosis" className={navLinkClass}>
              <span>Chẩn đoán &amp; Lộ trình</span>
            </NavLink>

            {/* Menu 3: Phân tích CV (AI) */}
            <NavLink to="/cv-upload" className={navLinkClass}>
              <span>Phân tích CV (AI)</span>
            </NavLink>

            {/* Menu 4: Việc làm */}
            <NavLink to="/jobs" className={navLinkClass}>
              <span>Việc làm</span>
            </NavLink>

            {/* Menu 5: Khám Phá Ngành Nghề */}
            <NavLink to="/explore-industries" className={navLinkClass}>
              <span>Khám phá ngành nghề</span>
            </NavLink>

            {/* Menu 6: Khóa học */}
            <NavLink to="/courses" className={navLinkClass}>
              <span>Khóa học</span>
            </NavLink>

            {/* Menu 7: Cẩm Nang Kỹ Năng Mềm */}
            <NavLink to="/soft-skills" className={navLinkClass}>
              <span>Cẩm nang kỹ năng mềm</span>
            </NavLink>
          </nav>
        </div>
      </header>

        {/* Mobile Navigation Bar */}
        <div className="md:hidden flex items-center justify-around border-t border-white/10 py-2 bg-[#083e38]/90 px-2 text-[11px] font-bold">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'text-[#5eead4]' : 'text-teal-200'}>
            Chẩn Đoán AI
          </NavLink>
          <NavLink to="/explore-industries" className={({ isActive }) => isActive ? 'text-[#5eead4]' : 'text-teal-200'}>
            Ngành Nghề
          </NavLink>
          <NavLink to="/soft-skills" className={({ isActive }) => isActive ? 'text-[#5eead4]' : 'text-teal-200'}>
            Kỹ Năng Mềm
          </NavLink>
        </div>
      </header>

      {/* ══════════════════════════════════════════════════════ */}
      {/* ── NỘI DUNG TRANG CON (Outlet) ──                    */}
      {/* ══════════════════════════════════════════════════════ */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* FOOTER THÂN THIỆN CHO ỨNG VIÊN */}
      <footer className="bg-[#052824] border-t border-white/10 py-6 text-center text-xs text-teal-200/60">
        <div className="max-w-7xl mx-auto px-4">
          © 2026 <strong className="text-teal-200">SkillGap.AI</strong> – Hệ Thống AI Phân Tích &amp; Hướng Nghiệp Kỹ Năng Lao Động TP. Cần Thơ.
        </div>
      </footer>
    </div>
  );
}

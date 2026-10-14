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
  const [currentUser, setCurrentUser] = useState(null);
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
    `inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all ${
      isActive
        ? 'bg-[#06332e] text-white border border-[#5eead4]/40 shadow-sm'
        : 'text-teal-100/80 hover:text-white hover:bg-white/5'
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-[#094741] text-white antialiased" style={{ background: 'radial-gradient(ellipse at 50% 0%, #0d6e64 0%, #0a564e 35%, #073b36 70%, #052c28 100%)', backgroundAttachment: 'fixed', fontFamily: "'Be Vietnam Pro', system-ui, sans-serif" }}>
      {/* ══════════════════════════════════════════════════════ */}
      {/* ── TOP NAVBAR NẰM NGANG (Bỏ hoàn toàn Sidebar cũ) ── */}
      {/* ══════════════════════════════════════════════════════ */}
      <header className="sticky top-0 z-50 bg-[#083e38]/95 backdrop-blur-md border-b border-white/10 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between gap-4">
          
          {/* CỤM TRÁI: LOGO "SkillGapAI" */}
          <Link to="/" className="flex items-center gap-2.5 text-decoration-none group">
            <span className="text-2xl font-black tracking-tight text-white">
              SkillGap<span className="text-[#5eead4]">AI</span>
            </span>
          </Link>

          {/* CỤM GIỮA: 3 MENU ĐIỀU HƯỚNG NGANG DÀNH CHO ỨNG VIÊN */}
          <nav className="hidden md:flex items-center gap-2">
            {/* Menu 1: Chẩn đoán AI & Lộ trình */}
            <NavLink to="/" end className={navLinkClass}>
              <span>CHẨN ĐOÁN &amp; LỘ TRÌNH</span>
            </NavLink>

            {/* Menu 2: Khám Phá Ngành Nghề */}
            <NavLink to="/explore-industries" className={navLinkClass}>
              <span>KHÁM PHÁ NGÀNH NGHỀ</span>
            </NavLink>

            {/* Menu 3: Cẩm Nang Kỹ Năng Mềm */}
            <NavLink to="/soft-skills" className={navLinkClass}>
              <span>CẨM NANG KỸ NĂNG MỀM</span>
            </NavLink>
          </nav>

          {/* CỤM PHẢI: AVATAR / ĐĂNG NHẬP / ĐĂNG TUYỂN */}
          <div className="flex items-center gap-2.5">
            {currentUser ? (
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2.5 p-1.5 pl-3 rounded-full hover:bg-white/10 transition-colors border border-white/20"
                >
                  <span className="text-xs font-bold text-teal-100 hidden sm:inline-block">
                    {currentUser.full_name || 'Người dùng'}
                  </span>
                  <div className="w-8 h-8 rounded-full bg-[#0d5f57] text-white font-bold text-sm flex items-center justify-center shadow-xs">
                    {(currentUser.full_name || 'U').charAt(0).toUpperCase()}
                  </div>
                </button>

                {/* Dropdown Menu */}
                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-2xl border border-slate-100 py-1.5 z-50 text-slate-800">
                    <div className="px-4 py-2 border-b border-slate-100">
                      <div className="text-xs font-bold text-slate-800">{currentUser.full_name}</div>
                      <div className="text-[11px] text-slate-400">{currentUser.email}</div>
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
                      className="w-full text-left px-4 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Đăng xuất
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-full text-xs font-extrabold bg-white text-[#094741] hover:bg-teal-50 transition-colors shadow-sm uppercase tracking-wide"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-full text-xs font-extrabold bg-[#06332e] hover:bg-[#042824] text-white border border-white/20 transition-colors shadow-sm uppercase tracking-wide"
                >
                  Đăng ký
                </Link>
                <Link
                  to="/employer"
                  className="hidden sm:inline-flex px-4 py-2 rounded-full text-xs font-extrabold bg-[#86efac] text-[#064e3b] hover:bg-[#6ee7b7] transition-colors shadow-sm uppercase tracking-wide"
                >
                  Đăng tuyển &amp; Tìm hồ sơ
                </Link>
              </div>
            )}
          </div>
        </div>

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

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ROLE_TABS = [
  { id: 'candidate', label: 'Ứng viên', icon: '👤', desc: 'Sinh viên & Người lao động' },
  { id: 'employer', label: 'Nhà tuyển dụng', icon: '🏢', desc: 'Doanh nghiệp & HR' },
  { id: 'provider', label: 'Trung tâm đào tạo', icon: '🎓', desc: 'Đơn vị đào tạo khóa học' }
];

export default function RegisterPage() {
  const navigate = useNavigate();

  // 1. State role mặc định là 'candidate'
  const [role, setRole] = useState('candidate');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // 2. Hàm submit gửi payload chính xác lên API
  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!fullName.trim() || !email.trim() || !password) {
      setErrorMsg('Vui lòng điền đầy đủ các thông tin bắt buộc.');
      return;
    }

    if (password.length < 6) {
      setErrorMsg('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }

    if (role === 'employer' && !companyName.trim()) {
      setErrorMsg('Vui lòng nhập tên công ty / doanh nghiệp của bạn.');
      return;
    }

    // Payload chuẩn xác theo yêu cầu kỹ thuật bắt buộc
    const payload = {
      email: email.trim(),
      password: password,
      full_name: fullName.trim(),
      role: role,
      company_name: role === 'employer' ? companyName.trim() : null
    };

    console.log('[Register] Gửi payload đăng ký:', payload);

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        setSuccessMsg('🎉 Đăng ký thành công! Đang chuyển hướng sang trang đăng nhập...');
        setTimeout(() => {
          navigate('/login', { state: { registeredEmail: email.trim() } });
        }, 1200);
      } else {
        const message = data.detail || 'Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.';
        setErrorMsg(typeof message === 'string' ? message : JSON.stringify(message));
      }
    } catch (err) {
      console.error('Registration error:', err);
      setErrorMsg('Không thể kết nối đến máy chủ API. Vui lòng kiểm tra lại kết nối mạng.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-[#08332e] via-[#0d5f57] to-[#062420] flex items-center justify-center p-4 sm:p-6 lg:p-8 font-sans">
      <div className="w-full max-w-xl bg-white rounded-3xl shadow-2xl p-6 sm:p-10 border border-teal-100">
        
        {/* Header / Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-1.5 text-2xl font-black text-[#0d5f57] tracking-tight">
            <span>SkillGap</span>
            <span className="text-[#0fa39e]">AI</span>
          </Link>
          <h1 className="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight">
            Đăng Ký Tài Khoản
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Hệ thống phân tích khoảng cách kỹ năng & kết nối việc làm thông minh
          </p>
        </div>

        {/* Thông báo lỗi & thành công */}
        {errorMsg && (
          <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-xl flex items-center gap-2">
            <span>⚠️ {errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-6 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold rounded-xl flex items-center gap-2">
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          {/* YÊU CẦU 1 & 2: 3 Tabs chọn Loại tài khoản (role) */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
              Loại tài khoản đăng ký: <span className="text-rose-500">*</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {ROLE_TABS.map((tab) => {
                const isActive = role === tab.id;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setRole(tab.id)}
                    className={`flex flex-col items-center text-center p-3.5 rounded-2xl border transition-all cursor-pointer ${
                      isActive
                        ? 'bg-[#ecfdf5] border-[#0d5f57] text-[#0d5f57] ring-2 ring-[#0d5f57]/30 shadow-xs'
                        : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100 hover:border-slate-300'
                    }`}
                  >
                    <span className="text-xl mb-1">{tab.icon}</span>
                    <span className="text-xs font-bold leading-tight">{tab.label}</span>
                    <span className="text-[10px] text-slate-400 mt-0.5 leading-tight">{tab.desc}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Họ và tên */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Họ và tên <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Ví dụ: Nguyễn Văn An"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/20 transition-all"
            />
          </div>

          {/* YÊU CẦU 3: Bắt buộc hiển thị ô input Tên công ty khi role === 'employer' */}
          {role === 'employer' && (
            <div className="p-4 bg-teal-50/70 border-2 border-teal-300 rounded-2xl animate-in fade-in duration-200">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#0d5f57] mb-1.5">
                🏢 Tên công ty / Doanh nghiệp <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                required
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Ví dụ: Công ty TNHH Phần Mềm FPT Cần Thơ"
                className="w-full px-4 py-2.5 rounded-xl border border-teal-300 bg-white text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/20 transition-all"
              />
              <p className="text-[11px] text-teal-700 mt-1">
                Tên công ty sẽ hiển thị trên tất cả các tin tuyển dụng của bạn.
              </p>
            </div>
          )}

          {/* Địa chỉ Email */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Địa chỉ Email <span className="text-rose-500">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/20 transition-all"
            />
          </div>

          {/* Mật khẩu */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Mật khẩu <span className="text-rose-500">*</span>
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Tối thiểu 6 ký tự"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/20 transition-all"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 rounded-xl font-bold text-white bg-[#0d5f57] hover:bg-[#0b4d46] active:scale-[0.99] transition-all duration-150 shadow-lg shadow-teal-900/20 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span>Đang xử lý đăng ký...</span>
              </>
            ) : (
              <span>Đăng Ký Tài Khoản</span>
            )}
          </button>
        </form>

        {/* Footer chuyển sang Login */}
        <div className="mt-6 text-center text-sm text-slate-500 border-t border-slate-100 pt-5">
          Đã có tài khoản?{' '}
          <Link to="/login" className="font-bold text-[#0d5f57] hover:underline">
            Đăng nhập ngay
          </Link>
        </div>

      </div>
    </div>
  );
}

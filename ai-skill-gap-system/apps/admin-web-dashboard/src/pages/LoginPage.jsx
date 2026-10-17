import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Nhận email nếu chuyển từ trang Register sang
  const defaultEmail = location.state?.registeredEmail || '';

  const [email, setEmail] = useState(defaultEmail);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!email.trim() || !password) {
      setErrorMsg('Vui lòng nhập đầy đủ email và mật khẩu.');
      return;
    }

    setLoading(true);

    try {
      // Backend FastAPI sử dụng OAuth2PasswordRequestForm
      // Bắt buộc gửi dạng FormData (x-www-form-urlencoded) gồm username và password
      const formData = new URLSearchParams();
      formData.append('username', email.trim());
      formData.append('password', password);

      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        // 1. Lưu Token
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
        }

        // 2. Làm sạch data trước khi lưu vào localStorage (loại bỏ tiền tố Python Enum)
        const safeRole = String(data?.user?.role || 'candidate').toLowerCase().trim().replace('userrole.', '');
        const safeUser = { ...data.user, role: safeRole };
        localStorage.setItem('current_user', JSON.stringify(safeUser));

        // 3. Logic chuyển hướng dựa trên safeRole
        if (safeRole === 'admin') {
          navigate('/admin/dashboard', { replace: true });
        } else if (safeRole === 'employer') {
          navigate('/employer/dashboard', { replace: true });
        } else if (safeRole === 'provider') {
          navigate('/provider/gap-analytics', { replace: true });
        } else {
          navigate('/', { replace: true });
        }
      } else {
        // Xử lý thông báo lỗi (ví dụ 401: Sai mật khẩu / email)
        if (res.status === 401) {
          setErrorMsg('Email hoặc mật khẩu không chính xác. Vui lòng thử lại!');
        } else if (res.status === 422) {
          setErrorMsg('Định dạng tài khoản hoặc mật khẩu không hợp lệ.');
        } else {
          const detail = data.detail || 'Đăng nhập không thành công. Vui lòng thử lại sau.';
          setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
        }
      }
    } catch (err) {
      console.error('Login error:', err);
      setErrorMsg('Không thể kết nối đến máy chủ xác thực. Vui lòng kiểm tra kết nối API backend.');
    } finally {
      setLoading(false);
    }
  };

  // Hỗ trợ đăng nhập nhanh Demo (Quick Fill Test)
  const quickFill = (testEmail, testRole) => {
    setEmail(testEmail);
    setPassword('admin123');
    setErrorMsg('');
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-[#08332e] via-[#0d5f57] to-[#062420] flex items-center justify-center p-4 sm:p-6 lg:p-8 font-sans">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-6 sm:p-10 border border-teal-100">

        {/* Header / Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-1.5 text-2xl font-black text-[#0d5f57] tracking-tight">
            <span>SkillGap</span>
            <span className="text-[#0fa39e]">AI</span>
          </Link>
          <h1 className="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight">
            Chào mừng trở lại
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Đăng nhập để quản lý lộ trình học & kết nối việc làm
          </p>
        </div>

        {/* Thông báo lỗi */}
        {errorMsg && (
          <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-xl flex items-center gap-2">
            <svg className="w-5 h-5 shrink-0 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          {/* Email / Username */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Email đăng nhập <span className="text-rose-500">*</span>
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/15 transition-all"
            />
          </div>

          {/* Password */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">
                Mật khẩu <span className="text-rose-500">*</span>
              </label>
              <a href="#forgot" onClick={(e) => { e.preventDefault(); alert('Vui lòng liên hệ quản trị viên để đặt lại mật khẩu.'); }} className="text-xs text-[#0f766e] hover:underline font-semibold">
                Quên mật khẩu?
              </a>
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu của bạn"
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-slate-800 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-3 focus:ring-[#0d5f57]/15 transition-all"
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
                <span>Đang kiểm tra thông tin...</span>
              </>
            ) : (
              <span>Đăng Nhập</span>
            )}
          </button>
        </form>

        {/* Demo Fast Login Pills */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 text-center mb-2.5">
            Điền nhanh tài khoản thử nghiệm:
          </p>
          <div className="flex flex-wrap gap-1.5 justify-center">
            <button
              type="button"
              onClick={() => quickFill('admin@skillgap.com', 'admin')}
              className="text-xs px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors cursor-pointer"
            >
              👑 Admin
            </button>
            <button
              type="button"
              onClick={() => quickFill('employer@skillgap.com', 'employer')}
              className="text-xs px-2.5 py-1 bg-teal-50 hover:bg-teal-100 text-teal-800 font-semibold rounded-lg transition-colors cursor-pointer"
            >
              🏢 Doanh nghiệp
            </button>
            <button
              type="button"
              onClick={() => quickFill('provider@skillgap.com', 'provider')}
              className="text-xs px-2.5 py-1 bg-purple-50 hover:bg-purple-100 text-purple-800 font-semibold rounded-lg transition-colors cursor-pointer"
            >
              🎓 Đào tạo
            </button>
            <button
              type="button"
              onClick={() => quickFill('candidate@skillgap.com', 'candidate')}
              className="text-xs px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold rounded-lg transition-colors cursor-pointer"
            >
              👤 Ứng viên
            </button>
          </div>
        </div>

        {/* Footer / Switch to Register */}
        <div className="mt-6 text-center text-sm text-slate-500 border-t border-slate-100 pt-5">
          Chưa có tài khoản?{' '}
          <Link to="/register" className="font-bold text-[#0f766e] hover:text-[#0d5f57] hover:underline">
            Đăng ký ngay
          </Link>
        </div>

      </div>
    </div>
  );
}

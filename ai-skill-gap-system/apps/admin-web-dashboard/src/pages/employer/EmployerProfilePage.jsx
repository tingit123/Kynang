import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EmployerProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Form states
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [companyLogoUrl, setCompanyLogoUrl] = useState('');
  const [companyDescription, setCompanyDescription] = useState('');

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  // 1. Tải thông tin hồ sơ hiện tại
  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setErrorMsg('');
      try {
        const res = await fetch(`${API_BASE}/api/auth/me`, {
          headers: getAuthHeaders()
        });

        if (res.ok) {
          const user = await res.json();
          setFullName(user.full_name || '');
          setEmail(user.email || '');
          setCompanyName(user.company_name || '');
          setCompanyLogoUrl(user.company_logo_url || '');
          setCompanyDescription(user.company_description || '');
        } else {
          // Fallback to localStorage if API unavailable
          const raw = localStorage.getItem('current_user');
          if (raw) {
            const u = JSON.parse(raw);
            setFullName(u.full_name || '');
            setEmail(u.email || '');
            setCompanyName(u.company_name || '');
          }
        }
      } catch (err) {
        console.error(err);
        const raw = localStorage.getItem('current_user');
        if (raw) {
          const u = JSON.parse(raw);
          setFullName(u.full_name || '');
          setEmail(u.email || '');
          setCompanyName(u.company_name || '');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // 2. Cập nhật thông tin hồ sơ
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    setErrorMsg('');

    const payload = {
      full_name: fullName.trim(),
      company_name: companyName.trim(),
      company_logo_url: companyLogoUrl.trim() || null,
      company_description: companyDescription.trim() || null
    };

    try {
      const res = await fetch(`${API_BASE}/api/auth/profile`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const updated = await res.json();
        setSuccessMsg('🎉 Cập nhật hồ sơ doanh nghiệp thành công!');
        // Đồng bộ lại vào localStorage
        try {
          const old = JSON.parse(localStorage.getItem('current_user') || '{}');
          const merged = { ...old, ...payload, ...(updated.user || updated) };
          localStorage.setItem('current_user', JSON.stringify(merged));
        } catch (e) {}
        setTimeout(() => setSuccessMsg(''), 4000);
      } else {
        const err = await res.json().catch(() => ({}));
        setErrorMsg(err.detail || 'Không thể cập nhật hồ sơ doanh nghiệp.');
      }
    } catch (err) {
      console.error(err);
      setErrorMsg('Lỗi kết nối máy chủ khi lưu hồ sơ.');
    } finally {
      setSaving(false);
    }
  };

  const initialLetter = (companyName || fullName || 'D').charAt(0).toUpperCase();

  if (loading) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200/80">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
        <p className="text-sm font-medium text-slate-500">Đang tải hồ sơ doanh nghiệp...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <h1 className="text-xl sm:text-2xl font-black text-slate-800 flex items-center gap-2">
          <span>🏛️</span> Hồ Sơ Doanh Nghiệp
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Quản lý thương hiệu tuyển dụng, thông tin công ty và thông điệp gửi tới ứng viên tiềm năng
        </p>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold rounded-xl flex items-center gap-2 animate-in fade-in">
          <span>{successMsg}</span>
        </div>
      )}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-xl flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 2-Column Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        {/* CỘT TRÁI: Profile Card Preview */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col items-center text-center">
          {/* Logo / Avatar */}
          <div className="relative mb-4">
            {companyLogoUrl ? (
              <img
                src={companyLogoUrl}
                alt={companyName || 'Logo'}
                className="w-24 h-24 rounded-2xl object-cover border-2 border-sky-100 shadow-md"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            ) : (
              <div className="w-24 h-24 rounded-2xl bg-linear-to-br from-[#0284c7] to-[#0369a1] text-white font-black text-3xl flex items-center justify-center shadow-md">
                {initialLetter}
              </div>
            )}
          </div>

          <h2 className="text-lg font-black text-slate-800">
            {companyName || 'Tên doanh nghiệp'}
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-1">
            {email || 'Chưa có email'}
          </p>

          <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-50 text-sky-700 border border-sky-200">
            🏢 Tài khoản Doanh nghiệp
          </div>

          <div className="mt-6 pt-5 border-t border-slate-100 w-full text-left space-y-3 text-xs text-slate-600">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-semibold">Người đại diện:</span>
              <span className="font-bold text-slate-700">{fullName || 'Chưa cập nhật'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-semibold">Trạng thái xác minh:</span>
              <span className="font-bold text-emerald-600">✓ Đã kích hoạt</span>
            </div>
          </div>
        </div>

        {/* CỘT PHẢI: Form Chỉnh Sửa */}
        <div className="lg:col-span-2 bg-white p-6 sm:p-8 rounded-2xl border border-slate-200/80 shadow-xs">
          <h2 className="text-base font-extrabold text-slate-800 pb-3 border-b border-slate-100 mb-6">
            Thông tin chi tiết & Nhận diện công ty
          </h2>

          <form onSubmit={handleSaveProfile} className="space-y-5">
            {/* Tên người đại diện & Email */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Họ và tên người đại diện / HR <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ví dụ: Nguyễn Trọng Tín"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Email tài khoản (Không thể thay đổi)
                </label>
                <input
                  type="email"
                  disabled
                  value={email}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 text-sm cursor-not-allowed"
                />
              </div>
            </div>

            {/* Tên công ty & Link Logo */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Tên công ty / Doanh nghiệp <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Ví dụ: FPT Software Cần Thơ"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Đường dẫn Logo (URL)
                </label>
                <input
                  type="url"
                  value={companyLogoUrl}
                  onChange={(e) => setCompanyLogoUrl(e.target.value)}
                  placeholder="https://example.com/logo.png"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                />
              </div>
            </div>

            {/* Giới thiệu công ty */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Giới thiệu về doanh nghiệp & Văn hóa làm việc
              </label>
              <textarea
                rows={5}
                value={companyDescription}
                onChange={(e) => setCompanyDescription(e.target.value)}
                placeholder="Mô tả lĩnh vực hoạt động, quy mô công ty, môi trường làm việc, công nghệ áp dụng..."
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
              />
            </div>

            {/* Submit */}
            <div className="pt-4 border-t border-slate-100 flex items-center justify-end">
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white text-sm font-bold shadow-md shadow-sky-600/20 active:scale-95 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-60"
              >
                {saving ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    <span>Đang lưu thông tin...</span>
                  </>
                ) : (
                  <span>💾 Lưu Thay Đổi</span>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

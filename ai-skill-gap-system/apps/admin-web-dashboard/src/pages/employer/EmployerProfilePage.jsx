import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EmployerProfilePage() {
  const [representative, setRepresentative] = useState('Nguyễn Minh Khoa');
  const [companyName, setCompanyName] = useState('Mekong Tech');
  const [logoUrl, setLogoUrl] = useState('https://mekongtech.vn/logo.png');
  const [description, setDescription] = useState(
    'Mekong Tech là công ty phần mềm tại Cần Thơ, hơn 80 kỹ sư, tập trung xây dựng sản phẩm cho thị trường ĐBSCL. Chúng tôi coi trọng đào tạo nội bộ và lộ trình thăng tiến rõ ràng.'
  );

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Load from current_user in localStorage if available
  useEffect(() => {
    try {
      const raw = localStorage.getItem('current_user');
      if (raw) {
        const u = JSON.parse(raw);
        if (u.full_name) setRepresentative(u.full_name);
        if (u.company_name) setCompanyName(u.company_name);
        if (u.company_logo_url) setLogoUrl(u.company_logo_url);
        if (u.company_description) setDescription(u.company_description);
      }
    } catch (e) {}
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!companyName.trim()) {
      alert('Vui lòng nhập tên doanh nghiệp!');
      return;
    }

    setSaving(true);
    setMessage('');

    const payload = {
      full_name: representative.trim(),
      company_name: companyName.trim(),
      company_logo_url: logoUrl.trim() || null,
      company_description: description.trim() || null
    };

    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      if (token) {
        await fetch(`${API_BASE}/api/auth/profile`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });
      }
    } catch (err) {
      console.warn('API update profile warning:', err);
    }

    try {
      const old = JSON.parse(localStorage.getItem('current_user') || '{}');
      const merged = { ...old, ...payload };
      localStorage.setItem('current_user', JSON.stringify(merged));
    } catch (e) {}

    setSaving(false);
    setMessage('Đã lưu thay đổi hồ sơ công ty thành công!');
    setTimeout(() => setMessage(''), 3500);
  };

  const initialLetter = (companyName.trim() || 'M').charAt(0).toUpperCase();

  return (
    <div className="space-y-6 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Hồ sơ công ty
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Thương hiệu tuyển dụng này hiển thị đồng bộ trên mọi tin của công ty.
        </p>
      </div>

      {message && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-bold rounded-2xl">
          {message}
        </div>
      )}

      {/* ── 2. BỐ CỤC 2 CỘT (FORM TRÁI & XEM TRƯỚC PHẢI) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
        {/* CỘT TRÁI: FORM CẬP NHẬT HỒ SƠ (7 COLS) */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200/90 p-8 shadow-xs">
          <h2 className="text-base font-extrabold text-slate-900 mb-6">
            Thông tin thương hiệu tuyển dụng
          </h2>

          <form onSubmit={handleSave} className="space-y-5">
            {/* Tên người đại diện */}
            <div>
              <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-2">
                TÊN NGƯỜI ĐẠI DIỆN
              </label>
              <input
                type="text"
                value={representative}
                onChange={(e) => setRepresentative(e.target.value)}
                required
                className="w-full px-5 py-3 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57] transition-colors"
                placeholder="Nguyễn Minh Khoa"
              />
            </div>

            {/* Tên doanh nghiệp */}
            <div>
              <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-2">
                TÊN DOANH NGHIỆP
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
                className="w-full px-5 py-3 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57] transition-colors"
                placeholder="Mekong Tech"
              />
            </div>

            {/* Đường dẫn logo */}
            <div>
              <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-2">
                ĐƯỜNG DẪN LOGO
              </label>
              <input
                type="text"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
                className="w-full px-5 py-3 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57] transition-colors"
                placeholder="https://mekongtech.vn/logo.png"
              />
            </div>

            {/* Giới thiệu văn hóa & môi trường làm việc */}
            <div>
              <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-2">
                GIỚI THIỆU VĂN HÓA VÀ MÔI TRƯỜNG LÀM VIỆC
              </label>
              <textarea
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-5 py-3.5 rounded-2xl border border-slate-300 text-sm font-medium text-slate-800 focus:outline-none focus:border-[#0d5f57] transition-colors resize-none leading-relaxed"
                placeholder="Mô tả văn hóa công ty, chế độ đãi ngộ..."
              />
            </div>

            {/* Nút Submit */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={saving}
                className="px-8 py-3.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white text-xs font-black uppercase tracking-wider transition-all shadow-md shadow-teal-900/10 cursor-pointer disabled:opacity-50"
              >
                {saving ? 'ĐANG LƯU...' : 'LƯU THAY ĐỔI'}
              </button>
            </div>
          </form>
        </div>

        {/* CỘT PHẢI: XEM TRƯỚC (5 COLS) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <div className="text-[11px] font-black uppercase text-[#0d5f57] tracking-wider">
            XEM TRƯỚC
          </div>
          <h2 className="text-base font-extrabold text-slate-900 mt-1 mb-5">
            Ứng viên sẽ thấy trên mỗi tin tuyển dụng
          </h2>

          <div className="space-y-4">
            {/* Box 1: Company Profile Snapshot */}
            <div className="bg-[#f8fafc] rounded-2xl border border-slate-100 p-5">
              <div className="flex items-center gap-3.5">
                <div className="w-12 h-12 rounded-xl bg-[#0d9488] text-white font-black text-xl flex items-center justify-center shrink-0 shadow-xs">
                  {initialLetter}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-base font-extrabold text-slate-900 truncate">
                    {companyName || 'Mekong Tech'}
                  </div>
                  <div className="text-xs text-slate-500 font-medium mt-0.5 truncate">
                    Người đại diện: {representative || 'Nguyễn Minh Khoa'}
                  </div>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed font-normal mt-3.5 line-clamp-3">
                {description ||
                  'Mekong Tech là công ty phần mềm tại Cần Thơ, hơn 80 kỹ sư, tập trung xây dựng sản phẩm cho thị trường ĐBSCL...'}
              </p>
            </div>

            {/* Box 2: Sample Job Card Preview */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4.5 flex items-center justify-between gap-3 shadow-2xs">
              <div className="min-w-0 flex-1">
                <div className="text-sm font-extrabold text-slate-900 truncate">
                  Python Backend Developer
                </div>
                <div className="text-xs text-slate-500 font-medium mt-0.5 truncate">
                  {companyName || 'Mekong Tech'} · Cần Thơ · 15–25 triệu
                </div>
              </div>
              <div className="shrink-0">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#dcfce7] text-[#0f766e]">
                  Đang tuyển
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

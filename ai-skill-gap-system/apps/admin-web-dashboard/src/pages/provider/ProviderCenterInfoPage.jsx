import React, { useState } from 'react';

export default function ProviderCenterInfoPage() {
  const [logoUrl, setLogoUrl] = useState('https://mekongskills.vn/logo.png');
  const [centerName, setCenterName] = useState('Mekong Skills');
  const [about, setAbout] = useState(
    'Mekong Skills là trung tâm đào tạo kỹ năng nghề tại Cần Thơ, tập trung vào lập trình, phân tích dữ liệu và ngoại ngữ cho sinh viên và người đi làm khu vực ĐBSCL.'
  );
  const [savedMsg, setSavedMsg] = useState('');

  const initialLetter = (centerName.trim().charAt(0) || 'M').toUpperCase();

  const handleSave = () => {
    setSavedMsg('Đã lưu thông tin trung tâm thành công!');
    setTimeout(() => setSavedMsg(''), 3000);
  };

  const handleCancel = () => {
    setCenterName('Mekong Skills');
    setLogoUrl('https://mekongskills.vn/logo.png');
    setAbout(
      'Mekong Skills là trung tâm đào tạo kỹ năng nghề tại Cần Thơ, tập trung vào lập trình, phân tích dữ liệu và ngoại ngữ cho sinh viên và người đi làm khu vực ĐBSCL.'
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Thông tin trung tâm</h1>
        <p className="text-sm text-slate-500 mt-1">
          Logo, tên và phần giới thiệu hiển thị cho ứng viên trên các khóa học của bạn.
        </p>
      </div>

      {savedMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-xs font-bold">
          {savedMsg}
        </div>
      )}

      {/* 2 Columns: Edit Form & Live Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200 p-8 shadow-xs space-y-6">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Thông tin trung tâm</h2>
            <p className="text-xs text-slate-500 mt-0.5">Hiển thị trên mọi khóa học bạn đăng.</p>
          </div>

          {/* Logo URL */}
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#0d9488] text-white flex items-center justify-center font-black text-xl shrink-0 shadow-sm">
              {initialLetter}
            </div>
            <div className="flex-1">
              <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
                ĐƯỜNG DẪN LOGO
              </label>
              <input
                type="text"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
                placeholder="https://..."
                className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146]"
              />
              <span className="block text-[11px] text-slate-400 mt-1">
                Ảnh vuông, tối thiểu 256 × 256 px. Để trống thì dùng chữ cái đầu của tên trung tâm.
              </span>
            </div>
          </div>

          {/* Center Name */}
          <div>
            <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
              TÊN TRUNG TÂM
            </label>
            <input
              type="text"
              value={centerName}
              onChange={(e) => setCenterName(e.target.value)}
              placeholder="VD: Mekong Skills"
              className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
          </div>

          {/* About */}
          <div>
            <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
              GIỚI THIỆU TRUNG TÂM
            </label>
            <textarea
              rows={5}
              maxLength={500}
              value={about}
              onChange={(e) => setAbout(e.target.value)}
              className="w-full p-4 rounded-2xl border border-slate-300 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146] resize-none leading-relaxed"
            />
            <div className="text-right text-[11px] text-slate-400 mt-1">
              {about.length} / 500 ký tự
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleCancel}
              className="px-6 py-2.5 rounded-full border border-slate-300 text-xs font-extrabold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              HỦY THAY ĐỔI
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-8 py-2.5 rounded-full bg-[#0a5146] text-white text-xs font-extrabold hover:bg-[#073d35] transition-colors shadow-sm"
            >
              LƯU THAY ĐỔI
            </button>
          </div>
        </div>

        {/* Right Column: Live Preview & Stats */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs">
            <span className="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">
              XEM TRƯỚC
            </span>
            <h3 className="text-base font-extrabold text-slate-900 mb-4">Ứng viên sẽ thấy thế này</h3>

            {/* Live card */}
            <div className="bg-[#e6f7f5] rounded-2xl p-5 border border-emerald-200">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-extrabold bg-white text-[#0a5146] mb-3">
                Python
              </span>
              <div className="flex items-center gap-2.5 mb-2">
                <div className="w-8 h-8 rounded-lg bg-[#0d9488] text-white font-black text-sm flex items-center justify-center shrink-0">
                  {initialLetter}
                </div>
                <span className="text-xs font-extrabold text-slate-800">{centerName || 'Mekong Skills'}</span>
              </div>
              <h4 className="text-sm font-black text-slate-900 mb-2">Python Backend thực chiến</h4>
              <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                {about || 'Mekong Skills là trung tâm đào tạo kỹ năng nghề tại Cần Thơ...'}
              </p>
            </div>
          </div>

          {/* KPI Stats */}
          <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs flex items-center justify-around text-center">
            <div>
              <span className="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                ĐANG PHÂN PHỐI
              </span>
              <div className="text-3xl font-black text-[#0a5146] mt-1">4</div>
              <span className="text-xs font-medium text-slate-500">khóa học</span>
            </div>
            <div className="w-px h-12 bg-slate-100"></div>
            <div>
              <span className="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                TỔNG LƯỢT CLICK
              </span>
              <div className="text-3xl font-black text-[#0d9488] mt-1">359</div>
              <span className="text-xs font-medium text-slate-500">từ gợi ý của AI</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

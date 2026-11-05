import React, { useState } from 'react';

export default function ProviderProfilePage() {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('current_user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  });

  const [fullName, setFullName] = useState(user?.full_name || 'Trần Thanh Hải');
  const [email, setEmail] = useState(user?.email || 'hai.tran@mekongskills.vn');
  const [phone, setPhone] = useState(user?.phone || '0901 234 567');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [feedback, setFeedback] = useState({ text: '', isError: false });

  const initialLetter = (fullName.trim().charAt(0) || 'M').toUpperCase();

  const handleSave = () => {
    if (newPassword) {
      if (newPassword.length < 6) {
        setFeedback({ text: 'Mật khẩu mới phải có tối thiểu 6 ký tự!', isError: true });
        return;
      }
      if (newPassword !== confirmPassword) {
        setFeedback({ text: 'Xác nhận mật khẩu mới không khớp!', isError: true });
        return;
      }
      if (!currentPassword) {
        setFeedback({ text: 'Vui lòng nhập mật khẩu hiện tại để đổi mật khẩu!', isError: true });
        return;
      }
    }

    const updatedUser = {
      ...(user || {}),
      full_name: fullName,
      email,
      phone
    };
    try {
      localStorage.setItem('current_user', JSON.stringify(updatedUser));
      setUser(updatedUser);
    } catch (e) {}

    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setFeedback({ text: 'Lưu thông tin hồ sơ cá nhân thành công!', isError: false });
    setTimeout(() => setFeedback({ text: '', isError: false }), 3000);
  };

  const handleCancel = () => {
    setFullName(user?.full_name || 'Trần Thanh Hải');
    setEmail(user?.email || 'hai.tran@mekongskills.vn');
    setPhone(user?.phone || '0901 234 567');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setFeedback({ text: '', isError: false });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Hồ sơ cá nhân</h1>
        <p className="text-sm text-slate-500 mt-1">
          Tên người đại diện, email và mật khẩu tài khoản đơn vị đào tạo.
        </p>
      </div>

      {feedback.text && (
        <div
          className={`p-4 rounded-2xl text-xs font-bold ${
            feedback.isError
              ? 'bg-rose-50 border border-rose-200 text-rose-800'
              : 'bg-emerald-50 border border-emerald-200 text-emerald-800'
          }`}
        >
          {feedback.text}
        </div>
      )}

      {/* 2 Columns: Representative Profile & Summary Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200 p-8 shadow-xs space-y-6">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Người đại diện đơn vị</h2>
            <p className="text-xs text-slate-500 mt-0.5">Thông tin liên hệ trực tiếp cho đối tác và học viên.</p>
          </div>

          <div>
            <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
              TÊN NGƯỜI ĐẠI DIỆN
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="VD: Trần Thanh Hải"
              className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
              EMAIL ĐĂNG NHẬP
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
              SỐ ĐIỆN THOẠI
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="VD: 0901 234 567"
              className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
          </div>

          <div className="pt-4 border-t border-slate-100 space-y-4">
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">Đổi mật khẩu</h3>
              <p className="text-xs text-slate-500">Bỏ trống các ô mật khẩu bên dưới nếu không muốn đổi.</p>
            </div>

            <div>
              <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
                MẬT KHẨU HIỆN TẠI
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Nhập mật khẩu cũ..."
                className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146]"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
                  MẬT KHẨU MỚI
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Tối thiểu 6 ký tự..."
                  className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146]"
                />
              </div>
              <div>
                <label className="block text-[11px] font-extrabold text-slate-500 uppercase tracking-wider mb-1.5">
                  XÁC NHẬN MẬT KHẨU
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Nhập lại mật khẩu mới..."
                  className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146]"
                />
              </div>
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

        {/* Right Column: Account Summary Card */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-6">
          <span className="block text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
            TÀI KHOẢN ĐẠI DIỆN
          </span>

          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#0a5146] text-[#5eead4] flex items-center justify-center font-black text-2xl shrink-0 shadow-sm">
              {initialLetter}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-base font-extrabold text-slate-900 truncate">{fullName}</h3>
              <p className="text-xs text-slate-500 truncate">{email}</p>
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-slate-100 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Vai trò:</span>
              <span className="font-extrabold text-[#0a5146] bg-teal-50 px-3 py-1 rounded-full">
                🎓 Đơn vị đào tạo
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Đơn vị:</span>
              <span className="font-bold text-slate-800">{user?.organization || 'Mekong Skills'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Trạng thái:</span>
              <span className="font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full">
                ✓ Đã xác thực
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

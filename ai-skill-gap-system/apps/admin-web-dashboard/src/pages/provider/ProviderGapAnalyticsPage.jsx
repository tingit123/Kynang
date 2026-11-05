import React, { useState } from 'react';

const ALL_SKILLS_DATA = [
  {
    id: 1,
    name: 'Python',
    industry: 'IT',
    industryLabel: 'IT',
    demand: 92,
    supply: 32,
    gap: 60,
    barColor: '#be123c' // Crimson / Red for high gap
  },
  {
    id: 2,
    name: 'Data Analysis',
    industry: 'IT',
    industryLabel: 'IT',
    demand: 68,
    supply: 24,
    gap: 44,
    barColor: '#be123c'
  },
  {
    id: 3,
    name: 'Machine Learning',
    industry: 'IT',
    industryLabel: 'IT',
    demand: 55,
    supply: 12,
    gap: 43,
    barColor: '#be123c'
  },
  {
    id: 4,
    name: 'English',
    industry: 'all',
    industryLabel: 'Tất cả',
    demand: 76.6,
    supply: 42,
    gap: 34.6,
    barColor: '#d97706' // Amber / Orange for medium gap
  },
  {
    id: 5,
    name: 'AI Ethics',
    industry: 'IT',
    industryLabel: 'IT',
    demand: 38,
    supply: 8,
    gap: 30,
    barColor: '#d97706'
  },
  {
    id: 6,
    name: 'Logistics',
    industry: 'logistics',
    industryLabel: 'Logistics',
    demand: 45,
    supply: 28,
    gap: 17,
    barColor: '#0d9488' // Teal / Green for lower gap
  },
  {
    id: 7,
    name: 'Communication',
    industry: 'all',
    industryLabel: 'Tất cả',
    demand: 35.3,
    supply: 18.3,
    gap: 17,
    barColor: '#0d9488'
  },
  {
    id: 8,
    name: 'Digital Marketing',
    industry: 'economics',
    industryLabel: 'Kinh tế',
    demand: 42.7,
    supply: 26.7,
    gap: 16,
    barColor: '#0d9488'
  },
  {
    id: 9,
    name: 'Problem Solving',
    industry: 'all',
    industryLabel: 'Tất cả',
    demand: 38.1,
    supply: 22.8,
    gap: 15.3,
    barColor: '#0d9488'
  },
  {
    id: 10,
    name: 'Customer Service',
    industry: 'tourism',
    industryLabel: 'Du lịch',
    demand: 30,
    supply: 20,
    gap: 10,
    barColor: '#0d9488'
  }
];

export default function ProviderGapAnalyticsPage() {
  const [selectedIndustry, setSelectedIndustry] = useState('all');
  const [modalSkill, setModalSkill] = useState(null);
  const [courseForm, setCourseForm] = useState({
    title: '',
    duration: '4 tuần',
    price: '299.000đ',
    url: ''
  });
  const [successToast, setSuccessToast] = useState('');

  // Filter skills based on selected industry
  const filteredSkills = ALL_SKILLS_DATA.filter((s) => {
    if (selectedIndustry === 'all') return true;
    return s.industry === selectedIndustry || s.industry === 'all';
  });

  const handleOpenModal = (skill) => {
    setModalSkill(skill);
    setCourseForm({
      title: `Khóa học bồi dưỡng chuyên sâu ${skill.name}`,
      duration: '4 tuần (Online)',
      price: '299.000đ',
      url: 'https://training.ctu.edu.vn/'
    });
  };

  const handleCreateCourse = (e) => {
    e.preventDefault();
    setSuccessToast(`Đã tạo khóa học bù đắp cho kỹ năng [${modalSkill.name}] thành công! AI sẽ ưu tiên đề xuất khóa này.`);
    setModalSkill(null);
    setTimeout(() => setSuccessToast(''), 4500);
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Phân tích kỹ năng thiếu hụt
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Biết sinh viên đang yếu kỹ năng nào nhất để thiết kế khóa học trúng đích.
        </p>
      </div>

      {successToast && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-bold rounded-2xl animate-in fade-in">
          {successToast}
        </div>
      )}

      {/* ── 2. BỘ LỌC NGÀNH NGHỀ (FILTER ROW) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider shrink-0">
          NGÀNH NGHỀ
        </label>
        <div className="flex items-center gap-3">
          <select
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
            className="px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0d5f57] shadow-2xs min-w-[200px] cursor-pointer"
          >
            <option value="all">Tất cả</option>
            <option value="IT">IT &amp; Công nghệ</option>
            <option value="tourism">Du lịch &amp; Khách sạn</option>
            <option value="logistics">Logistics &amp; XNK</option>
            <option value="economics">Kinh tế &amp; Tài chính</option>
          </select>
          <span className="text-xs text-slate-500 font-medium hidden sm:inline">
            Có thể chọn: IT, Du lịch, Logistics, Kinh tế
          </span>
        </div>
      </div>

      {/* ── 3. BANNER GỢI Ý TỪ AI ── */}
      <div className="bg-[#e6f7f5] border border-[#99f6e4] rounded-2xl p-4.5 sm:px-6 sm:py-4 shadow-2xs">
        <div className="text-sm text-slate-800 leading-relaxed font-normal">
          <strong className="font-extrabold text-[#0d5f57]">Gợi ý:</strong> Hãy ưu tiên xây dựng khóa học cho Top 3 kỹ năng thiếu hụt trên để được AI hệ thống ưu tiên đề xuất cho 100% ứng viên.
        </div>
      </div>

      {/* ── 4. BẢNG XẾP HẠNG KỸ NĂNG THIẾU HỤT (MAIN CARD) ── */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 mb-2 gap-2">
          <h2 className="text-base font-extrabold text-slate-900">
            Bảng xếp hạng kỹ năng thiếu hụt
          </h2>
          <span className="text-xs text-slate-400 font-medium">
            Xếp theo gap giảm dần · Gap = Nhu cầu - Cung
          </span>
        </div>

        {/* Table view */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-[11px] font-black text-slate-400 uppercase tracking-wider border-b border-slate-100">
                <th className="pb-3.5 pl-2 w-12">#</th>
                <th className="pb-3.5 pr-4">KỸ NĂNG</th>
                <th className="pb-3.5 px-4 w-28">NHU CẦU</th>
                <th className="pb-3.5 px-4 w-28">CUNG</th>
                <th className="pb-3.5 px-4 w-64">THIẾU HỤT (GAP)</th>
                <th className="pb-3.5 pr-2 text-right"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100/80 text-sm">
              {filteredSkills.map((item, idx) => {
                const rank = idx + 1;
                const isTop3 = rank <= 3;

                return (
                  <tr key={item.id} className="hover:bg-slate-50/60 transition-colors">
                    {/* # Rank */}
                    <td className="py-4 pl-2 font-bold text-slate-600">
                      {isTop3 ? (
                        <div className="w-8 h-8 rounded-full bg-[#0d5f57] text-white font-extrabold text-xs flex items-center justify-center shadow-2xs">
                          {rank}
                        </div>
                      ) : (
                        <div className="w-8 h-8 flex items-center justify-center font-bold text-slate-600 text-sm">
                          {rank}
                        </div>
                      )}
                    </td>

                    {/* Kỹ năng */}
                    <td className="py-4 pr-4">
                      <div className="font-extrabold text-slate-900 text-sm">
                        {item.name}
                      </div>
                      <div className="text-xs text-slate-400 font-medium mt-0.5">
                        {item.industryLabel}
                      </div>
                    </td>

                    {/* Nhu cầu */}
                    <td className="py-4 px-4 font-semibold text-slate-700 text-sm">
                      {item.demand}%
                    </td>

                    {/* Cung */}
                    <td className="py-4 px-4 font-semibold text-slate-700 text-sm">
                      {item.supply}%
                    </td>

                    {/* Thiếu hụt (Gap) */}
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden max-w-[140px]">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${Math.min(100, item.gap * 1.5)}%`,
                              backgroundColor: item.barColor
                            }}
                          />
                        </div>
                        <span className="font-extrabold text-slate-800 text-xs w-10">
                          {item.gap}%
                        </span>
                      </div>
                    </td>

                    {/* Action Button */}
                    <td className="py-4 pr-2 text-right">
                      <button
                        onClick={() => handleOpenModal(item)}
                        className="px-4 py-1.5 rounded-full border border-[#0d5f57] hover:bg-[#0d5f57] text-[#0d5f57] hover:text-white text-xs font-bold transition-all shadow-2xs cursor-pointer whitespace-nowrap"
                      >
                        + Tạo khóa học bù đắp
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── MODAL TẠO KHÓA HỌC BÙ ĐẮP ── */}
      {modalSkill && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4">
          <div className="bg-white rounded-3xl p-7 max-w-lg w-full shadow-2xl border border-slate-200 animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
              <div>
                <span className="text-[11px] font-black uppercase text-[#0d5f57] tracking-wider">
                  THIẾT KẾ KHÓA HỌC BÙ ĐẮP
                </span>
                <h3 className="text-lg font-black text-slate-900 mt-0.5">
                  Khóa học kỹ năng {modalSkill.name}
                </h3>
              </div>
              <button
                onClick={() => setModalSkill(null)}
                className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateCourse} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Tên khóa học
                </label>
                <input
                  type="text"
                  value={courseForm.title}
                  onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })}
                  required
                  className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Thời lượng
                  </label>
                  <input
                    type="text"
                    value={courseForm.duration}
                    onChange={(e) => setCourseForm({ ...courseForm, duration: e.target.value })}
                    required
                    className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Học phí
                  </label>
                  <input
                    type="text"
                    value={courseForm.price}
                    onChange={(e) => setCourseForm({ ...courseForm, price: e.target.value })}
                    required
                    className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Đường dẫn đăng ký / Khóa học
                </label>
                <input
                  type="url"
                  value={courseForm.url}
                  onChange={(e) => setCourseForm({ ...courseForm, url: e.target.value })}
                  required
                  className="w-full px-4 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                />
              </div>

              <div className="pt-3 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setModalSkill(null)}
                  className="px-5 py-2.5 rounded-full border border-slate-200 text-slate-600 font-bold text-xs hover:bg-slate-100 cursor-pointer"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-extrabold text-xs uppercase tracking-wider shadow-md shadow-teal-900/20 cursor-pointer"
                >
                  Xác nhận &amp; Đẩy lên AI
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

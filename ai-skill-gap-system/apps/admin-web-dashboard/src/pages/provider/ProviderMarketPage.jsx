import React, { useState } from 'react';

const INITIAL_MARKET_COURSES = [
  { id: 1, title: 'Python for Everybody Specialization', provider: 'Coursera', is_mine: false, industry: 'it', skill: 'Python', clicks: 214, is_partner: false, status: 'public' },
  { id: 2, title: 'Python Backend thực chiến', provider: 'Mekong Skills', is_mine: true, industry: 'it', skill: 'Python', clicks: 128, is_partner: true, status: 'my' },
  { id: 3, title: 'Machine Learning Specialization', provider: 'Coursera', is_mine: false, industry: 'it', skill: 'Machine Learning', clicks: 187, is_partner: false, status: 'public' },
  { id: 4, title: 'Tax Compliance & VAT Deep Dive', provider: 'Đại học Cần Thơ', is_mine: false, industry: 'business', skill: 'Tax Compliance', clicks: 94, is_partner: false, status: 'public' },
  { id: 5, title: 'Phân tích dữ liệu với Power BI', provider: 'Mekong Skills', is_mine: true, industry: 'data', skill: 'Data Analysis', clicks: 112, is_partner: true, status: 'my' },
  { id: 6, title: 'Customs Compliance & Xuất Nhập Khẩu', provider: 'VCCI Cần Thơ', is_mine: false, industry: 'logistics', skill: 'Customs Compliance', clicks: 76, is_partner: false, status: 'public' }
];

export default function ProviderMarketPage() {
  const [courses] = useState(INITIAL_MARKET_COURSES);
  const [unitFilter, setUnitFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('all');
  const [selectedSkill, setSelectedSkill] = useState('all');

  const filtered = courses.filter((c) => {
    if (unitFilter === 'mine' && !c.is_mine) return false;
    if (unitFilter === 'others' && c.is_mine) return false;
    if (selectedIndustry !== 'all' && c.industry !== selectedIndustry) return false;
    if (selectedSkill !== 'all' && c.skill !== selectedSkill) return false;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return c.title.toLowerCase().includes(q) || c.provider.toLowerCase().includes(q) || c.skill.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Thị trường khóa học</h1>
        <p className="text-sm text-slate-500 mt-1">
          Xem các khóa học công khai của tất cả đơn vị đào tạo để tham khảo nội dung, kỹ năng và mức độ quan tâm.
        </p>
      </div>

      {/* Notice Banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-xs font-semibold text-emerald-800">
        <span className="font-bold">Lưu ý:</span> đây là khu vực chỉ để xem. Bạn xem được các khóa học đã công khai của mọi đơn vị, nhưng chỉ sửa hoặc xóa được khóa học của mình trong mục <span className="font-bold underline cursor-pointer">Khóa học của tôi</span>.
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-1 min-w-[280px]">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm theo tên khóa học, kỹ năng, đơn vị đào tạo..."
              className="flex-1 px-4 py-2 rounded-full border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
            <button className="px-5 py-2 bg-[#0a5146] text-white rounded-full text-xs font-bold hover:bg-[#073d35]">
              Tìm
            </button>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="px-4 py-2 rounded-full border border-slate-200 text-xs font-bold text-slate-700 bg-white cursor-pointer focus:outline-none"
            >
              <option value="all">Mọi ngành</option>
              <option value="it">Công nghệ thông tin</option>
              <option value="data">Dữ liệu & AI</option>
              <option value="business">Kinh tế & Quản trị</option>
              <option value="logistics">Logistics & XNK</option>
            </select>

            <select
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
              className="px-4 py-2 rounded-full border border-slate-200 text-xs font-bold text-slate-700 bg-white cursor-pointer focus:outline-none"
            >
              <option value="all">Mọi kỹ năng</option>
              <option value="Python">Python</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Data Analysis">Data Analysis</option>
              <option value="Tax Compliance">Tax Compliance</option>
              <option value="Customs Compliance">Customs Compliance</option>
            </select>
          </div>
        </div>

        {/* Unit Filter Pills */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setUnitFilter('all')}
              className={`px-4 py-1.5 rounded-full font-bold transition-colors ${
                unitFilter === 'all'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Tất cả đơn vị (118)
            </button>
            <button
              onClick={() => setUnitFilter('mine')}
              className={`px-4 py-1.5 rounded-full font-bold transition-colors ${
                unitFilter === 'mine'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Của tôi (4)
            </button>
            <button
              onClick={() => setUnitFilter('others')}
              className={`px-4 py-1.5 rounded-full font-bold transition-colors ${
                unitFilter === 'others'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Đơn vị khác (114)
            </button>
          </div>
          <span className="text-slate-400 font-medium">Hiển thị {filtered.length} trong 118 khóa học công khai</span>
        </div>
      </div>

      {/* Course Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((c) => (
          <div
            key={c.id}
            className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col justify-between hover:shadow-md transition-shadow"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="px-3 py-1 rounded-full text-[11px] font-extrabold bg-teal-50 text-teal-800 border border-teal-100">
                  {c.skill}
                </span>
                <span
                  className={`px-3 py-0.5 rounded-full text-[10px] font-black uppercase ${
                    c.is_mine
                      ? 'bg-[#0a5146] text-white'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {c.is_mine ? 'Của bạn' : 'Công khai'}
                </span>
              </div>

              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 rounded-md bg-[#0d9488] text-white text-xs font-black flex items-center justify-center">
                  {c.provider.charAt(0)}
                </div>
                <span className="text-xs font-semibold text-slate-500">{c.provider}</span>
              </div>

              <h3 className="text-base font-extrabold text-slate-900 line-clamp-2 mb-4">
                {c.title}
              </h3>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                <div>
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Lượt quan tâm</span>
                  <span className="text-lg font-black text-slate-800">{c.clicks}</span>
                </div>
                <div className="text-right">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Đơn vị đào tạo</span>
                  <span className="font-bold text-slate-700">{c.provider}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="flex-1 py-2 px-3 border border-slate-200 rounded-full text-xs font-bold text-slate-700 hover:bg-slate-50">
                  Chi tiết
                </button>
                {c.is_mine ? (
                  <button className="flex-1 py-2 px-3 border border-slate-200 rounded-full text-xs font-bold text-slate-700 hover:bg-slate-50">
                    Quản lý khóa học này
                  </button>
                ) : (
                  <button className="flex-1 py-2 px-3 bg-[#0a5146] text-white rounded-full text-xs font-bold hover:bg-[#073d35]">
                    TRUY CẬP KHÓA HỌC
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

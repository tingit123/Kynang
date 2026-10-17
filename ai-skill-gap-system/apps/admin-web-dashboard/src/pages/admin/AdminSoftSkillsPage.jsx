import React, { useState } from 'react';

// Dữ liệu Top 10 Kỹ năng mềm chung kèm ngành nghề áp dụng tiêu biểu
const SOFT_SKILLS_DATA = [
  { rank: 1, name: "Giao tiếp (Communication)", industry: "Du lịch, Khách sạn & Dịch vụ", shortIndustry: "Du lịch & Dịch vụ", demand: 88.4, supply: 52.1, gap: 36.3, trend: "+8%", coursesCount: 3 },
  { rank: 2, name: "Giải quyết vấn đề", industry: "CNTT, Kỹ thuật & Quản trị", shortIndustry: "CNTT & Kỹ thuật", demand: 82.6, supply: 48.3, gap: 34.3, trend: "+12%", coursesCount: 3 },
  { rank: 3, name: "Tiếng Anh (Ngoại ngữ chuyên môn)", industry: "IT, Logistics & Thương mại QT", shortIndustry: "IT & Logistics", demand: 79.8, supply: 39.2, gap: 40.6, trend: "+15%", coursesCount: 4 },
  { rank: 4, name: "Làm việc nhóm", industry: "Sản xuất, Nhà máy & Đa ngành", shortIndustry: "Sản xuất & Đa ngành", demand: 76.5, supply: 55.8, gap: 20.7, trend: "+5%", coursesCount: 3 },
  { rank: 5, name: "Tư duy phản biện", industry: "Fintech, AI & Phân tích Dữ liệu", shortIndustry: "Fintech & AI", demand: 71.3, supply: 34.6, gap: 36.7, trend: "+18%", coursesCount: 3 },
  { rank: 6, name: "Quản lý thời gian", industry: "Kinh tế & Quản trị Dự án", shortIndustry: "Kinh tế - Dự án", demand: 68.9, supply: 44.7, gap: 24.2, trend: "+6%", coursesCount: 3 },
  { rank: 7, name: "Sáng tạo & Đổi mới", industry: "Marketing số & Thiết kế Media", shortIndustry: "Marketing & Media", demand: 64.2, supply: 38.9, gap: 25.3, trend: "+22%", coursesCount: 3 },
  { rank: 8, name: "Lãnh đạo & Tạo ảnh hưởng", industry: "Quản trị Doanh nghiệp & Vận hành", shortIndustry: "Quản trị & Vận hành", demand: 58.7, supply: 29.4, gap: 29.3, trend: "+10%", coursesCount: 3 },
  { rank: 9, name: "Thích nghi thay đổi", industry: "Công nghệ mới & Ứng dụng AI", shortIndustry: "Tech & GenAI Mới", demand: 55.4, supply: 41.2, gap: 14.2, trend: "+25%", coursesCount: 3 },
  { rank: 10, name: "Dịch vụ khách hàng", industry: "Bán lẻ & Thương mại Điện tử", shortIndustry: "Bán lẻ & E-commerce", demand: 52.1, supply: 42.8, gap: 9.3, trend: "+4%", coursesCount: 3 },
];

// Dữ liệu chuỗi thời gian 7 quý gần nhất (Q1/2025 -> Q3/2026)
const SOFT_TREND_DATA = {
  quarters: ['Q1/2025', 'Q2/2025', 'Q3/2025', 'Q4/2025', 'Q1/2026', 'Q2/2026', 'Q3/2026'],
  skills: [
    {
      name: 'Tiếng Anh (IT & Logistics)',
      color: '#8b5cf6',
      demandHistory: [65.0, 68.4, 71.2, 74.0, 76.5, 78.0, 79.8],
      gapHistory: [28.0, 31.2, 33.5, 36.0, 38.2, 39.5, 40.6]
    },
    {
      name: 'Tư duy phản biện (Fintech & AI)',
      color: '#0ea5e9',
      demandHistory: [48.0, 52.5, 57.0, 61.8, 65.4, 68.7, 71.3],
      gapHistory: [18.5, 22.0, 26.1, 29.8, 33.0, 35.2, 36.7]
    },
    {
      name: 'Giao tiếp (Du lịch & Dịch vụ)',
      color: '#ef4444',
      demandHistory: [78.0, 80.2, 82.5, 84.1, 85.8, 87.2, 88.4],
      gapHistory: [30.5, 31.8, 32.9, 34.0, 35.1, 35.8, 36.3]
    },
    {
      name: 'Giải quyết VĐ (CNTT & KT)',
      color: '#f59e0b',
      demandHistory: [70.0, 72.5, 75.0, 77.2, 79.5, 81.0, 82.6],
      gapHistory: [26.0, 27.8, 29.5, 31.2, 32.8, 33.6, 34.3]
    },
    {
      name: 'Thích nghi (Tech & AI Mới)',
      color: '#10b981',
      demandHistory: [35.0, 38.5, 42.0, 46.2, 49.8, 52.5, 55.4],
      gapHistory: [8.0, 9.5, 10.8, 12.0, 13.1, 13.8, 14.2]
    }
  ]
};

export default function AdminSoftSkillsPage() {
  const [displayCount, setDisplayCount] = useState(5); // Mặc định hiển thị Top 5
  const [trendMetric, setTrendMetric] = useState('gap'); // 'gap' or 'demand'
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('vertical'); // 'vertical' or 'horizontal'
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [modalIndustryFilter, setModalIndustryFilter] = useState('all');

  const visibleSkills = SOFT_SKILLS_DATA.slice(0, displayCount);

  const filteredSkills = SOFT_SKILLS_DATA.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.industry.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const modalFilteredSkills = modalIndustryFilter === 'all'
    ? SOFT_SKILLS_DATA
    : SOFT_SKILLS_DATA.filter(s => s.shortIndustry.toLowerCase().includes(modalIndustryFilter.toLowerCase()));

  return (
    <div className="space-y-6">
      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight flex items-center gap-2">
            Top 10 Kỹ Năng Mềm Theo Ngành
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
              Thị Trường 2026
            </span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Mặc định hiển thị 5 kỹ năng nghề trọng điểm kèm tên ngành · Bấm "Xem chi tiết" để mở toàn cảnh
          </p>
        </div>
      </div>

      {/* ── GỘP BIỂU ĐỒ CỘT VÀ BIỂU ĐỒ ĐƯỜNG ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* CARD 1: BIỂU ĐỒ CỘT GỘP 3 CHỈ SỐ (7 Cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3 mb-4">
              <div>
                <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                  <span>📊</span> Đối Sánh Kỹ Năng Nghề Theo Ngành
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {displayCount === 5 ? 'Hiển thị thoáng Top 5 skill nghề trọng điểm kèm tên ngành' : 'Hiển thị tất cả 10 skill nghề'}
                </p>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={() => setDisplayCount(c => c === 5 ? 10 : 5)}
                  className="px-2.5 py-1 text-xs font-bold rounded-lg border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 transition-colors"
                >
                  {displayCount === 5 ? '⭐ Xem Top 5' : '📋 Đang Xem 10'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsDetailModalOpen(true)}
                  className="px-3 py-1 text-xs font-bold rounded-lg bg-teal-600 text-white hover:bg-teal-700 transition-colors shadow-xs"
                >
                  🔍 Xem Chi Tiết
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode(v => v === 'vertical' ? 'horizontal' : 'vertical')}
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  {viewMode === 'vertical' ? '📊 Cột Dọc' : '📑 Thanh Ngang'}
                </button>
              </div>
            </div>

            {/* Chú thích màu sắc */}
            <div className="flex items-center gap-4 text-xs font-semibold mb-3 px-1">
              <span className="flex items-center gap-1.5 text-slate-700">
                <span className="w-3 h-3 rounded-xs bg-rose-500 inline-block"></span> Nhu cầu (Demand)
              </span>
              <span className="flex items-center gap-1.5 text-slate-700">
                <span className="w-3 h-3 rounded-xs bg-teal-500 inline-block"></span> Cung hiện có (Supply)
              </span>
              <span className="flex items-center gap-1.5 text-slate-700">
                <span className="w-3 h-3 rounded-xs bg-purple-600 inline-block"></span> Thiếu hụt (Gap)
              </span>
            </div>

            {/* Trực quan hóa Biểu đồ Cột Gộp */}
            {viewMode === 'vertical' ? (
              <div className="h-72 flex items-end justify-between gap-3 pt-6 pb-2 px-1 border-b border-slate-100 overflow-x-auto">
                {visibleSkills.map((s, idx) => (
                  <div key={idx} className="flex-1 min-w-[70px] flex flex-col items-center gap-1.5 h-full justify-end group">
                    <div className="w-full flex items-end justify-center gap-1.5 h-48">
                      {/* Demand bar */}
                      <div
                        className="w-1/3 bg-rose-500 rounded-t-xs hover:brightness-110 transition-all relative group/bar"
                        style={{ height: `${s.demand * 0.9}%` }}
                        title={`Demand: ${s.demand}%`}
                      >
                        <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-bold text-rose-600 opacity-0 group-hover/bar:opacity-100 transition-opacity bg-white px-1 shadow-xs rounded border border-rose-100 pointer-events-none">
                          {s.demand}%
                        </span>
                      </div>
                      {/* Supply bar */}
                      <div
                        className="w-1/3 bg-teal-500 rounded-t-xs hover:brightness-110 transition-all relative group/bar"
                        style={{ height: `${s.supply * 0.9}%` }}
                        title={`Supply: ${s.supply}%`}
                      >
                        <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-bold text-teal-600 opacity-0 group-hover/bar:opacity-100 transition-opacity bg-white px-1 shadow-xs rounded border border-teal-100 pointer-events-none">
                          {s.supply}%
                        </span>
                      </div>
                      {/* Gap bar */}
                      <div
                        className="w-1/3 bg-purple-600 rounded-t-xs hover:brightness-110 transition-all relative group/bar"
                        style={{ height: `${s.gap * 0.9}%` }}
                        title={`Gap: ${s.gap.toFixed(1)}%`}
                      >
                        <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[9px] font-bold text-purple-600 opacity-0 group-hover/bar:opacity-100 transition-opacity bg-white px-1 shadow-xs rounded border border-purple-100 pointer-events-none">
                          {s.gap.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    {/* Multiline label: Skill Name & Industry Tag */}
                    <div className="text-center">
                      <div className="text-[11px] font-bold text-slate-800 leading-tight">
                        {s.name.split(' ')[0]}
                      </div>
                      <div className="text-[9.5px] font-semibold text-teal-700 bg-teal-50/80 px-1 py-0.5 rounded mt-0.5 whitespace-nowrap">
                        [{s.shortIndustry}]
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {visibleSkills.map((s, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-50/80 border border-slate-100">
                    <div className="flex justify-between items-center text-xs mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">{s.name}</span>
                        <span className="text-[10px] font-semibold text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-200">
                          {s.shortIndustry}
                        </span>
                      </div>
                      <span className="text-purple-700 font-bold bg-purple-50 px-2 py-0.5 rounded text-[10px]">
                        Gap: {s.gap.toFixed(1)}%
                      </span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-[10px]">
                        <span className="w-12 text-slate-400">Demand</span>
                        <div className="flex-1 bg-slate-200/60 rounded-full h-1.5 overflow-hidden">
                          <div className="bg-rose-500 h-full rounded-full" style={{ width: `${s.demand}%` }} />
                        </div>
                        <span className="w-8 text-right font-bold text-slate-600">{s.demand}%</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px]">
                        <span className="w-12 text-slate-400">Supply</span>
                        <div className="flex-1 bg-slate-200/60 rounded-full h-1.5 overflow-hidden">
                          <div className="bg-teal-500 h-full rounded-full" style={{ width: `${s.supply}%` }} />
                        </div>
                        <span className="w-8 text-right font-bold text-slate-600">{s.supply}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Thanh thông báo hỗ trợ */}
          <div className="mt-3 p-2.5 bg-teal-50/60 border border-teal-100 rounded-xl flex items-center justify-between text-xs text-teal-800">
            <span>🏷️ Hiển thị rõ ràng tên ngành bên dưới mỗi kỹ năng để dễ đối sánh.</span>
            <button
              type="button"
              onClick={() => setIsDetailModalOpen(true)}
              className="font-bold text-teal-700 hover:underline"
            >
              Mở toàn màn hình ↗
            </button>
          </div>
        </div>

        {/* CARD 2: BIỂU ĐỒ ĐƯỜNG XU HƯỚNG THEO THỜI GIAN (5 Cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3 mb-4">
              <div>
                <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                  <span>📈</span> Xu Hướng Biến Động Theo Quý
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {trendMetric === 'gap' ? 'Độ thiếu hụt (Gap %) qua 7 quý gần nhất' : 'Nhu cầu tuyển dụng (Demand %) qua 7 quý'}
                </p>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setTrendMetric('gap')}
                  className={`px-2.5 py-1 text-xs font-bold rounded-full transition-colors ${
                    trendMetric === 'gap'
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Thiếu Hụt (Gap %)
                </button>
                <button
                  type="button"
                  onClick={() => setTrendMetric('demand')}
                  className={`px-2.5 py-1 text-xs font-bold rounded-full transition-colors ${
                    trendMetric === 'demand'
                      ? 'bg-rose-500 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Nhu Cầu (%)
                </button>
              </div>
            </div>

            {/* Trực quan hóa Biểu đồ Đường SVG */}
            <div className="h-72 pt-2 flex flex-col justify-between">
              {/* Legend */}
              <div className="flex flex-wrap gap-2 text-[10px] font-semibold mb-2">
                {SOFT_TREND_DATA.skills.map((s, idx) => (
                  <span key={idx} className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-50 border border-slate-100">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                    <span className="text-slate-700">{s.name}</span>
                  </span>
                ))}
              </div>

              {/* Line graph area */}
              <div className="flex-1 relative flex items-center">
                <svg className="w-full h-44 overflow-visible" viewBox="0 0 350 140" preserveAspectRatio="none">
                  <line x1="0" y1="20" x2="350" y2="20" stroke="#f1f5f9" strokeDasharray="3 3" />
                  <line x1="0" y1="60" x2="350" y2="60" stroke="#f1f5f9" strokeDasharray="3 3" />
                  <line x1="0" y1="100" x2="350" y2="100" stroke="#f1f5f9" strokeDasharray="3 3" />

                  {SOFT_TREND_DATA.skills.map((s, idx) => {
                    const values = trendMetric === 'gap' ? s.gapHistory : s.demandHistory;
                    const maxVal = trendMetric === 'gap' ? 50 : 100;
                    const minVal = trendMetric === 'gap' ? 0 : 30;
                    
                    const points = values.map((val, qIdx) => {
                      const x = (qIdx / (SOFT_TREND_DATA.quarters.length - 1)) * 350;
                      const y = 130 - ((val - minVal) / (maxVal - minVal)) * 120;
                      return `${x},${y}`;
                    }).join(' ');

                    return (
                      <g key={idx}>
                        <polyline
                          fill="none"
                          stroke={s.color}
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          points={points}
                        />
                        {values.map((val, qIdx) => {
                          const cx = (qIdx / (SOFT_TREND_DATA.quarters.length - 1)) * 350;
                          const cy = 130 - ((val - minVal) / (maxVal - minVal)) * 120;
                          return (
                            <circle
                              key={qIdx}
                              cx={cx}
                              cy={cy}
                              r="3.5"
                              fill="#ffffff"
                              stroke={s.color}
                              strokeWidth="2"
                            />
                          );
                        })}
                      </g>
                    );
                  })}
                </svg>
              </div>

              {/* X Axis Quarters */}
              <div className="flex justify-between text-[10px] text-slate-400 font-semibold pt-2 border-t border-slate-100">
                {SOFT_TREND_DATA.quarters.map((q, idx) => (
                  <span key={idx}>{q}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── BẢNG XẾP HẠNG CHI TIẾT ── */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Bảng Xếp Hạng Chi Tiết – Kỹ Năng Mềm Theo Ngành</h3>
            <p className="text-xs text-slate-500 mt-0.5">Sắp xếp theo Nhu cầu tuyển dụng · Gắn với ngành nghề trọng điểm Cần Thơ</p>
          </div>
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm kỹ năng hoặc ngành..."
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-200 w-56"
            />
            <span className="absolute left-2.5 top-2 text-slate-400 text-xs">🔍</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
              <tr>
                <th className="py-3 px-4 w-12">#</th>
                <th className="py-3 px-4">Kỹ Năng Mềm</th>
                <th className="py-3 px-4">Ngành Nghề Áp Dụng</th>
                <th className="py-3 px-4">Nhu Cầu (Demand)</th>
                <th className="py-3 px-4">Cung Hiện Có (Supply)</th>
                <th className="py-3 px-4">Thiếu Hụt (Gap)</th>
                <th className="py-3 px-4">Xu Hướng</th>
                <th className="py-3 px-4 text-right">Hành Động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredSkills.map((s) => (
                <tr key={s.rank} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-500">
                    {s.rank === 1 ? '🥇' : s.rank === 2 ? '🥈' : s.rank === 3 ? '🥉' : `#${s.rank}`}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">{s.name}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded font-semibold text-[10.5px] bg-teal-50 text-teal-800 border border-teal-200">
                      🏷️ {s.shortIndustry}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-rose-500 h-full rounded-full" style={{ width: `${s.demand}%` }} />
                      </div>
                      <span className="font-bold text-slate-800">{s.demand}%</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-teal-500 h-full rounded-full" style={{ width: `${s.supply}%` }} />
                      </div>
                      <span className="font-bold text-slate-800">{s.supply}%</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded font-bold text-[11px] bg-purple-50 text-purple-700 border border-purple-200">
                      {s.gap.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[11px]">
                      🔺 {s.trend}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button className="px-3 py-1 rounded-lg bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 font-semibold transition-colors inline-flex items-center gap-1">
                      <span>Xem {s.coursesCount} khóa học</span>
                      <span>↗</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── MODAL: CHI TIẾT TỔNG QUAN TẤT CẢ KỸ NĂNG & NGÀNH NGHỀ ── */}
      {isDetailModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
                  <span>📋</span> Tổng Quan Chi Tiết Tất Cả Kỹ Năng &amp; Phân Bổ Theo Ngành Nghề
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Toàn cảnh đối sánh 10 kỹ năng nghề chuẩn hóa với đầy đủ tên ngành đào tạo tương ứng
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsDetailModalOpen(false)}
                className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors flex items-center gap-1"
              >
                ✕ Đóng
              </button>
            </div>

            {/* Filter Pills */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100">
              <span className="text-xs font-bold text-slate-600">Lọc theo ngành:</span>
              <div className="flex flex-wrap gap-2">
                {[
                  { key: 'all', label: 'Tất Cả (10 Skill)' },
                  { key: 'Du lịch', label: '✈️ Du Lịch & Dịch Vụ' },
                  { key: 'CNTT', label: '💻 CNTT & Kỹ Thuật' },
                  { key: 'Logistics', label: '📦 IT & Logistics' },
                  { key: 'Fintech', label: '📊 Fintech & AI' },
                ].map(item => (
                  <button
                    key={item.key}
                    type="button"
                    onClick={() => setModalIndustryFilter(item.key)}
                    className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${
                      modalIndustryFilter === item.key
                        ? 'bg-teal-600 text-white'
                        : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Modal Table */}
            <div className="border border-slate-200 rounded-2xl overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                  <tr>
                    <th className="py-3 px-4">#</th>
                    <th className="py-3 px-4">Kỹ Năng</th>
                    <th className="py-3 px-4">Ngành Nghề Áp Dụng</th>
                    <th className="py-3 px-4">Nhu Cầu</th>
                    <th className="py-3 px-4">Cung Ứng</th>
                    <th className="py-3 px-4">Thiếu Hụt (Gap)</th>
                    <th className="py-3 px-4">Xu Hướng</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {modalFilteredSkills.map(s => (
                    <tr key={s.rank} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-bold text-slate-400">#{s.rank}</td>
                      <td className="py-3 px-4 font-bold text-slate-900">{s.name}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded font-semibold text-[10.5px] bg-teal-50 text-teal-800 border border-teal-200">
                          🏷️ {s.industry}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-rose-600">{s.demand}%</td>
                      <td className="py-3 px-4 font-bold text-teal-600">{s.supply}%</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded font-bold text-[11px] bg-purple-50 text-purple-700 border border-purple-200">
                          {s.gap.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-emerald-600">🔺 {s.trend}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <span className="text-xs text-slate-400">Hệ thống phân tích kỹ năng SkillGapAI Cần Thơ</span>
              <button
                type="button"
                onClick={() => setIsDetailModalOpen(false)}
                className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs transition-colors"
              >
                Đóng Chi Tiết
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

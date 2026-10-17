import React, { useState } from 'react';

const YEAR_SHIFT_DATA = {
  '2024-2025': {
    fromYear: '2024',
    toYear: '2025',
    bannerPeriod: 'Giai đoạn 2024 – 2025',
    summary:
      'Thị trường bắt đầu bước vào giai đoạn phục hồi và tăng trưởng số. IT & Công nghệ (+23.9%) và Du lịch & Khách sạn (+16.7%) là hai điểm sáng lớn, trong khi Kinh tế truyền thống (-6.9%) bắt đầu chững lại.',
    topWinner: { name: 'IT & Công nghệ', growth: '+23.9%', sub: 'Tỷ trọng tăng từ 25.5% → 28.5%' },
    runnerUp: { name: 'Du lịch & Khách sạn', growth: '+16.7%', sub: 'Phục hồi sau dịch, khách quốc tế tăng' },
    agri: { name: 'Nông nghiệp CNC', growth: '+28.6%', sub: 'Mô hình ứng dụng IoT khởi động' },
    decliner: { name: 'Kinh tế & Kế toán', growth: '-6.9%', sub: 'Thị phần giảm từ 32.2% → 27.0%' },
    industries: [
      { name: 'IT & Công nghệ', icon: '💻', countFrom: 230, pctFrom: 25.5, countTo: 285, pctTo: 28.5, growth: 23.9, trend: 'Tăng trưởng nhanh', statusClass: 'growth', drivers: 'Thành lập trung tâm phần mềm vệ tinh, chuyển đổi số doanh nghiệp ĐBSCL' },
      { name: 'Logistics & XNK', icon: '🚢', countFrom: 165, pctFrom: 18.3, countTo: 190, pctTo: 19.0, growth: 15.2, trend: 'Tăng trưởng đều', statusClass: 'growth', drivers: 'Mở rộng cao tốc Trung Lương - Mỹ Thuận - Cần Thơ, dịch vụ kho vận' },
      { name: 'Du lịch & Khách sạn', icon: '✈️', countFrom: 180, pctFrom: 20.0, countTo: 210, pctTo: 21.0, growth: 16.7, trend: 'Phục hồi tích cực', statusClass: 'growth', drivers: 'Du lịch MICE & sinh thái miệt vườn đón dòng khách quốc tế trở lại' },
      { name: 'Kinh tế & Tài chính', icon: '📊', countFrom: 290, pctFrom: 32.2, countTo: 270, pctTo: 27.0, growth: -6.9, trend: 'Bão hòa & Giảm nhẹ', statusClass: 'decline', drivers: 'Tự động hóa tác vụ nhập liệu, sáp nhập phòng giao dịch ngân hàng' },
      { name: 'Nông nghiệp CNC', icon: '🌱', countFrom: 35, pctFrom: 3.9, countTo: 45, pctTo: 4.5, growth: 28.6, trend: 'Bắt đầu khởi sắc', statusClass: 'boom', drivers: 'Thử nghiệm cảm biến IoT đo độ mặn, canh tác hữu cơ xuất khẩu' }
    ]
  },
  '2025-2026': {
    fromYear: '2025',
    toYear: '2026',
    bannerPeriod: 'Giai đoạn 2025 – 2026',
    summary:
      'Thị trường lao động TP. Cần Thơ & ĐBSCL đang chuyển dịch bùng nổ sang IT & Công nghệ số (+35.1%) và Logistics (+26.8%). Ngược lại, ngành Kinh tế & Kế toán truyền thống sụt giảm tỷ trọng (-42.2%) do tác động của tự động hóa và AI.',
    topWinner: { name: 'IT & Công nghệ', growth: '+35.1%', sub: 'Tỷ trọng tăng từ 28.5% → 38.5% (+10% thị phần)' },
    runnerUp: { name: 'Logistics & XNK', growth: '+26.8%', sub: 'Tỷ trọng tăng từ 19.0% → 24.1% (+5.1% thị phần)' },
    agri: { name: 'Nông nghiệp CNC', growth: '+73.3%', sub: 'Thị phần tăng vọt từ 4.5% → 7.8%' },
    decliner: { name: 'Kinh tế & Kế toán', growth: '-42.2%', sub: 'Thị phần sụt giảm từ 27.0% → 15.6%' },
    industries: [
      { name: 'IT & Công nghệ', icon: '💻', countFrom: 285, pctFrom: 28.5, countTo: 385, pctTo: 38.5, growth: 35.1, trend: '🔥 Chuyển dịch trọng tâm', statusClass: 'boom', drivers: 'Sự mở rộng của FPT, TMA, Viettel Digital; nhu cầu Python, Cloud, Fullstack, AI' },
      { name: 'Logistics & XNK', icon: '🚢', countFrom: 190, pctFrom: 19.0, countTo: 241, pctTo: 24.1, growth: 26.8, trend: '🚀 Tăng trưởng mạnh mẽ', statusClass: 'growth', drivers: 'Cảng nước sâu Cái Cui, logistics chuỗi lạnh nông thủy sản xuất khẩu EU, Mỹ' },
      { name: 'Du lịch & Khách sạn', icon: '✈️', countFrom: 210, pctFrom: 21.0, countTo: 218, pctTo: 21.8, growth: 3.8, trend: '⚖️ Ổn định & Chuyên sâu', statusClass: 'stable', drivers: 'Chuyển đổi số du lịch, nâng chuẩn ngoại ngữ & kỹ năng trải nghiệm khách hàng' },
      { name: 'Kinh tế & Tài chính', icon: '📊', countFrom: 270, pctFrom: 27.0, countTo: 156, pctTo: 15.6, growth: -42.2, trend: '📉 Thu hẹp (Tự động hóa)', statusClass: 'decline', drivers: 'Ứng dụng GenAI, RPA trong kế toán & thuế, giảm mạnh chỉ tiêu kế toán sơ cấp' },
      { name: 'Nông nghiệp CNC', icon: '🌱', countFrom: 45, pctFrom: 4.5, countTo: 78, pctTo: 7.8, growth: 73.3, trend: '🌱 Tăng tốc đột phá', statusClass: 'boom', drivers: 'Đề án 1 triệu ha lúa chất lượng cao, drone gieo sạ, cảm biến IoT đo độ phèn mặn' }
    ]
  },
  '2026-2027': {
    fromYear: '2026',
    toYear: '2027 (Dự báo)',
    bannerPeriod: 'Dự báo giai đoạn 2026 – 2027',
    summary:
      'Dự báo lực lượng lao động tiếp tục dịch chuyển mạnh về Kinh tế số & Kinh tế xanh. IT và Logistics chiếm hơn 68% tổng việc làm mới, trong khi Nông nghiệp công nghệ cao vượt mốc 10% thị phần.',
    topWinner: { name: 'Nông nghiệp CNC & IT', growth: '+41.0%', sub: 'Bùng nổ nông nghiệp xanh & tín chỉ carbon' },
    runnerUp: { name: 'Logistics & Cảng biển', growth: '+20.3%', sub: 'Trở thành trung tâm logistics vùng ĐBSCL' },
    agri: { name: 'Nông nghiệp CNC', growth: '+41.0%', sub: 'Thị phần chính thức đạt 10.0%' },
    decliner: { name: 'Kế toán truyền thống', growth: '-26.3%', sub: 'Thị phần chỉ còn 10.5%, dịch chuyển sang Fintech' },
    industries: [
      { name: 'IT & Công nghệ', icon: '💻', countFrom: 385, pctFrom: 38.5, countTo: 460, pctTo: 41.8, growth: 19.5, trend: '👑 Giữ vị thế chủ lực', statusClass: 'boom', drivers: 'Kỹ sư AI Agent, Data Engineer, An toàn thông tin phục vụ đô thị thông minh Cần Thơ' },
      { name: 'Logistics & XNK', icon: '🚢', countFrom: 241, pctFrom: 24.1, countTo: 290, pctTo: 26.4, growth: 20.3, trend: '🚀 Tăng trưởng bền vững', statusClass: 'growth', drivers: 'Hạ tầng cao tốc kết nối toàn vùng, hình thành trung tâm logistics liên vùng' },
      { name: 'Du lịch & Khách sạn', icon: '✈️', countFrom: 218, pctFrom: 21.8, countTo: 225, pctTo: 20.5, growth: 3.2, trend: '⚖️ Duy trì ổn định', statusClass: 'stable', drivers: 'Nghỉ dưỡng sinh thái ven sông Hậu cao cấp, du lịch kết hợp chăm sóc sức khỏe' },
      { name: 'Kinh tế & Tài chính', icon: '📊', countFrom: 156, pctFrom: 15.6, countTo: 115, pctTo: 10.5, growth: -26.3, trend: '🔄 Chuyển dịch sang Fintech', statusClass: 'decline', drivers: 'Vị trí kế toán truyền thống giảm, chỉ tuyển chuyên viên phân tích tài chính số' },
      { name: 'Nông nghiệp CNC', icon: '🌱', countFrom: 78, pctFrom: 7.8, countTo: 110, pctTo: 10.0, growth: 41.0, trend: '🌱 Bùng nổ kinh tế xanh', statusClass: 'boom', drivers: 'Thương mại tín chỉ carbon lúa gạo, chế biến sâu xuất khẩu nông thủy sản' }
    ]
  }
};

const MULTI_YEAR_SERIES = [
  { year: '2023', it: 180, logistics: 140, tourism: 150, economics: 310, agri: 25 },
  { year: '2024', it: 230, logistics: 165, tourism: 180, economics: 290, agri: 35 },
  { year: '2025', it: 285, logistics: 190, tourism: 210, economics: 270, agri: 45 },
  { year: '2026', it: 385, logistics: 241, tourism: 218, economics: 156, agri: 78 },
  { year: '2027 (Dự báo)', it: 460, logistics: 290, tourism: 225, economics: 115, agri: 110 }
];

export default function AdminDashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('2025-2026');
  const currentData = YEAR_SHIFT_DATA[selectedPeriod] || YEAR_SHIFT_DATA['2025-2026'];

  return (
    <div className="space-y-6">
      {/* ── HEADER ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight">Dashboard Tổng Quan</h1>
          <p className="text-sm text-slate-500">
            Dữ liệu từ 1,000 Job Postings (TopCV) · 500 CV Sinh viên · AI xử lý tự động
          </p>
        </div>
        <button
          onClick={() => alert('Đang xuất báo cáo phân tích dịch chuyển ngành nghề...')}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0fa39e] hover:bg-[#0d8f8a] text-white font-bold text-xs shadow-sm cursor-pointer transition-colors"
        >
          <span>📥</span> Xuất Báo Cáo
        </button>
      </div>

      {/* ── 4 KPI CARDS ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center text-xl">
            💼
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase">Tin Tuyển Dụng</div>
            <div className="text-2xl font-black text-slate-800">1,000</div>
            <div className="text-[11px] font-bold text-emerald-600">↗ Từ TopCV · 4 ngành chủ chốt</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl">
            🎓
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase">CV Sinh Viên</div>
            <div className="text-2xl font-black text-slate-800">500</div>
            <div className="text-[11px] font-bold text-emerald-600">↗ Đã phân loại kỹ năng bằng AI</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-xl">
            ⚠️
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase">Gap Trung Bình</div>
            <div className="text-2xl font-black text-amber-600">34.6%</div>
            <div className="text-[11px] font-bold text-amber-600">↗ Cần cải thiện khẩn cấp</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center text-xl">
            ⚡
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase">Kỹ Năng AI Phân Loại</div>
            <div className="text-2xl font-black text-purple-600">68</div>
            <div className="text-[11px] font-bold text-purple-600">↗ Nhóm lớn → nhóm nhỏ</div>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── CARD: XU HƯỚNG CHUYỂN DỊCH NGÀNH NGHỀ QUA CÁC NĂM ──          */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-7 space-y-6">
        {/* Title and Period Selector Pills */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl">📈</span>
              <h2 className="text-lg font-black text-slate-800 tracking-tight">
                Xu Hướng Chuyển Dịch Ngành Nghề Qua Các Năm
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
                AI Shift Analytics
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Phân tích động thái dịch chuyển thị phần tuyển dụng &amp; nhu cầu nhân lực tại Cần Thơ &amp; ĐBSCL
            </p>
          </div>

          <div className="flex items-center gap-1.5 p-1 rounded-full bg-slate-100 border border-slate-200 self-start sm:self-auto">
            {['2024-2025', '2025-2026', '2026-2027'].map(period => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  selectedPeriod === period
                    ? 'bg-[#0fa39e] text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {period === '2025-2026' ? '2025 – 2026 (Hiện tại)' : period === '2026-2027' ? '2026 – 2027 (Dự báo)' : '2024 – 2025'}
              </button>
            ))}
          </div>
        </div>

        {/* AI Insight Headline Banner */}
        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-teal-50 to-emerald-50 border border-teal-200 flex items-start gap-3.5">
          <span className="text-2xl leading-none">💡</span>
          <div className="space-y-1">
            <div className="text-xs font-extrabold text-[#0fa39e] uppercase tracking-wide">
              KẾT LUẬN CHUYỂN DỊCH TỪ HỆ THỐNG AI ({currentData.bannerPeriod})
            </div>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
              {currentData.summary}
            </p>
          </div>
        </div>

        {/* 4 Stat Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70">
            <div className="text-[11px] font-bold text-emerald-600 uppercase">🚀 Dẫn đầu chuyển dịch</div>
            <div className="text-base font-extrabold text-slate-800 mt-1">{currentData.topWinner.name}</div>
            <div className="text-2xl font-black text-emerald-600 mt-1">{currentData.topWinner.growth}</div>
            <div className="text-[11px] text-slate-500 mt-1">{currentData.topWinner.sub}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70">
            <div className="text-[11px] font-bold text-amber-600 uppercase">🚢 Đón sóng hạ tầng</div>
            <div className="text-base font-extrabold text-slate-800 mt-1">{currentData.runnerUp.name}</div>
            <div className="text-2xl font-black text-amber-600 mt-1">{currentData.runnerUp.growth}</div>
            <div className="text-[11px] text-slate-500 mt-1">{currentData.runnerUp.sub}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70">
            <div className="text-[11px] font-bold text-purple-600 uppercase">🌱 Bứt phá công nghệ cao</div>
            <div className="text-base font-extrabold text-slate-800 mt-1">{currentData.agri.name}</div>
            <div className="text-2xl font-black text-purple-600 mt-1">{currentData.agri.growth}</div>
            <div className="text-[11px] text-slate-500 mt-1">{currentData.agri.sub}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70">
            <div className="text-[11px] font-bold text-rose-600 uppercase">📉 Thu hẹp do tự động hóa</div>
            <div className="text-base font-extrabold text-slate-800 mt-1">{currentData.decliner.name}</div>
            <div className="text-2xl font-black text-rose-600 mt-1">{currentData.decliner.growth}</div>
            <div className="text-[11px] text-slate-500 mt-1">{currentData.decliner.sub}</div>
          </div>
        </div>

        {/* Detailed Industry Shift Table */}
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-extrabold text-slate-500 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Ngành Nghề</th>
                <th className="py-3 px-4 text-center">Năm {currentData.fromYear}</th>
                <th className="py-3 px-4 text-center">Năm {currentData.toYear}</th>
                <th className="py-3 px-4 text-center">Biến Động (Δ)</th>
                <th className="py-3 px-4">Tỷ Trọng Thị Phần</th>
                <th className="py-3 px-4">Xu Hướng</th>
                <th className="py-3 px-4">Động Lực Dịch Chuyển</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {currentData.industries.map((ind, idx) => {
                const isPos = ind.growth > 0;
                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-800">
                      <span className="mr-2 text-base">{ind.icon}</span>
                      {ind.name}
                    </td>
                    <td className="py-3.5 px-4 text-center text-slate-600">
                      <span className="font-bold">{ind.countFrom}</span> tin
                      <div className="text-[11px] text-slate-400">({ind.pctFrom}%)</div>
                    </td>
                    <td className="py-3.5 px-4 text-center text-slate-800">
                      <span className="font-extrabold text-[#0fa39e]">{ind.countTo}</span> tin
                      <div className="text-[11px] font-bold text-teal-600">({ind.pctTo}%)</div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black ${
                          isPos
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {isPos ? `+${ind.growth}% ↗` : `${ind.growth}% ↘`}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 min-w-[140px]">
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>{ind.pctFrom}%</span>
                        <span className="font-bold text-teal-700">{ind.pctTo}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-100 overflow-hidden flex">
                        <div style={{ width: `${ind.pctFrom}%` }} className="bg-slate-300" />
                        <div
                          style={{ width: `${Math.max(0, ind.pctTo - ind.pctFrom)}%` }}
                          className={isPos ? 'bg-emerald-500' : 'bg-rose-500'}
                        />
                      </div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                          ind.statusClass === 'boom'
                            ? 'bg-emerald-100 text-emerald-800'
                            : ind.statusClass === 'growth'
                            ? 'bg-teal-100 text-teal-800'
                            : ind.statusClass === 'stable'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {ind.trend}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-500 max-w-xs">{ind.drivers}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

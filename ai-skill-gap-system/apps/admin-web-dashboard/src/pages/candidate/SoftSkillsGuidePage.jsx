import React, { useState } from 'react';

const TOP_10_SOFT_SKILLS = [
  { rank: 1, name: 'Tiếng Anh Giao Tiếp & Kỹ Thuật', demand: 76.6, supply: 42.0, gap: 34.6, trend: '+8%', desc: 'Kỹ năng số 1 bắt buộc cho mọi ngành nghề để đọc tài liệu, giao tiếp quốc tế và tiếp cận tài liệu chuyên môn.' },
  { rank: 2, name: 'Giao Tiếp & Thuyết Trình', demand: 72.0, supply: 48.0, gap: 24.0, trend: '+12%', desc: 'Truyền đạt ý tưởng ngắn gọn, rõ ràng với đồng nghiệp, khách hàng và cấp trên.' },
  { rank: 3, name: 'Giải Quyết Vấn Đề (Problem Solving)', demand: 68.5, supply: 41.5, gap: 27.0, trend: '+18%', desc: 'Tư duy logic, tìm nguyên nhân gốc rễ và đưa ra giải pháp thực thi hiệu quả.' },
  { rank: 4, name: 'Làm Việc Nhóm (Teamwork & Collab)', demand: 65.0, supply: 50.0, gap: 15.0, trend: '+5%', desc: 'Phối hợp nhịp nhàng, lắng nghe và chia sẻ trách nhiệm trong tập thể.' },
  { rank: 5, name: 'Tư Duy Phản Biện (Critical Thinking)', demand: 58.0, supply: 32.0, gap: 26.0, trend: '+22%', desc: 'Đánh giá thông tin khách quan, không chấp nhận định kiến sẵn có.' },
  { rank: 6, name: 'Quản Lý Thời Gian & Năng Suất', demand: 54.0, supply: 35.0, gap: 19.0, trend: '+10%', desc: 'Sắp xếp mức độ ưu tiên công việc, đảm bảo tiến độ deadline cam kết.' },
  { rank: 7, name: 'Sáng Tạo & Đổi Mới (Innovation)', demand: 48.0, supply: 26.0, gap: 22.0, trend: '+25%', desc: 'Tìm tòi cách làm mới, tối ưu hóa quy trình thủ công lạc hậu.' },
  { rank: 8, name: 'Lãnh Đạo & Tạo Ảnh Hưởng', demand: 42.0, supply: 22.0, gap: 20.0, trend: '+14%', desc: 'Khả năng định hướng, thúc đẩy tinh thần và dẫn dắt đội ngũ hoàn thành mục tiêu.' },
  { rank: 9, name: 'Thích Nghi Thay Đổi (Adaptability)', demand: 40.0, supply: 25.0, gap: 15.0, trend: '+30%', desc: 'Chủ động đón nhận công nghệ mới (đặc biệt là công cụ AI tạo sinh).' },
  { rank: 10, name: 'Dịch Vụ Khách Hàng Chuyên Nghiệp', demand: 36.0, supply: 24.0, gap: 12.0, trend: '+7%', desc: 'Thấu hiểu tâm lý khách hàng, giữ thái độ chuẩn mực và tận tâm.' },
];

export default function SoftSkillsGuidePage() {
  const [filterQuery, setFilterQuery] = useState('');

  const filteredSkills = TOP_10_SOFT_SKILLS.filter(s =>
    s.name.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-8 py-4">
      {/* ── HEADER ── */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 bg-amber-50 text-amber-800 text-xs font-bold px-3 py-1 rounded-full border border-amber-200">
          <span>💡 Bộ Chỉ Số Thị Trường Lao Động Cần Thơ</span>
          <span>•</span>
          <span>Gap = Demand – Supply</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
          Cẩm Nang Top 10 Kỹ Năng Mềm Được Nhà Tuyển Dụng Săn Đón
        </h1>
        <p className="text-slate-500 text-sm max-w-3xl leading-relaxed">
          Biểu đồ phân tích độ thiếu hụt (Gap) giữa nhu cầu tuyển dụng thực tế và mức độ đáp ứng của sinh viên / người lao động tại TP. Cần Thơ.
        </p>
      </div>

      {/* ── THANH TÌM KIẾM NHANH ── */}
      <div className="flex items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Tìm kiếm kỹ năng mềm (VD: Tiếng Anh, Giao tiếp...)"
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
          />
          <span className="absolute left-3 top-2.5 text-slate-400">🔍</span>
        </div>
        <div className="text-xs text-slate-500 font-semibold hidden sm:block">
          Hiển thị <strong>{filteredSkills.length}</strong> / 10 kỹ năng cốt lõi
        </div>
      </div>

      {/* ── BẢNG BIỂU ĐỒ THANH NGANG ── */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Thống Kê Nhu Cầu &amp; Khoảng Cách Thiếu Hụt (Gap)</h3>
            <p className="text-xs text-slate-500">Cột màu đỏ thể hiện mức độ thiếu hụt lao động mà bạn nên ưu tiên rèn luyện ngay</p>
          </div>
          {/* Chú thích màu sắc */}
          <div className="flex items-center gap-4 text-xs font-semibold">
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-3 h-3 rounded-sm bg-rose-500 inline-block"></span> Nhu cầu (Demand)
            </span>
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-3 h-3 rounded-sm bg-teal-500 inline-block"></span> Cung hiện có (Supply)
            </span>
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-3 h-3 rounded-sm bg-purple-600 inline-block"></span> Thiếu hụt (Gap)
            </span>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {filteredSkills.map((item) => (
            <div key={item.rank} className="p-5 hover:bg-slate-50/80 transition-colors space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-extrabold ${
                    item.rank <= 3 ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-600'
                  }`}>
                    #{item.rank}
                  </span>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{item.name}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  <span className="text-xs font-bold text-purple-700 bg-purple-50 px-2.5 py-1 rounded-md border border-purple-200">
                    Gap: {item.gap.toFixed(1)}%
                  </span>
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md">
                    🔺 {item.trend}
                  </span>
                </div>
              </div>

              {/* Thanh ngang so sánh 3 chỉ số */}
              <div className="space-y-1.5 pt-1">
                {/* Demand */}
                <div className="flex items-center gap-3 text-xs">
                  <span className="w-20 text-slate-400 font-medium">Demand</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-rose-500 h-2 rounded-full" style={{ width: `${item.demand}%` }} />
                  </div>
                  <span className="w-12 text-right font-bold text-slate-700">{item.demand}%</span>
                </div>

                {/* Supply */}
                <div className="flex items-center gap-3 text-xs">
                  <span className="w-20 text-slate-400 font-medium">Supply</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-teal-500 h-2 rounded-full" style={{ width: `${item.supply}%` }} />
                  </div>
                  <span className="w-12 text-right font-bold text-slate-700">{item.supply}%</span>
                </div>

                {/* Gap */}
                <div className="flex items-center gap-3 text-xs">
                  <span className="w-20 text-purple-600 font-bold">Thiếu hụt</span>
                  <div className="flex-1 bg-purple-50 rounded-full h-2 overflow-hidden">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${item.gap}%` }} />
                  </div>
                  <span className="w-12 text-right font-bold text-purple-700">{item.gap.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

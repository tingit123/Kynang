import React from 'react';

const TOP_COURSES = [
  {
    id: 1,
    title: 'Python Backend thực chiến',
    skill: 'Python',
    clicks: 128,
    percent: 35.7,
    isTop: true
  },
  {
    id: 2,
    title: 'Nhập môn Machine Learning',
    skill: 'Machine Learning',
    clicks: 96,
    percent: 26.7,
    isTop: false
  },
  {
    id: 3,
    title: 'FastAPI & Docker cho người mới',
    skill: 'Python',
    clicks: 74,
    percent: 20.6,
    isTop: false
  },
  {
    id: 4,
    title: 'Phân tích dữ liệu với Power BI',
    skill: 'Data Analysis',
    clicks: 61,
    percent: 17.0,
    isTop: false
  },
  {
    id: 5,
    title: 'IELTS 6.5 cho sinh viên',
    skill: 'English',
    clicks: 0,
    percent: 0.0,
    isTop: false
  },
  {
    id: 6,
    title: 'Giao tiếp và thuyết trình',
    skill: 'Communication',
    clicks: 0,
    percent: 0.0,
    isTop: false
  }
];

export default function ProviderAnalyticsPage() {
  return (
    <div className="space-y-7 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Thống kê lượt click
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Đo hiệu quả: có bao nhiêu sinh viên bấm vào khóa học từ gợi ý của AI.
        </p>
      </div>

      {/* ── 2. 3 THẺ KPI TOP (KHỚP 100% ẢNH MẪU) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Tổng lượt truy cập */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#0d9488]" />
          <div className="text-[11.5px] font-black uppercase text-slate-500 tracking-wider">
            TỔNG LƯỢT TRUY CẬP
          </div>
          <div className="text-5xl font-black text-slate-900 my-2.5">
            359
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Sinh viên bấm vào khóa học từ gợi ý của AI
          </div>
        </div>

        {/* Card 2: Khóa học đang phân phối */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#f59e0b]" />
          <div className="text-[11.5px] font-black uppercase text-slate-500 tracking-wider">
            KHÓA HỌC ĐANG PHÂN PHỐI
          </div>
          <div className="text-5xl font-black text-slate-900 my-2.5">
            4
          </div>
          <div className="text-xs text-slate-500 font-medium">
            Trên tổng số 6 khóa học đã đăng
          </div>
        </div>

        {/* Card 3: Thu hút nhất */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-[#2563eb]" />
          <div>
            <div className="text-[11.5px] font-black uppercase text-slate-500 tracking-wider">
              THU HÚT NHẤT
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-900 mt-2.5 leading-snug">
              Python Backend thực chiến
            </div>
          </div>
          <div className="text-xs text-slate-500 font-medium mt-3">
            128 lượt click
          </div>
        </div>
      </div>

      {/* ── 3. BỐ CỤC 2 CỘT DƯỚI (KHÓA HỌC THU HÚT NHẤT & TỶ TRỌNG LƯỢT CLICK) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
        {/* CỘT TRÁI: BẢNG KHÓA HỌC THU HÚT NHẤT (6 COLS) */}
        <div className="lg:col-span-6 bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <h2 className="text-base font-extrabold text-slate-900 mb-5">
            Khóa học thu hút nhất
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[11px] font-black text-slate-400 uppercase tracking-wider border-b border-slate-100">
                  <th className="pb-3 pl-1 w-8">#</th>
                  <th className="pb-3 pr-2">KHÓA HỌC</th>
                  <th className="pb-3 px-2 w-32">KỸ NĂNG BÙ ĐẮP</th>
                  <th className="pb-3 pr-2 w-14 text-right">CLICK</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100/80 text-sm">
                {TOP_COURSES.map((item, idx) => (
                  <tr key={item.id} className="hover:bg-slate-50/50">
                    <td className="py-4 pl-1 font-bold text-slate-400 text-xs">
                      {idx + 1}
                    </td>
                    <td className="py-4 pr-2 font-bold text-slate-900 text-sm">
                      {item.title}
                    </td>
                    <td className="py-4 px-2">
                      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                        {item.skill}
                      </span>
                    </td>
                    <td className="py-4 pr-2 text-right font-black text-slate-900 text-sm">
                      {item.clicks}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* CỘT PHẢI: TỶ TRỌNG LƯỢT CLICK THEO KHÓA HỌC (6 COLS) */}
        <div className="lg:col-span-6 bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <h2 className="text-base font-extrabold text-slate-900">
            Tỷ trọng lượt click theo khóa học
          </h2>
          <p className="text-xs text-slate-400 font-medium mt-1 mb-6">
            Thanh càng dài thì khóa học càng được quan tâm
          </p>

          <div className="space-y-5">
            {TOP_COURSES.map((item) => {
              // Max click is 128
              const barWidth = item.clicks > 0 ? (item.clicks / 128) * 100 : 0;
              const barColor = item.isTop ? '#0d5f57' : '#5eead4';

              return (
                <div key={item.id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-800">
                    <span className="truncate pr-2">{item.title}</span>
                    <span className="shrink-0 text-slate-500 font-medium">
                      {item.clicks} click · {item.percent.toFixed(1)}%
                    </span>
                  </div>

                  <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex items-center">
                    {item.clicks > 0 ? (
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${barWidth}%`,
                          backgroundColor: barColor
                        }}
                      />
                    ) : (
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-300 ml-1" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

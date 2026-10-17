import React, { useState } from 'react';

const INDUSTRIES = [
  { id: 'IT', label: 'IT & Công nghệ' },
  { id: 'tourism', label: 'Du lịch & Khách sạn' },
  { id: 'logistics', label: 'Logistics & XNK' },
  { id: 'economics', label: 'Kinh tế & Tài chính' },
  { id: 'agriculture', label: 'Nông nghiệp' }
];

const MARKET_SKILLS_DATA = {
  IT: {
    skills: [
      { name: 'Python', demand: 91.1, supply: 32.4, gap: 58.7 },
      { name: 'Machine Learning', demand: 78.4, supply: 18.1, gap: 60.3 },
      { name: 'Data Analysis', demand: 74.2, supply: 29.8, gap: 44.4 },
      { name: 'ReactJS', demand: 68.7, supply: 38.3, gap: 30.4 },
      { name: 'Docker & DevOps', demand: 62.4, supply: 21.9, gap: 40.5 },
      { name: 'SQL & Database', demand: 58.7, supply: 44.6, gap: 14.1 },
      { name: 'Cloud (AWS/GCP)', demand: 52.6, supply: 15.5, gap: 37.1 },
      { name: 'Cybersecurity', demand: 48.4, supply: 12.3, gap: 36.1 }
    ],
    aiSuggestions: [
      {
        title: 'Machine Learning · thiếu 60,3%',
        content:
          'Cân nhắc nhận ứng viên có nền tảng Python và đào tạo ML trong 3 tháng đầu, thay vì bắt buộc kinh nghiệm ML trong mô tả công việc.'
      },
      {
        title: 'Python · thiếu 58,7%',
        content:
          'Đây là kỹ năng khan hiếm nhất. Nên nêu rõ lộ trình thử việc và cân nhắc mức lương cao hơn khung 15–25 triệu để cạnh tranh.'
      },
      {
        title: 'Cloud · thiếu 37,1%',
        content:
          'Chuyển Cloud từ "bắt buộc" sang "ưu tiên" để mở rộng nguồn ứng viên mà vẫn giữ chất lượng.'
      }
    ]
  },
  tourism: {
    skills: [
      { name: 'Tiếng Anh giao tiếp Quốc tế', demand: 88.5, supply: 41.2, gap: 47.3 },
      { name: 'Quản trị Khách sạn & PMS', demand: 72.4, supply: 33.0, gap: 39.4 },
      { name: 'Tiếng Trung du lịch', demand: 58.0, supply: 21.5, gap: 36.5 },
      { name: 'Xử lý khủng hoảng dịch vụ', demand: 65.2, supply: 38.1, gap: 27.1 },
      { name: 'Digital Marketing & OTA Channel', demand: 54.0, supply: 30.5, gap: 23.5 }
    ],
    aiSuggestions: [
      {
        title: 'Tiếng Anh giao tiếp · thiếu 47,3%',
        content:
          'Nguồn nhân lực thạo ngoại ngữ tại ĐBSCL có sự phân hóa lớn. Doanh nghiệp có thể tài trợ khóa đào tạo tiếng Anh chuyên ngành sau khi nhận việc.'
      },
      {
        title: 'PMS System · thiếu 39,4%',
        content:
          'Nên kiểm tra khả năng tiếp thu công nghệ thay vì đòi hỏi chứng chỉ phần mềm quản lý phòng cụ thể.'
      }
    ]
  },
  logistics: {
    skills: [
      { name: 'Quản lý chuỗi cung ứng SCM', demand: 82.0, supply: 29.4, gap: 52.6 },
      { name: 'Khai báo Hải quan & Incoterms', demand: 76.5, supply: 35.0, gap: 41.5 },
      { name: 'Phần mềm ERP / SAP Logistics', demand: 64.0, supply: 25.2, gap: 38.8 },
      { name: 'Tiếng Anh Logistics thương mại', demand: 71.0, supply: 38.5, gap: 32.5 },
      { name: 'Quản trị Kho bãi WMS', demand: 59.0, supply: 34.0, gap: 25.0 }
    ],
    aiSuggestions: [
      {
        title: 'Quản lý chuỗi cung ứng · thiếu 52,6%',
        content:
          'Ưu tiên tuyển các ứng viên có tư duy phân tích luồng vận tải và đào tạo nghiệp vụ cảng thực tế theo quy trình công ty.'
      },
      {
        title: 'Phần mềm ERP · thiếu 38,8%',
        content:
          'Có thể tuyển nhân sự biết Excel nâng cao hoặc các phần mềm kho cơ bản rồi chuyển giao hướng dẫn SAP.'
      }
    ]
  },
  economics: {
    skills: [
      { name: 'Phân tích Dữ liệu Power BI', demand: 85.0, supply: 32.0, gap: 53.0 },
      { name: 'Phần mềm Kế toán MISA / FAST', demand: 78.0, supply: 42.0, gap: 36.0 },
      { name: 'Phân tích Báo cáo Tài chính', demand: 68.0, supply: 35.0, gap: 33.0 },
      { name: 'Digital Marketing đa kênh', demand: 74.0, supply: 45.0, gap: 29.0 },
      { name: 'Kỹ năng Đàm phán & Thuyết trình', demand: 66.0, supply: 40.0, gap: 26.0 }
    ],
    aiSuggestions: [
      {
        title: 'Phân tích Power BI · thiếu 53,0%',
        content:
          'Nhu cầu BI tăng vọt nhưng sinh viên chủ yếu được dạy Excel. Cân nhắc hỗ trợ ứng viên nâng cấp kỹ năng Dashboarding trong kỳ thử việc.'
      }
    ]
  },
  agriculture: {
    skills: [
      { name: 'IoT & Cảm biến Nông nghiệp', demand: 75.0, supply: 18.0, gap: 57.0 },
      { name: 'Tiêu chuẩn VietGAP / GlobalGAP', demand: 82.0, supply: 34.0, gap: 48.0 },
      { name: 'Bảo quản chế biến sau thu hoạch', demand: 69.0, supply: 28.0, gap: 41.0 },
      { name: 'Thương mại điện tử nông sản', demand: 63.0, supply: 31.0, gap: 32.0 }
    ],
    aiSuggestions: [
      {
        title: 'IoT Nông nghiệp · thiếu 57,0%',
        content:
          'Kỹ sư nông nghiệp kết hợp công nghệ cao rất hiếm tại ĐBSCL. Hãy hợp tác trực tiếp với các viện nghiên cứu hoặc trường ĐH để đặt hàng trước.'
      }
    ]
  }
};

export default function EmployerMarketSkillsPage() {
  const [selectedIndustry, setSelectedIndustry] = useState('IT');

  const currentData = MARKET_SKILLS_DATA[selectedIndustry] || MARKET_SKILLS_DATA.IT;

  const getBadgeStyle = (gap) => {
    if (gap >= 40) {
      return 'bg-[#ffe4e6] text-[#e11d48]';
    } else if (gap >= 20) {
      return 'bg-[#fef3c7] text-[#b45309]';
    } else {
      return 'bg-[#dcfce7] text-[#0f766e]';
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Kỹ năng theo ngành · Thị trường
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Xem khoảng cách kỹ năng trên thị trường để điều chỉnh mô tả công việc.
        </p>
      </div>

      {/* ── 2. BỘ LỌC NGÀNH NGHỀ (HORIZONTAL PILLS) ── */}
      <div className="flex flex-wrap items-center gap-2.5">
        {INDUSTRIES.map((ind) => {
          const isActive = selectedIndustry === ind.id;
          return (
            <button
              key={ind.id}
              onClick={() => setSelectedIndustry(ind.id)}
              className={`px-5 py-2 rounded-full text-xs font-bold transition-all cursor-pointer ${
                isActive
                  ? 'bg-[#115e59] text-white shadow-xs'
                  : 'bg-white text-slate-700 border border-slate-200 hover:border-slate-300'
              }`}
            >
              {ind.label}
            </button>
          );
        })}
      </div>

      {/* ── 3. BỐ CỤC 2 CỘT (7 COLS & 5 COLS) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
        {/* CỘT TRÁI: NHU CẦU VÀ CUNG LAO ĐỘNG (7 COLS) */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <h2 className="text-base font-extrabold text-slate-900">
            Nhu cầu tuyển dụng và cung lao động
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-1 mb-6">
            Thanh teal: % tin tuyển dụng đòi hỏi · Thanh vàng: % sinh viên đạt yêu cầu
          </p>

          <div className="space-y-5">
            {currentData.skills.map((item, idx) => (
              <div key={idx} className="flex items-center gap-4">
                {/* Skill name */}
                <div className="w-36 shrink-0 text-sm font-bold text-slate-800 truncate">
                  {item.name}
                </div>

                {/* Double Bars Center */}
                <div className="flex-1 space-y-1.5">
                  {/* Top Bar: Teal (Demand) */}
                  <div className="flex items-center gap-2.5">
                    <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-[#0d5f57] h-full rounded-full transition-all duration-500"
                        style={{ width: `${item.demand}%` }}
                      />
                    </div>
                    <span className="text-[11.5px] font-extrabold text-[#0d5f57] w-12 text-right shrink-0">
                      {item.demand}%
                    </span>
                  </div>

                  {/* Bottom Bar: Gold/Amber (Supply) */}
                  <div className="flex items-center gap-2.5">
                    <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-[#f59e0b] h-full rounded-full transition-all duration-500"
                        style={{ width: `${item.supply}%` }}
                      />
                    </div>
                    <span className="text-[11.5px] font-extrabold text-[#b45309] w-12 text-right shrink-0">
                      {item.supply}%
                    </span>
                  </div>
                </div>

                {/* Gap Badge Right */}
                <div className="w-28 text-right shrink-0">
                  <span
                    className={`inline-block px-3 py-1 rounded-xl text-xs font-bold ${getBadgeStyle(
                      item.gap
                    )}`}
                  >
                    Thiếu {item.gap}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CỘT PHẢI: GỢI Ý TỪ AI (5 COLS) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <div className="text-[11px] font-black uppercase text-[#0d5f57] tracking-wider">
            GỢI Ý TỪ AI
          </div>
          <h2 className="text-base font-extrabold text-slate-900 mt-1 mb-5">
            Điều chỉnh tin tuyển dụng để thu hút ứng viên
          </h2>

          <div className="space-y-4">
            {currentData.aiSuggestions.map((sug, idx) => (
              <div
                key={idx}
                className="bg-[#f8fafc] rounded-2xl border border-slate-100 p-4.5"
              >
                <div className="text-sm font-extrabold text-slate-900 mb-1.5">
                  {sug.title}
                </div>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {sug.content}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

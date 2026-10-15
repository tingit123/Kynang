import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const INDUSTRY_TABS = [
  { id: 'IT', label: '💻 IT & Công nghệ' },
  { id: 'tourism', label: '✈️ Du lịch & Khách sạn' },
  { id: 'logistics', label: '📦 Logistics & XNK' },
  { id: 'economics', label: '📊 Kinh tế & Tài chính' },
  { id: 'agriculture', label: '🌾 Nông nghiệp' }
];

// Fallback data khi API chưa có dữ liệu chi tiết của ngành
const MOCK_MARKET_SKILLS = {
  IT: [
    { skill: 'Python / Django / FastAPI', demand: 91.2, supply: 32.5, gap: 58.7, type: 'Chuyên môn' },
    { skill: 'Docker & DevOps CI/CD', demand: 62.4, supply: 22.1, gap: 40.3, type: 'Chuyên môn' },
    { skill: 'Cloud (AWS / GCP / Azure)', demand: 52.8, supply: 15.6, gap: 37.2, type: 'Chuyên môn' },
    { skill: 'Cybersecurity & Bảo mật', demand: 48.6, supply: 12.3, gap: 36.3, type: 'Chuyên môn' },
    { skill: 'Kubernetes Container Orchestration', demand: 44.1, supply: 10.3, gap: 33.8, type: 'Chuyên môn' },
    { skill: 'Terraform & Infrastructure as Code', demand: 31.2, supply: 6.8, gap: 24.4, type: 'Chuyên môn' },
    { skill: 'Tiếng Anh giao tiếp chuyên ngành', demand: 60.4, supply: 42.1, gap: 18.3, type: 'Kỹ năng mềm' },
    { skill: 'SQL & Tối ưu hóa Database', demand: 49.7, supply: 36.2, gap: 13.5, type: 'Chuyên môn' }
  ],
  tourism: [
    { skill: 'Tiếng Anh giao tiếp Quốc tế', demand: 88.5, supply: 41.2, gap: 47.3, type: 'Kỹ năng mềm' },
    { skill: 'Quản trị Khách sạn & PMS System', demand: 72.4, supply: 33.0, gap: 39.4, type: 'Chuyên môn' },
    { skill: 'Tiếng Trung du lịch giao tiếp', demand: 58.0, supply: 21.5, gap: 36.5, type: 'Kỹ năng mềm' },
    { skill: 'Xử lý khủng hoảng & Chăm sóc khách hàng', demand: 65.2, supply: 38.1, gap: 27.1, type: 'Kỹ năng mềm' },
    { skill: 'Digital Marketing & OTA Channel', demand: 54.0, supply: 30.5, gap: 23.5, type: 'Chuyên môn' }
  ],
  logistics: [
    { skill: 'Quản lý chuỗi cung ứng SCM', demand: 82.0, supply: 29.4, gap: 52.6, type: 'Chuyên môn' },
    { skill: 'Khai báo Hải quan & Incoterms 2020', demand: 76.5, supply: 35.0, gap: 41.5, type: 'Chuyên môn' },
    { skill: 'Phần mềm ERP / SAP Logistics', demand: 64.0, supply: 25.2, gap: 38.8, type: 'Chuyên môn' },
    { skill: 'Tiếng Anh Logistics thương mại', demand: 71.0, supply: 38.5, gap: 32.5, type: 'Kỹ năng mềm' },
    { skill: 'Quản trị Kho bãi WMS', demand: 59.0, supply: 34.0, gap: 25.0, type: 'Chuyên môn' }
  ],
  economics: [
    { skill: 'Phân tích Dữ liệu Power BI / Tableau', demand: 85.0, supply: 32.0, gap: 53.0, type: 'Chuyên môn' },
    { skill: 'Phần mềm Kế toán MISA SME / FAST', demand: 78.0, supply: 42.0, gap: 36.0, type: 'Chuyên môn' },
    { skill: 'Phân tích Báo cáo Tài chính & Rủi ro', demand: 68.0, supply: 35.0, gap: 33.0, type: 'Chuyên môn' },
    { skill: 'Digital Marketing đa kênh & SEO', demand: 74.0, supply: 45.0, gap: 29.0, type: 'Chuyên môn' },
    { skill: 'Kỹ năng Đàm phán & Thuyết trình', demand: 66.0, supply: 40.0, gap: 26.0, type: 'Kỹ năng mềm' }
  ],
  agriculture: [
    { skill: 'IoT & Nông nghiệp thông minh', demand: 75.0, supply: 18.0, gap: 57.0, type: 'Chuyên môn' },
    { skill: 'Tiêu chuẩn VietGAP / GlobalGAP', demand: 82.0, supply: 34.0, gap: 48.0, type: 'Chuyên môn' },
    { skill: 'Bảo quản chế biến sau thu hoạch', demand: 69.0, supply: 28.0, gap: 41.0, type: 'Chuyên môn' },
    { skill: 'Thương mại điện tử nông sản', demand: 63.0, supply: 31.0, gap: 32.0, type: 'Chuyên môn' }
  ]
};

export default function EmployerMarketSkillsPage() {
  const [activeIndustry, setActiveIndustry] = useState('IT');
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  useEffect(() => {
    const fetchMarketSkills = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/skills/detailed?industry=${activeIndustry}`, {
          headers: getAuthHeaders()
        });

        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setSkills(data);
          } else {
            setSkills(MOCK_MARKET_SKILLS[activeIndustry] || []);
          }
        } else {
          setSkills(MOCK_MARKET_SKILLS[activeIndustry] || []);
        }
      } catch (err) {
        console.error(err);
        setSkills(MOCK_MARKET_SKILLS[activeIndustry] || []);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketSkills();
  }, [activeIndustry]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <h1 className="text-xl sm:text-2xl font-black text-slate-800 flex items-center gap-2">
          <span>🌐</span> Thống Kê Kỹ Năng Thị Trường Theo Ngành
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Dữ liệu phân tích từ hàng ngàn tin tuyển dụng thực tế & khảo sát nguồn cung lao động tại ĐBSCL giúp doanh nghiệp định vị JD chuẩn xác
        </p>

        {/* Industry Tabs */}
        <div className="flex flex-wrap gap-2 mt-5">
          {INDUSTRY_TABS.map((tab) => {
            const active = activeIndustry === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveIndustry(tab.id)}
                className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                  active
                    ? 'bg-[#0284c7] text-white shadow-md shadow-sky-600/20'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-extrabold text-slate-800">
              Top Kỹ Năng Đang Thiếu Hụt Trong Ngành ({activeIndustry})
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Sắp xếp theo tỷ lệ khoảng cách thiếu hụt (Skill Gap) giảm dần</p>
          </div>
          {/* Legend */}
          <div className="flex items-center gap-4 text-xs font-semibold">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-rose-500 inline-block" />
              <span className="text-slate-600">Nhu cầu tuyển (Demand)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />
              <span className="text-slate-600">Nguồn cung có sẵn (Supply)</span>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
            <p className="text-sm font-medium text-slate-500">Đang phân tích dữ liệu thị trường...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100">
                <tr>
                  <th className="py-3.5 px-4 font-bold w-12">#</th>
                  <th className="py-3.5 px-4 font-bold min-w-[200px]">Tên kỹ năng</th>
                  <th className="py-3.5 px-4 font-bold">Phân loại</th>
                  <th className="py-3.5 px-6 font-bold min-w-[280px]">Nhu cầu vs Nguồn cung (%)</th>
                  <th className="py-3.5 px-4 font-bold text-center">Khoảng cách (Gap)</th>
                  <th className="py-3.5 px-4 font-bold text-center">Mức độ thiếu</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {skills.map((s, idx) => {
                  const demandVal = s.demand || 0;
                  const supplyVal = s.supply || 0;
                  const gapVal = s.gap !== undefined ? s.gap : Math.max(0, demandVal - supplyVal);

                  const isSevere = gapVal > 30;
                  const isModerate = gapVal >= 15 && gapVal <= 30;

                  return (
                    <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3.5 px-4 font-black text-slate-400">
                        {idx < 3 ? (
                          <span className="w-6 h-6 rounded-md bg-amber-100 text-amber-800 text-xs flex items-center justify-center font-bold">
                            {idx + 1}
                          </span>
                        ) : (
                          idx + 1
                        )}
                      </td>
                      <td className="py-3.5 px-4 font-extrabold text-slate-800">
                        {s.skill || s.skill_name}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`text-[11px] font-bold px-2.5 py-1 rounded-md ${
                          s.type === 'Kỹ năng mềm'
                            ? 'bg-purple-50 text-purple-700 border border-purple-200'
                            : 'bg-sky-50 text-sky-700 border border-sky-200'
                        }`}>
                          {s.type || 'Chuyên môn'}
                        </span>
                      </td>
                      {/* Dual Progress Bar */}
                      <td className="py-3.5 px-6">
                        <div className="space-y-1.5">
                          {/* Demand Bar (Red) */}
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-rose-600 w-12 text-right shrink-0">
                              {demandVal.toFixed(1)}%
                            </span>
                            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                              <div
                                className="bg-rose-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(demandVal, 100)}%` }}
                              />
                            </div>
                          </div>
                          {/* Supply Bar (Green) */}
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-emerald-600 w-12 text-right shrink-0">
                              {supplyVal.toFixed(1)}%
                            </span>
                            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                              <div
                                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(supplyVal, 100)}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </td>
                      {/* Gap Value */}
                      <td className="py-3.5 px-4 text-center font-black text-sm text-rose-600">
                        +{gapVal.toFixed(1)}%
                      </td>
                      {/* Status Badge */}
                      <td className="py-3.5 px-4 text-center">
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                          isSevere
                            ? 'bg-rose-100 text-rose-800 border border-rose-200'
                            : isModerate
                            ? 'bg-amber-100 text-amber-800 border border-amber-200'
                            : 'bg-teal-100 text-teal-800 border border-teal-200'
                        }`}>
                          {isSevere ? '🔥 Rất thiếu' : isModerate ? '⚡ Thiếu vừa' : 'Ổn định'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Suggestion Card for Employers */}
      <div className="p-5 rounded-2xl bg-sky-50 border border-sky-200 text-sky-900 text-xs sm:text-sm flex items-start gap-3">
        <span className="text-xl shrink-0">💡</span>
        <div className="leading-relaxed">
          <strong className="block font-bold mb-0.5">Lời khuyên tuyển dụng từ AI:</strong>
          Các kỹ năng có tỷ lệ khoảng cách (Gap) trên 30% là những kỹ năng ứng viên trên thị trường đang rất khan hiếm. Nếu công ty yêu cầu những kỹ năng này trong tin tuyển dụng, hãy cân nhắc mức đãi ngộ hấp dẫn hơn hoặc đưa ra chính sách đào tạo bù đắp (OJT) cho ứng viên mới tốt nghiệp.
        </div>
      </div>
    </div>
  );
}

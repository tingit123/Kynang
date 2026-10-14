import React, { useState } from 'react';

const INDUSTRIES_DATA = [
  { id: 'IT', name: 'IT & Công nghệ', icon: '💻', count: '385 tin tuyển dụng', avgSalary: '15 – 35 Triệu' },
  { id: 'tourism', name: 'Du lịch & Khách sạn', icon: '✈️', count: '218 tin tuyển dụng', avgSalary: '8 – 20 Triệu' },
  { id: 'logistics', name: 'Logistics & Chuỗi Cung Ứng', icon: '📦', count: '241 tin tuyển dụng', avgSalary: '10 – 25 Triệu' },
  { id: 'economics', name: 'Kinh tế & Tài chính', icon: '📊', count: '156 tin tuyển dụng', avgSalary: '9 – 22 Triệu' },
  { id: 'agriculture', name: 'Nông nghiệp Công nghệ cao', icon: '🌾', count: '98 tin tuyển dụng', avgSalary: '8 – 18 Triệu' },
];

const ROLES_BY_INDUSTRY = {
  IT: [
    {
      id: 'it-python',
      name: 'Python Backend Developer',
      icon: '🐍',
      level: 'Junior / Middle',
      salary: '18 – 32 Triệu VNĐ/tháng',
      desc: 'Thiết kế RESTful API, xây dựng cơ sở dữ liệu và tích hợp mô hình AI Machine Learning vào hệ thống thực tế.',
      mustSkills: ['Python', 'FastAPI/Django', 'MySQL/PostgreSQL', 'Docker', 'Git'],
      niceSkills: ['Machine Learning', 'Redis', 'AWS/GCP', 'CI/CD']
    },
    {
      id: 'it-data',
      name: 'Data Analyst (Phân tích dữ liệu)',
      icon: '📈',
      level: 'Fresher / Junior',
      salary: '12 – 22 Triệu VNĐ/tháng',
      desc: 'Khai phá và làm sạch dữ liệu kinh doanh, xây dựng Dashboard trực quan bằng Power BI và truy vấn SQL tối ưu.',
      mustSkills: ['SQL', 'Power BI', 'Python (Pandas)', 'Excel nâng cao', 'Data Visualization'],
      niceSkills: ['Tableau', 'Kinh tế lượng', 'A/B Testing']
    },
    {
      id: 'it-react',
      name: 'Frontend Developer (ReactJS)',
      icon: '⚛️',
      level: 'Junior / Middle',
      salary: '15 – 28 Triệu VNĐ/tháng',
      desc: 'Xây dựng giao diện web phản hồi đa nền tảng, tối ưu trải nghiệm người dùng và kết nối API backend mượt mà.',
      mustSkills: ['ReactJS', 'JavaScript (ES6+)', 'TypeScript', 'HTML5/TailwindCSS', 'REST API'],
      niceSkills: ['Next.js', 'Redux Toolkit', 'UI/UX Design']
    },
    {
      id: 'it-aiml',
      name: 'AI / Machine Learning Engineer',
      icon: '🤖',
      level: 'Middle / Senior',
      salary: '25 – 45 Triệu VNĐ/tháng',
      desc: 'Huấn luyện và triển khai mô hình học máy, xử lý ngôn ngữ tự nhiên (NLP) và tích hợp các LLM lớn như Gemini/GPT-4o.',
      mustSkills: ['Python', 'TensorFlow/PyTorch', 'NLP & LLMs', 'Scikit-Learn', 'Math & Statistics'],
      niceSkills: ['MLOps', 'Vector Database', 'LangChain']
    }
  ],
  tourism: [
    {
      id: 'tour-guide',
      name: 'Hướng Dẫn Viên Du Lịch Quốc Tế',
      icon: '🚩',
      level: 'Mọi cấp độ',
      salary: '12 – 25 Triệu VNĐ/tháng',
      desc: 'Thuyết minh và hướng dẫn khách du lịch tham quan các tuyến ĐBSCL, am hiểu sâu sắc văn hóa sông nước miền Tây.',
      mustSkills: ['Thẻ HDV Quốc tế', 'Tiếng Anh lưu loát', 'Kỹ năng thuyết trình', 'Xử lý tình huống khẩn cấp'],
      niceSkills: ['Tiếng Pháp / Trung', 'Sơ cấp cứu', 'Kỹ năng hoạt náo']
    },
    {
      id: 'hotel-manager',
      name: 'Quản Lý Sảnh Khách Sạn (Front Office)',
      icon: '🛎️',
      level: 'Middle (2+ năm)',
      salary: '14 – 24 Triệu VNĐ/tháng',
      desc: 'Điều phối hoạt động nhận/trả phòng, quản lý doanh thu phòng và xử lý các phản hồi từ khách quốc tế.',
      mustSkills: ['Phần mềm Opera/Smile', 'Tiếng Anh B2/C1', 'Chăm sóc khách hàng VIP', 'Kỹ năng lãnh đạo nhóm'],
      niceSkills: ['Kỹ năng Upsell phòng', 'Quản lý doanh thu (Revenue Management)']
    }
  ],
  logistics: [
    {
      id: 'log-xnk',
      name: 'Chuyên Viên Xuất Nhập Khẩu',
      icon: '🚢',
      level: 'Junior / Middle',
      salary: '11 – 20 Triệu VNĐ/tháng',
      desc: 'Soạn thảo chứng từ xuất nhập khẩu (B/L, C/O, Invoice), làm việc với hãng tàu và thông quan hải quan hàng thủy sản.',
      mustSkills: ['Incoterms 2020', 'Khai hải quan VNACCS/ECUS5', 'Chứng từ ngoại thương', 'Tiếng Anh thương mại'],
      niceSkills: ['Hiểu biết FTA', 'Logistics lạnh (Cold Chain)']
    },
    {
      id: 'log-supply',
      name: 'Chuyên Viên Chuỗi Cung Ứng',
      icon: '🏭',
      level: 'Middle',
      salary: '15 – 26 Triệu VNĐ/tháng',
      desc: 'Lập kế hoạch nhu cầu vật tư, quản lý tồn kho và tối ưu chi phí vận tải cho hệ thống phân phối miền Tây.',
      mustSkills: ['Quản lý chuỗi cung ứng', 'Phần mềm ERP/SAP', 'Phân tích dữ liệu tồn kho', 'Đàm phán nhà cung cấp'],
      niceSkills: ['Lean Six Sigma', 'Quản trị rủi ro chuỗi cung ứng']
    }
  ],
  economics: [
    {
      id: 'eco-ktth',
      name: 'Kế Toán Tổng Hợp',
      icon: '📑',
      level: 'Middle (1-3 năm)',
      salary: '12 – 22 Triệu VNĐ/tháng',
      desc: 'Kiểm tra đối chiếu số liệu, lập báo cáo tài chính, kê khai thuế định kỳ và quyết toán thuế doanh nghiệp.',
      mustSkills: ['Kế toán doanh nghiệp', 'Phần mềm MISA SME', 'Báo cáo tài chính', 'Luật Thuế hiện hành', 'Excel nâng cao'],
      niceSkills: ['Tiếng Anh chuyên ngành', 'Phần mềm SAP/Fast']
    },
    {
      id: 'eco-mkt',
      name: 'Digital Marketing Specialist',
      icon: '📢',
      level: 'Junior / Middle',
      salary: '12 – 25 Triệu VNĐ/tháng',
      desc: 'Lên chiến lược và tối ưu các chiến dịch quảng cáo đa kênh (Facebook, Google, TikTok), phát triển nội dung số thu hút.',
      mustSkills: ['Facebook Ads', 'Google Ads', 'SEO Content', 'Google Analytics', 'Kỹ năng viết thông điệp'],
      niceSkills: ['Thiết kế Canva/Photoshop', 'Quay dựng video ngắn']
    }
  ],
  agriculture: [
    {
      id: 'agri-iot',
      name: 'Kỹ Sư Canh Tác Công Nghệ Cao',
      icon: '🌱',
      level: 'Fresher / Junior',
      salary: '10 – 18 Triệu VNĐ/tháng',
      desc: 'Ứng dụng công nghệ nhà màng, tưới nhỏ giọt tự động và cảm biến IoT vào quy trình trồng cây ăn trái & rau màu sạch.',
      mustSkills: ['Canh tác nhà màng', 'Vận hành hệ thống IoT', 'Chẩn đoán dinh dưỡng cây trồng', 'Tiêu chuẩn VietGAP/GlobalGAP'],
      niceSkills: ['Lập trình Arduino cơ bản', 'Quản lý chất lượng chuỗi nông sản']
    }
  ]
};

export default function IndustryExplorePage() {
  const [activeIndustry, setActiveIndustry] = useState('IT');
  const [selectedRole, setSelectedRole] = useState(ROLES_BY_INDUSTRY.IT[0]);

  const handleSelectIndustry = (indId) => {
    setActiveIndustry(indId);
    const roles = ROLES_BY_INDUSTRY[indId] || [];
    if (roles.length > 0) {
      setSelectedRole(roles[0]);
    }
  };

  const currentRoles = ROLES_BY_INDUSTRY[activeIndustry] || [];

  return (
    <div className="max-w-7xl mx-auto space-y-8 py-4">
      {/* ── HEADER ── */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-xs font-bold px-3 py-1 rounded-full border border-indigo-100">
          <span>🌐 Thị Trường Lao Động Cần Thơ</span>
          <span>•</span>
          <span>5 Ngành Trọng Điểm</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
          Khám Phá Yêu Cầu Kỹ Năng &amp; Mức Lương Theo Ngành Nghề
        </h1>
        <p className="text-slate-500 text-sm max-w-3xl leading-relaxed">
          Tra cứu chi tiết từng vị trí chuyên môn để biết các nhà tuyển dụng tại Cần Thơ đang yêu cầu bộ kỹ năng gì, mức lương trung bình bao nhiêu và cấp bậc nào phù hợp với bạn.
        </p>
      </div>

      {/* ── THANH CÔNG CỤ CHỌN NGÀNH NGHỀ (Tabs) ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {INDUSTRIES_DATA.map((ind) => {
          const isActive = activeIndustry === ind.id;
          return (
            <button
              key={ind.id}
              onClick={() => handleSelectIndustry(ind.id)}
              className={`p-4 rounded-xl text-left border transition-all flex flex-col justify-between gap-3 ${
                isActive
                  ? 'bg-teal-600 text-white border-teal-600 shadow-md shadow-teal-600/20 -translate-y-0.5'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-teal-300 hover:bg-teal-50/30'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl">{ind.icon}</span>
                {isActive && <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold">Đang xem</span>}
              </div>
              <div>
                <div className="font-extrabold text-sm">{ind.name}</div>
                <div className={`text-xs mt-0.5 ${isActive ? 'text-teal-100' : 'text-slate-400'}`}>
                  {ind.count}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* ── CHỌN VỊ TRÍ CHUYÊN MÔN (ROLE CHIPS) ── */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <span>🎯</span> Chọn Vị Trí Chuyên Môn Để Xem Yêu Cầu:
          </h2>
          <div className="flex flex-wrap gap-2.5 mt-3">
            {currentRoles.map((role) => {
              const isSelected = selectedRole.id === role.id;
              return (
                <button
                  key={role.id}
                  onClick={() => setSelectedRole(role)}
                  className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all ${
                    isSelected
                      ? 'bg-slate-900 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <span>{role.icon}</span>
                  <span>{role.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── CHI TIẾT VỊ TRÍ ĐÃ CHỌN (PANEL) ── */}
        {selectedRole && (
          <div className="border border-slate-200 rounded-xl p-6 bg-slate-50/60 space-y-6">
            {/* Header Vị Trí */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl p-3 bg-white rounded-2xl border border-slate-200 shadow-sm">
                  {selectedRole.icon}
                </span>
                <div>
                  <h3 className="text-xl font-extrabold text-slate-900">{selectedRole.name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Tiêu chuẩn mô hình hóa nghề nghiệp theo chuẩn Cần Thơ</p>
                </div>
              </div>

              {/* Thông tin nhanh: Mức lương & Cấp bậc */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1.5 rounded-lg border border-emerald-200">
                  💰 Lương: {selectedRole.salary}
                </span>
                <span className="bg-blue-100 text-blue-800 text-xs font-bold px-3 py-1.5 rounded-lg border border-blue-200">
                  🏅 Cấp bậc: {selectedRole.level}
                </span>
              </div>
            </div>

            {/* Mô tả nhiệm vụ */}
            <div className="text-sm text-slate-600 leading-relaxed bg-white p-4 rounded-xl border border-slate-200">
              <strong className="text-slate-800 font-bold block mb-1">Mô tả trọng tâm công việc:</strong>
              {selectedRole.desc}
            </div>

            {/* Bộ Kỹ Năng Yêu Cầu */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Kỹ Năng Bắt Buộc (Core) */}
              <div className="bg-white p-5 rounded-xl border border-rose-200 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-extrabold uppercase tracking-wider text-rose-800 flex items-center gap-1.5">
                    <span>⚡</span> Kỹ Năng Bắt Buộc (Core Skills)
                  </h4>
                  <span className="text-[11px] font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full">
                    Bắt buộc có
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedRole.mustSkills.map((sk) => (
                    <span
                      key={sk}
                      className="px-3 py-1.5 bg-rose-50 border border-rose-200 text-rose-900 font-semibold text-xs rounded-lg flex items-center gap-1"
                    >
                      <span>🔥</span> {sk}
                    </span>
                  ))}
                </div>
              </div>

              {/* Kỹ Năng Ưu Tiên / Bổ Trợ (Nice-to-have) */}
              <div className="bg-white p-5 rounded-xl border border-teal-200 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-extrabold uppercase tracking-wider text-teal-800 flex items-center gap-1.5">
                    <span>✨</span> Kỹ Năng Ưu Tiên (Nice to have)
                  </h4>
                  <span className="text-[11px] font-bold bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full">
                    Tăng lương +30%
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedRole.niceSkills.map((sk) => (
                    <span
                      key={sk}
                      className="px-3 py-1.5 bg-teal-50 border border-teal-200 text-teal-900 font-semibold text-xs rounded-lg flex items-center gap-1"
                    >
                      <span>⭐</span> {sk}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

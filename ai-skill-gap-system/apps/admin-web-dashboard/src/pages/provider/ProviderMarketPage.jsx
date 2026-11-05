import React, { useState, useMemo } from 'react';

// DỮ LIỆU THẬT CÓ SẴN CỦA DỰ ÁN (36 khóa học chuẩn từ COURSES_DATA + các khóa học của Mekong Skills)
const ALL_PROJECT_COURSES = [
  // ── 1. CÁC KHÓA HỌC CỦA ĐƠN VỊ ĐÀO TẠO (MEKONG SKILLS - CỦA TÔI) ──
  {
    id: 'MS001',
    title: 'Python Backend thực chiến',
    skill: 'Python',
    industry: 'IT',
    provider: 'Mekong Skills',
    platform: 'Mekong Skills',
    is_mine: true,
    clicks: 128,
    rating: 4.9,
    price: 'Miễn phí',
    url: 'https://mekongskills.vn/python-backend',
    outcomes: 'Xây dựng RESTful API chuyên nghiệp với FastAPI, tối ưu hóa truy vấn MySQL và triển khai Docker lên Cloud.',
    skills_acquired: 'Python, FastAPI, SQLAlchemy, RESTful API, Docker cơ bản',
    tools_acquired: 'FastAPI, Docker, Postman, MySQL Workbench, Git'
  },
  {
    id: 'MS002',
    title: 'Phân tích dữ liệu với Power BI',
    skill: 'Data Analysis',
    industry: 'economics',
    provider: 'Mekong Skills',
    platform: 'Mekong Skills',
    is_mine: true,
    clicks: 112,
    rating: 4.9,
    price: 'Miễn phí',
    url: 'https://mekongskills.vn/powerbi',
    outcomes: 'Xử lý và trực quan hóa dữ liệu kinh doanh đa chiều, tự động hóa báo cáo doanh số cho doanh nghiệp ĐBSCL.',
    skills_acquired: 'Power BI, DAX, Power Query, Data Modeling',
    tools_acquired: 'Microsoft Power BI Desktop, Excel, SQL Server'
  },
  {
    id: 'MS003',
    title: 'IELTS 6.5 cho sinh viên và người đi làm',
    skill: 'English',
    industry: 'tourism',
    provider: 'Mekong Skills',
    platform: 'Mekong Skills',
    is_mine: true,
    clicks: 86,
    rating: 4.8,
    price: 'Miễn phí',
    url: 'https://mekongskills.vn/ielts',
    outcomes: 'Phát triển toàn diện 4 kỹ năng Nghe - Nói - Đọc - Viết, tự tin giao tiếp quốc tế và phỏng vấn doanh nghiệp FDI.',
    skills_acquired: 'Academic English, Communication, Presentation Skills',
    tools_acquired: 'Cambridge IELTS Materials, Zoom'
  },
  {
    id: 'MS004',
    title: 'Giao tiếp và thuyết trình đỉnh cao',
    skill: 'Communication',
    industry: 'softskills',
    provider: 'Mekong Skills',
    platform: 'Mekong Skills',
    is_mine: true,
    clicks: 95,
    rating: 4.9,
    price: 'Miễn phí',
    url: 'https://mekongskills.vn/giao-tiep',
    outcomes: 'Nâng cao năng lực làm việc nhóm, kỹ năng thuyết phục đối tác và trình bày giải pháp trước ban giám đốc.',
    skills_acquired: 'Thuyết trình, Đàm phán, Kỹ năng lắng nghe tích cực',
    tools_acquired: 'Canva, PowerPoint, Mindmap'
  },

  // ── 2. CÁC KHÓA HỌC CÔNG KHAI CÓ SẴN TRONG DỰ ÁN (COURSES_DATA) ──
  // IT & CÔNG NGHỆ
  { id: 'C001', title: 'Python for Everybody Specialization', skill: 'Python', industry: 'IT', provider: 'Coursera × Univ. of Michigan', platform: 'Coursera', is_mine: false, clicks: 214, rating: 4.8, url: 'https://www.coursera.org/specializations/python' },
  { id: 'C002', title: 'Machine Learning Specialization', skill: 'Machine Learning', industry: 'IT', provider: 'Coursera × DeepLearning.AI', platform: 'Coursera', is_mine: false, clicks: 187, rating: 4.9, url: 'https://www.coursera.org/specializations/machine-learning-introduction' },
  { id: 'C003', title: 'Google Data Analytics Professional Certificate', skill: 'Data Analysis', industry: 'IT', provider: 'Coursera × Google', platform: 'Coursera', is_mine: false, clicks: 195, rating: 4.8, url: 'https://www.coursera.org/professional-certificates/google-data-analytics' },
  { id: 'C004', title: 'React – The Complete Guide (incl. Hooks, Redux)', skill: 'ReactJS', industry: 'IT', provider: 'Udemy × Maximilian', platform: 'Udemy', is_mine: false, clicks: 168, rating: 4.9, url: 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/' },
  { id: 'C005', title: 'Docker & Kubernetes: The Practical Guide', skill: 'Docker & DevOps', industry: 'IT', provider: 'Udemy × Academind', platform: 'Udemy', is_mine: false, clicks: 154, rating: 4.9, url: 'https://www.udemy.com/course/docker-kubernetes-the-practical-guide/' },
  { id: 'C006', title: 'SQL for Data Science', skill: 'SQL & Database', industry: 'IT', provider: 'Coursera × UC Davis', platform: 'Coursera', is_mine: false, clicks: 142, rating: 4.7, url: 'https://www.coursera.org/learn/sql-for-data-science' },
  { id: 'C007', title: 'Git & GitHub Bootcamp', skill: 'Git & CI/CD', industry: 'IT', provider: 'Udemy × Colt Steele', platform: 'Udemy', is_mine: false, clicks: 129, rating: 4.8, url: 'https://www.udemy.com/course/git-and-github-bootcamp/' },
  { id: 'C008', title: 'AWS Certified Cloud Practitioner Essentials', skill: 'Cloud (AWS/GCP)', industry: 'IT', provider: 'Amazon Web Services', platform: 'AWS Training', is_mine: false, clicks: 173, rating: 4.8, url: 'https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/' },
  { id: 'C009', title: 'Google Cybersecurity Professional Certificate', skill: 'Cybersecurity', industry: 'IT', provider: 'Coursera × Google', platform: 'Coursera', is_mine: false, clicks: 135, rating: 4.8, url: 'https://www.coursera.org/professional-certificates/google-cybersecurity' },
  { id: 'C010', title: 'AI Ethics: Global Perspectives', skill: 'AI Ethics', industry: 'IT', provider: 'edX × Harvard Online', platform: 'edX', is_mine: false, clicks: 98, rating: 4.7, url: 'https://www.edx.org/learn/artificial-intelligence/harvard-university-data-science-ethics' },

  // DU LỊCH & KHÁCH SẠN
  { id: 'C011', title: 'English for Tourism & Hospitality Management', skill: 'Tiếng Anh Du lịch', industry: 'tourism', provider: 'British Council × edX', platform: 'British Council', is_mine: false, clicks: 147, rating: 4.8, url: 'https://learnenglish.britishcouncil.org/' },
  { id: 'C012', title: 'Nghiệp Vụ Hướng Dẫn Viên Du Lịch Quốc Tế', skill: 'Hướng dẫn du lịch', industry: 'tourism', provider: 'Trường Du Lịch Saigontourist', platform: 'Saigontourist', is_mine: false, clicks: 162, rating: 4.9, url: 'https://saigontourist.edu.vn' },
  { id: 'C013', title: 'Hotel Management & Operations Specialization', skill: 'Quản lý khách sạn', industry: 'tourism', provider: 'edX × Cornell University', platform: 'edX', is_mine: false, clicks: 139, rating: 4.8, url: 'https://www.edx.org/learn/hospitality-management' },
  { id: 'C014', title: 'Customer Service Fundamentals in Hospitality', skill: 'Chăm sóc khách hàng', industry: 'tourism', provider: 'Coursera × Zendesk', platform: 'Coursera', is_mine: false, clicks: 153, rating: 4.8, url: 'https://www.coursera.org/learn/customer-service-fundamentals' },
  { id: 'C015', title: 'Khóa Học Tiếng Trung Giao Tiếp & Du Lịch HSK', skill: 'Tiếng Trung HSK', industry: 'tourism', provider: 'Coursera × Peking University', platform: 'Coursera', is_mine: false, clicks: 122, rating: 4.8, url: 'https://www.coursera.org/learn/hsk-4' },
  { id: 'C016', title: 'Thiết Kế & Điều Hành Tour Du Lịch Sinh Thái ĐBSCL', skill: 'Lên kế hoạch tour', industry: 'tourism', provider: 'Trung Tâm Đào Tạo ĐH Cần Thơ', platform: 'CTU Edu', is_mine: false, clicks: 178, rating: 4.8, url: 'https://ctu.edu.vn' },
  { id: 'C017', title: 'Hotel Revenue Management Strategy', skill: 'Revenue Management', industry: 'tourism', provider: 'Coursera × ESSEC', platform: 'Coursera', is_mine: false, clicks: 114, rating: 4.7, url: 'https://www.coursera.org/learn/hotel-distribution' },

  // LOGISTICS & XUẤT NHẬP KHẨU
  { id: 'C018', title: 'Supply Chain Principles & Global Logistics', skill: 'Quản lý chuỗi cung ứng', industry: 'logistics', provider: 'edX × MIT OpenCourseWare', platform: 'edX', is_mine: false, clicks: 188, rating: 4.9, url: 'https://www.edx.org/learn/supply-chain-management' },
  { id: 'C019', title: 'Thủ Tục Hải Quan Điện Tử & Khai Báo VNACCS/VCIS', skill: 'Nghiệp vụ hải quan', industry: 'logistics', provider: 'VCCI Chi Nhánh Cần Thơ', platform: 'VCCI', is_mine: false, clicks: 165, rating: 4.9, url: 'https://vccicantho.com.vn' },
  { id: 'C020', title: 'Nghiệp Vụ Xuất Nhập Khẩu & Chứng Từ Thực Chiến', skill: 'Xuất nhập khẩu', industry: 'logistics', provider: 'VCCI Cần Thơ × Viện Logistics', platform: 'VCCI', is_mine: false, clicks: 172, rating: 4.9, url: 'https://vccicantho.com.vn' },
  { id: 'C021', title: 'Warehouse Management & Inventory Control Systems', skill: 'Quản lý kho hàng', industry: 'logistics', provider: 'edX × Delft University', platform: 'edX', is_mine: false, clicks: 141, rating: 4.7, url: 'https://www.edx.org/learn/supply-chain-management' },
  { id: 'C022', title: 'SAP S/4HANA Supply Chain & Logistics Overview', skill: 'SAP/ERP', industry: 'logistics', provider: 'SAP Learning Official', platform: 'SAP', is_mine: false, clicks: 156, rating: 4.8, url: 'https://learning.sap.com/' },
  { id: 'C023', title: 'Incoterms 2020 Masterclass for Trade', skill: 'Incoterms 2020', industry: 'logistics', provider: 'International Chamber of Commerce', platform: 'ICC Academy', is_mine: false, clicks: 133, rating: 4.9, url: 'https://2go.iccwbo.org/incoterms-2020-english.html' },

  // KINH TẾ & TÀI CHÍNH
  { id: 'C024', title: 'Google Digital Marketing & E-Commerce Certificate', skill: 'Digital Marketing', industry: 'economics', provider: 'Google Skillshop', platform: 'Google', is_mine: false, clicks: 224, rating: 4.9, url: 'https://skillshop.exceedlms.com/' },
  { id: 'C025', title: 'Financial Analysis and Valuation', skill: 'Phân tích tài chính', industry: 'economics', provider: 'Coursera × Wharton School', platform: 'Coursera', is_mine: false, clicks: 191, rating: 4.9, url: 'https://www.coursera.org/learn/wharton-finance' },
  { id: 'C026', title: 'Microsoft Excel: Data Analysis with Tables & Pivot', skill: 'Excel nâng cao', industry: 'economics', provider: 'Microsoft Learn Official', platform: 'Microsoft Learn', is_mine: false, clicks: 205, rating: 4.8, url: 'https://learn.microsoft.com' },
  { id: 'C027', title: 'Khóa Học Kế Toán Doanh Nghiệp & Phần Mềm MISA SME', skill: 'Kế toán – MISA', industry: 'economics', provider: 'Học Viện MISA Academy', platform: 'MISA', is_mine: false, clicks: 182, rating: 4.8, url: 'https://amis.misa.vn/' },
  { id: 'C028', title: 'Data Visualization with Microsoft Power BI', skill: 'Data Visualization', industry: 'economics', provider: 'Microsoft Learn', platform: 'Microsoft Learn', is_mine: false, clicks: 167, rating: 4.8, url: 'https://learn.microsoft.com' },
  { id: 'C029', title: 'Corporate Financial Risk Management', skill: 'Quản trị rủi ro', industry: 'economics', provider: 'Coursera × EDHEC', platform: 'Coursera', is_mine: false, clicks: 126, rating: 4.7, url: 'https://www.coursera.org/learn/financial-risk-management-overview' },

  // NÔNG NGHIỆP CÔNG NGHỆ CAO
  { id: 'C030', title: 'Precision Agriculture & Smart Farm Technologies', skill: 'Công nghệ nông nghiệp', industry: 'agriculture', provider: 'Coursera × Penn State', platform: 'Coursera', is_mine: false, clicks: 143, rating: 4.8, url: 'https://www.coursera.org/learn/precision-agriculture' },
  { id: 'C031', title: 'IoT & Sensor Solutions for Modern Agriculture', skill: 'Drone & IoT', industry: 'agriculture', provider: 'Microsoft Learn IoT Hub', platform: 'Microsoft Learn', is_mine: false, clicks: 119, rating: 4.8, url: 'https://learn.microsoft.com' },
  { id: 'C032', title: 'QGIS & GIS Mapping for Agricultural Land Management', skill: 'GIS & Bản đồ nông nghiệp', industry: 'agriculture', provider: 'QGIS Official Training Project', platform: 'QGIS', is_mine: false, clicks: 137, rating: 4.8, url: 'https://www.qgis.org' },
  { id: 'C033', title: 'HACCP & ISO 22000 Food Safety Quality Management', skill: 'Chế biến thực phẩm', industry: 'agriculture', provider: 'HACCP Academy Vietnam', platform: 'HACCP', is_mine: false, clicks: 151, rating: 4.9, url: 'https://www.haccp.com/' },

  // KỸ NĂNG MỀM CHUNG
  { id: 'C034', title: 'Kỹ Năng Giao Tiếp & Thuyết Trình Chuyên Nghiệp', skill: 'Giao tiếp (Communication)', industry: 'softskills', provider: 'Viện Quản Trị PACE', platform: 'PACE', is_mine: false, clicks: 189, rating: 4.9, url: 'https://www.pace.edu.vn' },
  { id: 'C035', title: 'Creative & Critical Thinking in Business', skill: 'Tư duy phản biện', industry: 'softskills', provider: 'edX × University of Queensland', platform: 'edX', is_mine: false, clicks: 134, rating: 4.8, url: 'https://www.edx.org/learn/critical-thinking' },
  { id: 'C036', title: 'Work Smarter, Not Harder: Time Management', skill: 'Quản lý thời gian', industry: 'softskills', provider: 'Coursera × UC Irvine', platform: 'Coursera', is_mine: false, clicks: 148, rating: 4.7, url: 'https://www.coursera.org/learn/work-smarter-not-harder' }
];

export default function ProviderMarketPage() {
  const [courses] = useState(ALL_PROJECT_COURSES);
  const [unitFilter, setUnitFilter] = useState('all'); // 'all' | 'mine' | 'others'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('all');
  const [selectedSkill, setSelectedSkill] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 6;

  // Tính số lượng tổng thực tế của từng nhóm đơn vị
  const totalAllCount = courses.length;
  const totalMineCount = courses.filter((c) => c.is_mine).length;
  const totalOthersCount = courses.filter((c) => !c.is_mine).length;

  // Logic lọc dữ liệu
  const filtered = useMemo(() => {
    return courses.filter((c) => {
      if (unitFilter === 'mine' && !c.is_mine) return false;
      if (unitFilter === 'others' && c.is_mine) return false;

      if (selectedIndustry !== 'all') {
        const cInd = (c.industry || '').toLowerCase();
        const tInd = selectedIndustry.toLowerCase();
        if (cInd !== tInd && cInd !== 'all') return false;
      }

      if (selectedSkill !== 'all') {
        const cSkill = (c.skill || '').toLowerCase();
        const tSkill = selectedSkill.toLowerCase();
        if (!cSkill.includes(tSkill)) return false;
      }

      if (searchTerm) {
        const q = searchTerm.toLowerCase().trim();
        const mTitle = (c.title || '').toLowerCase().includes(q);
        const mProv = (c.provider || '').toLowerCase().includes(q);
        const mPlat = (c.platform || '').toLowerCase().includes(q);
        const mSkill = (c.skill || '').toLowerCase().includes(q);
        if (!mTitle && !mProv && !mPlat && !mSkill) return false;
      }

      return true;
    });
  }, [courses, unitFilter, selectedIndustry, selectedSkill, searchTerm]);

  // Tính toán phân trang
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const activePage = Math.min(currentPage, totalPages);

  const startIndex = (activePage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, filtered.length);
  const pageCourses = filtered.slice(startIndex, endIndex);

  // Xử lý chuyển trang
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Reset về trang 1 khi đổi bộ lọc
  const handleFilterChange = (setter, val) => {
    setter(val);
    setCurrentPage(1);
  };

  // Sinh danh sách các nút phân trang
  const renderPaginationButtons = () => {
    if (totalPages <= 1) return null;
    const pages = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (activePage > 3) pages.push('...');
      const start = Math.max(2, activePage - 1);
      const end = Math.min(totalPages - 1, activePage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (activePage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }

    return (
      <div className="flex items-center justify-center gap-2 mt-8 text-xs font-extrabold select-none">
        <button
          onClick={() => handlePageChange(activePage - 1)}
          disabled={activePage <= 1}
          className={`w-9 h-9 rounded-xl border flex items-center justify-center transition-colors ${
            activePage <= 1
              ? 'border-slate-200 bg-slate-50 text-slate-300 cursor-not-allowed'
              : 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50 cursor-pointer'
          }`}
          title="Trang trước"
        >
          &lsaquo;
        </button>

        {pages.map((p, idx) => {
          if (p === '...') {
            return (
              <span key={`dots-${idx}`} className="px-2 text-slate-400">
                ...
              </span>
            );
          }
          const isActive = p === activePage;
          return (
            <button
              key={`page-${p}`}
              onClick={() => handlePageChange(p)}
              className={`min-w-9 h-9 px-3 rounded-xl border text-xs transition-colors cursor-pointer ${
                isActive
                  ? 'border-[#0a5146] bg-[#0a5146] text-white font-black shadow-xs'
                  : 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50'
              }`}
            >
              {p}
            </button>
          );
        })}

        <button
          onClick={() => handlePageChange(activePage + 1)}
          disabled={activePage >= totalPages}
          className={`w-9 h-9 rounded-xl border flex items-center justify-center transition-colors ${
            activePage >= totalPages
              ? 'border-slate-200 bg-slate-50 text-slate-300 cursor-not-allowed'
              : 'border-slate-200 bg-white text-slate-800 hover:bg-slate-50 cursor-pointer'
          }`}
          title="Trang sau"
        >
          &rsaquo;
        </button>
      </div>
    );
  };

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
      <div className="bg-[#e6f7f5] border border-teal-200 rounded-2xl p-4 text-xs font-semibold text-teal-900">
        <span className="font-bold">Lưu ý:</span> đây là khu vực chỉ để xem. Bạn xem được các khóa học đã công khai của mọi đơn vị, nhưng chỉ sửa hoặc xóa được khóa học của mình trong mục <span className="font-bold underline cursor-pointer">Khóa học của tôi</span>.
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-3xl border border-slate-200 p-5 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-1 min-w-[280px]">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleFilterChange(setSearchTerm, e.target.value)}
              placeholder="Tìm theo tên khóa học, kỹ năng, đơn vị đào tạo..."
              className="flex-1 px-4 py-2.5 rounded-full border border-slate-300 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0a5146]"
            />
            <button
              onClick={() => setCurrentPage(1)}
              className="px-6 py-2.5 bg-[#0a5146] text-white rounded-full text-xs font-bold hover:bg-[#073d35] cursor-pointer"
            >
              Tìm
            </button>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <select
              value={selectedIndustry}
              onChange={(e) => handleFilterChange(setSelectedIndustry, e.target.value)}
              className="px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 bg-white cursor-pointer focus:outline-none"
            >
              <option value="all">Mọi ngành nghề</option>
              <option value="IT">IT & Công nghệ</option>
              <option value="tourism">Du lịch & Khách sạn</option>
              <option value="logistics">Logistics & XNK</option>
              <option value="economics">Kinh tế & Tài chính</option>
              <option value="agriculture">Nông nghiệp CNC</option>
              <option value="softskills">Kỹ năng mềm</option>
            </select>

            <select
              value={selectedSkill}
              onChange={(e) => handleFilterChange(setSelectedSkill, e.target.value)}
              className="px-4 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 bg-white cursor-pointer focus:outline-none"
            >
              <option value="all">Mọi kỹ năng</option>
              <option value="Python">Python</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Data Analysis">Data Analysis</option>
              <option value="ReactJS">ReactJS</option>
              <option value="Docker">Docker & DevOps</option>
              <option value="SQL">SQL & Database</option>
              <option value="English">Tiếng Anh chuyên ngành</option>
              <option value="Supply Chain">Chuỗi cung ứng</option>
              <option value="Digital Marketing">Digital Marketing</option>
            </select>
          </div>
        </div>

        {/* Dynamic Unit Filter Pills & Count Range */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleFilterChange(setUnitFilter, 'all')}
              className={`px-4 py-1.5 rounded-full font-extrabold transition-colors cursor-pointer ${
                unitFilter === 'all'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <span>Tất cả đơn vị</span>
              <span className={`ml-2 px-2 py-0.5 rounded-full text-[11px] ${unitFilter === 'all' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {totalAllCount}
              </span>
            </button>

            <button
              onClick={() => handleFilterChange(setUnitFilter, 'mine')}
              className={`px-4 py-1.5 rounded-full font-extrabold transition-colors cursor-pointer ${
                unitFilter === 'mine'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <span>Của tôi</span>
              <span className={`ml-2 px-2 py-0.5 rounded-full text-[11px] ${unitFilter === 'mine' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {totalMineCount}
              </span>
            </button>

            <button
              onClick={() => handleFilterChange(setUnitFilter, 'others')}
              className={`px-4 py-1.5 rounded-full font-extrabold transition-colors cursor-pointer ${
                unitFilter === 'others'
                  ? 'bg-[#0a5146] text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <span>Đơn vị khác</span>
              <span className={`ml-2 px-2 py-0.5 rounded-full text-[11px] ${unitFilter === 'others' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {totalOthersCount}
              </span>
            </button>
          </div>

          <span className="text-slate-500 font-bold">
            {filtered.length === 0 ? (
              'Hiển thị 0 trong 0 khóa học công khai'
            ) : (
              <>
                Hiển thị <strong className="text-slate-900">{startIndex + 1}–{endIndex}</strong> trong <strong className="text-slate-900">{filtered.length}</strong> khóa học công khai
              </>
            )}
          </span>
        </div>
      </div>

      {/* Course Grid */}
      {filtered.length === 0 ? (
        <div className="bg-white rounded-3xl border border-dashed border-slate-300 p-12 text-center">
          <div className="text-4xl mb-3">🔍</div>
          <h3 className="text-base font-extrabold text-slate-800">Không tìm thấy khóa học phù hợp</h3>
          <p className="text-xs text-slate-500 mt-1">
            Hãy thử điều chỉnh lại bộ lọc ngành nghề, kỹ năng hoặc từ khóa tìm kiếm.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pageCourses.map((c) => (
            <div
              key={c.id}
              className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col justify-between hover:shadow-md transition-all hover:-translate-y-0.5"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="px-3 py-1 rounded-full text-[11px] font-extrabold bg-teal-50 text-teal-800 border border-teal-100">
                    {c.skill}
                  </span>
                  <span
                    className={`px-3 py-0.5 rounded-full text-[10px] font-black uppercase ${
                      c.is_mine
                        ? 'bg-[#0a5146] text-[#5eead4]'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {c.is_mine ? 'Của bạn' : 'Công khai'}
                  </span>
                </div>

                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 rounded-md bg-[#0d9488] text-white text-xs font-black flex items-center justify-center">
                    {(c.platform || c.provider || 'C').charAt(0).toUpperCase()}
                  </div>
                  <span className="text-xs font-semibold text-slate-500 truncate max-w-[200px]">
                    {c.platform || c.provider}
                  </span>
                </div>

                <h3 className="text-base font-black text-slate-900 line-clamp-2 mb-4 leading-snug">
                  {c.title}
                </h3>
              </div>

              <div className="pt-4 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                  <div>
                    <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Lượt quan tâm
                    </span>
                    <span className="text-lg font-black text-slate-800">{c.clicks}</span>
                  </div>
                  <div className="text-right">
                    <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Đơn vị đào tạo
                    </span>
                    <span className="font-bold text-slate-700 max-w-[150px] truncate block">
                      {c.platform || c.provider}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => window.open(c.url, '_blank')}
                    className="flex-1 py-2 px-3 border border-slate-200 rounded-full text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer"
                  >
                    Chi tiết
                  </button>
                  {c.is_mine ? (
                    <button
                      type="button"
                      className="flex-1 py-2 px-3 border border-slate-200 rounded-full text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer"
                    >
                      Quản lý khóa học
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => window.open(c.url, '_blank')}
                      className="flex-1 py-2 px-3 bg-[#0a5146] text-white rounded-full text-xs font-bold hover:bg-[#073d35] cursor-pointer"
                    >
                      TRUY CẬP KHÓA HỌC
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dynamic Pagination */}
      {renderPaginationButtons()}
    </div>
  );
}

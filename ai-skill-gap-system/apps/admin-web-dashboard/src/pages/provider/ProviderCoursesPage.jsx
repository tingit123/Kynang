import React, { useState } from 'react';

const INITIAL_COURSES = [
  {
    id: 1,
    title: 'Python Backend thực chiến',
    skill: 'Python',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    priority: '1',
    clicks: 128,
    date: '12/10/2026',
    url: 'https://mekongskills.vn/python-backend',
    theme: {
      bg: '#e6f7f5',
      titleColor: '#0a5146',
      badgeColor: '#0a5146'
    }
  },
  {
    id: 2,
    title: 'FastAPI & Docker cho người mới',
    skill: 'Python',
    platform: 'Udemy',
    status: 'active',
    statusLabel: 'Đang phân phối',
    priority: '2',
    clicks: 74,
    date: '08/10/2026',
    url: 'https://www.udemy.com/course/fastapi-docker',
    theme: {
      bg: '#eff6ff',
      titleColor: '#1e3a8a',
      badgeColor: '#1e3a8a'
    }
  },
  {
    id: 3,
    title: 'Nhập môn Machine Learning',
    skill: 'Machine Learning',
    platform: 'Coursera',
    status: 'active',
    statusLabel: 'Đang phân phối',
    priority: '1',
    clicks: 96,
    date: '02/10/2026',
    url: 'https://www.coursera.org/learn/machine-learning-introduction',
    theme: {
      bg: '#f5f3ff',
      titleColor: '#581c87',
      badgeColor: '#581c87'
    }
  },
  {
    id: 4,
    title: 'Phân tích dữ liệu với Power BI',
    skill: 'Data Analysis',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    priority: '1',
    clicks: 61,
    date: '25/09/2026',
    url: 'https://mekongskills.vn/power-bi-analysis',
    theme: {
      bg: '#fff7ed',
      titleColor: '#9a3412',
      badgeColor: '#9a3412'
    }
  },
  {
    id: 5,
    title: 'IELTS 6.5 cho sinh viên',
    skill: 'English',
    platform: 'Mekong Skills',
    status: 'pending',
    statusLabel: 'Chờ duyệt',
    priority: '1',
    clicks: 0,
    date: '16/10/2026',
    url: 'https://mekongskills.vn/ielts-6-5',
    theme: {
      bg: '#fdf2f8',
      titleColor: '#9d174d',
      badgeColor: '#9d174d'
    }
  },
  {
    id: 6,
    title: 'Giao tiếp và thuyết trình',
    skill: 'Communication',
    platform: 'Mekong Skills',
    status: 'pending',
    statusLabel: 'Chờ duyệt',
    priority: '2',
    clicks: 0,
    date: '15/10/2026',
    url: 'https://mekongskills.vn/communication-skills',
    theme: {
      bg: '#fefce8',
      titleColor: '#854d0e',
      badgeColor: '#854d0e'
    }
  }
];

function getSkillTheme(skill) {
  const s = String(skill || '').toLowerCase();
  if (s.includes('python')) {
    return { bg: '#e6f7f5', titleColor: '#0a5146', badgeColor: '#0a5146' };
  } else if (s.includes('machine learning') || s.includes('ai')) {
    return { bg: '#f5f3ff', titleColor: '#581c87', badgeColor: '#581c87' };
  } else if (s.includes('data') || s.includes('analytics')) {
    return { bg: '#fff7ed', titleColor: '#9a3412', badgeColor: '#9a3412' };
  } else if (s.includes('english') || s.includes('tiếng anh')) {
    return { bg: '#fdf2f8', titleColor: '#9d174d', badgeColor: '#9d174d' };
  } else if (s.includes('communication') || s.includes('giao tiếp')) {
    return { bg: '#fefce8', titleColor: '#854d0e', badgeColor: '#854d0e' };
  } else if (s.includes('docker') || s.includes('devops')) {
    return { bg: '#eff6ff', titleColor: '#1e3a8a', badgeColor: '#1e3a8a' };
  }
  return { bg: '#e6f7f5', titleColor: '#0a5146', badgeColor: '#0a5146' };
}

export default function ProviderCoursesPage() {
  const [courses, setCourses] = useState(INITIAL_COURSES);
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'active' | 'pending'
  const [skillFilter, setSkillFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'table'
  const [showModal, setShowModal] = useState(false);

  // Form states for creating new course
  const [skill, setSkill] = useState('Python · IT');
  const [title, setTitle] = useState('');
  const [platform, setPlatform] = useState('Mekong Skills');
  const [priority, setPriority] = useState('1 (cao nhất)');
  const [url, setUrl] = useState('');

  // Counts
  const totalCount = courses.length;
  const activeCount = courses.filter((c) => c.status === 'active').length;
  const pendingCount = courses.filter((c) => c.status === 'pending').length;

  // Filtered courses
  const filteredCourses = courses.filter((c) => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (skillFilter !== 'all' && c.skill !== skillFilter) return false;
    return true;
  });

  const handleOpenModal = (prefillSkill = '') => {
    if (prefillSkill) {
      setSkill(`${prefillSkill} · IT`);
      setTitle(`${prefillSkill} thực chiến & ứng dụng`);
    } else {
      setSkill('Python · IT');
      setTitle('Python Backend thực chiến');
    }
    setPlatform('Mekong Skills');
    setPriority('1 (cao nhất)');
    setUrl('https://mekongskills.vn/python-backend');
    setShowModal(true);
  };

  const handleAddCourse = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Vui lòng nhập tên khóa học');
      return;
    }

    const cleanSkill = skill.split('·')[0].split('-')[0].trim();
    const today = new Date();
    const dateStr = `${String(today.getDate()).padStart(2, '0')}/${String(today.getMonth() + 1).padStart(2, '0')}/${today.getFullYear()}`;
    const cleanPriority = priority.replace(/[^0-9]/g, '') || '1';

    const newCourse = {
      id: Date.now(),
      title: title.trim(),
      skill: cleanSkill,
      platform: platform.trim() || 'Mekong Skills',
      status: 'pending',
      statusLabel: 'Chờ duyệt',
      priority: cleanPriority,
      clicks: 0,
      date: dateStr,
      url: url.trim() || 'https://mekongskills.vn',
      theme: getSkillTheme(cleanSkill)
    };

    setCourses([newCourse, ...courses]);
    setShowModal(false);
    alert(`Đã thêm khóa học "${newCourse.title}" thành công!\nTrạng thái: Chờ duyệt (sẽ được AI phân phối sau khi duyệt).`);
  };

  const handleDelete = (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa khóa học này?')) {
      setCourses(courses.filter((c) => c.id !== id));
    }
  };

  const handleOpenCourseUrl = (courseUrl, courseTitle) => {
    if (courseUrl && (courseUrl.startsWith('http://') || courseUrl.startsWith('https://'))) {
      window.open(courseUrl, '_blank', 'noopener,noreferrer');
    } else {
      alert(`Khóa học: ${courseTitle}\nĐường dẫn: ${courseUrl || 'Chưa cung cấp liên kết'}`);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* ── 1. HEADER TRANG ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Quản lý khóa học
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Đăng khóa học và gắn kỹ năng để hệ thống AI gợi ý đúng người cần.
          </p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="px-6 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider shadow-md shadow-teal-950/20 cursor-pointer whitespace-nowrap self-start sm:self-auto transition-all"
        >
          THÊM KHÓA HỌC
        </button>
      </div>

      {/* ── 2. BỘ LỌC TABS & DROPDOWN (KHỚP 100% ẢNH MẪU 1) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Cụm Tabs bên trái: Tất cả, Đang phân phối, Chờ duyệt */}
        <div className="flex items-center gap-2.5 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setStatusFilter('all')}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black cursor-pointer transition-all ${
              statusFilter === 'all'
                ? 'bg-[#0d5f57] text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>Tất cả</span>
            <span
              className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold ${
                statusFilter === 'all' ? 'bg-[#073d35] text-white' : 'bg-slate-100 text-slate-600'
              }`}
            >
              {totalCount}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('active')}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black cursor-pointer transition-all ${
              statusFilter === 'active'
                ? 'bg-[#0d5f57] text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>Đang phân phối</span>
            <span
              className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold ${
                statusFilter === 'active' ? 'bg-[#073d35] text-white' : 'bg-slate-100 text-slate-600'
              }`}
            >
              {activeCount}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('pending')}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black cursor-pointer transition-all ${
              statusFilter === 'pending'
                ? 'bg-[#0d5f57] text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>Chờ duyệt</span>
            <span
              className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold ${
                statusFilter === 'pending' ? 'bg-[#073d35] text-white' : 'bg-slate-100 text-slate-600'
              }`}
            >
              {pendingCount}
            </span>
          </button>
        </div>

        {/* Cụm bên phải: Dropdown chọn kỹ năng & Chuyển dạng xem */}
        <div className="flex items-center gap-3">
          <select
            value={skillFilter}
            onChange={(e) => setSkillFilter(e.target.value)}
            className="px-4 py-2 rounded-full border border-slate-200 text-xs font-bold text-slate-800 bg-white cursor-pointer focus:outline-none focus:border-[#0d5f57] min-w-[150px]"
          >
            <option value="all">Mọi kỹ năng</option>
            <option value="Python">Python</option>
            <option value="Machine Learning">Machine Learning</option>
            <option value="Data Analysis">Data Analysis</option>
            <option value="Docker & DevOps">Docker &amp; DevOps</option>
            <option value="English">English</option>
            <option value="Communication">Communication</option>
          </select>

          {/* Toggle View: Grid / Table */}
          <div className="inline-flex bg-slate-100 p-1 rounded-full border border-slate-200/80">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 rounded-full text-xs font-black transition-all cursor-pointer ${
                viewMode === 'grid'
                  ? 'bg-white text-[#0d5f57] shadow-xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
              title="Dạng thẻ"
            >
              ▦ Thẻ
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1 rounded-full text-xs font-black transition-all cursor-pointer ${
                viewMode === 'table'
                  ? 'bg-white text-[#0d5f57] shadow-xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
              title="Dạng bảng"
            >
              ☰ Bảng
            </button>
          </div>
        </div>
      </div>

      {/* ── 3A. DẠNG XEM THẺ GRID (KHỚP 100% ẢNH MẪU 1) ── */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((c) => (
            <div
              key={c.id}
              className="bg-white rounded-3xl border border-slate-200/80 p-4 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              {/* Header Banner có màu pastel mềm */}
              <div
                style={{ backgroundColor: c.theme?.bg || '#e6f7f5' }}
                className="rounded-2xl p-4.5 mb-4 min-h-[145px] flex flex-col justify-between"
              >
                {/* Hàng nhãn: Skill + Trạng thái */}
                <div className="flex items-center justify-between gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-black bg-white text-slate-800 shadow-2xs">
                    {c.skill}
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-[11px] font-black bg-white shadow-2xs ${
                      c.status === 'active' ? 'text-emerald-700' : 'text-amber-700'
                    }`}
                  >
                    {c.status === 'active' ? 'Đang phân phối' : 'Chờ duyệt'}
                  </span>
                </div>

                {/* Nền tảng & Tên khóa học */}
                <div className="mt-3">
                  <div className="text-[11px] font-bold text-slate-500 mb-1">
                    {c.platform}
                  </div>
                  <h3
                    style={{ color: c.theme?.titleColor || '#0a5146' }}
                    className="text-base font-black leading-snug line-clamp-2"
                  >
                    {c.title}
                  </h3>
                </div>
              </div>

              {/* Phần thông số bên dưới (ƯU TIÊN, LƯỢT CLICK, NGÀY ĐĂNG) */}
              <div>
                <div className="grid grid-cols-3 gap-2 mb-4 px-1 text-center sm:text-left">
                  <div>
                    <div className="text-[9.5px] font-black text-slate-400 uppercase tracking-wider">
                      ƯU TIÊN
                    </div>
                    <div className="text-sm font-black text-slate-900 mt-0.5">
                      {c.priority}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9.5px] font-black text-slate-400 uppercase tracking-wider">
                      LƯỢT CLICK
                    </div>
                    <div className="text-sm font-black text-slate-900 mt-0.5">
                      {c.clicks}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9.5px] font-black text-slate-400 uppercase tracking-wider">
                      NGÀY ĐĂNG
                    </div>
                    <div className="text-xs font-black text-slate-900 mt-1 whitespace-nowrap">
                      {c.date}
                    </div>
                  </div>
                </div>

                {/* Hàng nút hành động: XEM TRANG KHÓA HỌC & Xóa */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => handleOpenCourseUrl(c.url, c.title)}
                    className="flex-1 py-2 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white text-[11px] font-black uppercase tracking-wider cursor-pointer transition-colors text-center shadow-xs"
                  >
                    XEM TRANG KHÓA HỌC
                  </button>
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="px-3.5 py-2 rounded-full border border-rose-200 hover:border-rose-300 text-rose-600 hover:bg-rose-50 text-xs font-bold transition-all cursor-pointer"
                  >
                    Xóa
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── 3B. DẠNG XEM BẢNG TABLE (KHỚP 100% ẢNH MẪU 2) ── */}
      {viewMode === 'table' && (
        <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 mb-2 gap-2">
            <h2 className="text-base font-black text-slate-900">
              Khóa học đã đăng
            </h2>
            <span className="text-xs text-slate-500 font-semibold">
              <strong>{activeCount}</strong> đang phân phối · <strong>{pendingCount}</strong> chờ duyệt
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[11px] font-black text-slate-400 uppercase tracking-wider border-b border-slate-100">
                  <th className="pb-3.5 pl-2">TÊN KHÓA HỌC</th>
                  <th className="pb-3.5 px-4 w-44">KỸ NĂNG BÙ ĐẮP</th>
                  <th className="pb-3.5 px-4 w-36">TRẠNG THÁI</th>
                  <th className="pb-3.5 px-4 w-28 text-center">LƯỢT CLICK</th>
                  <th className="pb-3.5 pr-2 w-20 text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm font-semibold">
                {filteredCourses.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                    {/* Tên khóa học */}
                    <td className="py-4 pl-2 font-bold text-slate-900">
                      <div>{c.title}</div>
                      <div className="text-[11px] font-normal text-slate-400">{c.platform} · Đăng ngày {c.date}</div>
                    </td>

                    {/* Kỹ năng bù đắp */}
                    <td className="py-4 px-4">
                      <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700">
                        {c.skill}
                      </span>
                    </td>

                    {/* Trạng thái */}
                    <td className="py-4 px-4">
                      {c.status === 'active' ? (
                        <span className="text-xs font-bold text-emerald-700">
                          Đang phân phối
                        </span>
                      ) : (
                        <span className="text-xs font-bold text-amber-600">
                          Chờ duyệt
                        </span>
                      )}
                    </td>

                    {/* Lượt click */}
                    <td className="py-4 px-4 text-center font-black text-slate-800">
                      {c.clicks}
                    </td>

                    {/* Action: Xóa */}
                    <td className="py-4 pr-2 text-right">
                      <button
                        onClick={() => handleDelete(c.id)}
                        className="px-3.5 py-1 rounded-full border border-slate-200 hover:border-rose-300 text-slate-500 hover:text-rose-600 text-xs font-semibold transition-all cursor-pointer"
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── 4. MODAL THÊM KHÓA HỌC MỚI (KHỚP 100% ẢNH MẪU 2) ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4">
          <div className="bg-white rounded-3xl p-7 sm:p-8 max-w-lg w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 relative">
            {/* Nút đóng ✕ */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-6 right-6 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center font-black text-sm cursor-pointer"
            >
              ✕
            </button>

            <h2 className="text-lg font-black text-slate-900 mb-6">
              Thêm khóa học mới
            </h2>

            <form onSubmit={handleAddCourse} className="space-y-4">
              {/* Kỹ năng bù đắp */}
              <div>
                <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                  KỸ NĂNG BÙ ĐẮP
                </label>
                <select
                  value={skill}
                  onChange={(e) => setSkill(e.target.value)}
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0d5f57] cursor-pointer"
                >
                  <option value="Python · IT">Python · IT</option>
                  <option value="Machine Learning · IT">Machine Learning · IT</option>
                  <option value="Data Analysis · IT">Data Analysis · IT</option>
                  <option value="Docker & DevOps · IT">Docker &amp; DevOps · IT</option>
                  <option value="English · Ngoại ngữ">English · Ngoại ngữ</option>
                  <option value="Communication · Kỹ năng mềm">Communication · Kỹ năng mềm</option>
                  <option value="AI Ethics · IT">AI Ethics · IT</option>
                  <option value="Logistics · Vận tải & XNK">Logistics · Vận tải &amp; XNK</option>
                  <option value="Digital Marketing · Kinh tế">Digital Marketing · Kinh tế</option>
                  <option value="Customer Service · Du lịch">Customer Service · Du lịch</option>
                </select>
              </div>

              {/* Tên khóa học */}
              <div>
                <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                  TÊN KHÓA HỌC
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  placeholder="Python Backend thực chiến"
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                />
              </div>

              {/* Nền tảng & Độ ưu tiên (2 cột) */}
              <div className="grid grid-cols-2 gap-3.5">
                <div>
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    NỀN TẢNG
                  </label>
                  <input
                    type="text"
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    required
                    placeholder="Mekong Skills"
                    className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    ĐỘ ƯU TIÊN
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0d5f57] cursor-pointer"
                  >
                    <option value="1 (cao nhất)">1 (cao nhất)</option>
                    <option value="2 (trung bình)">2 (trung bình)</option>
                    <option value="3 (thấp)">3 (thấp)</option>
                  </select>
                </div>
              </div>

              {/* Đường dẫn trang đăng ký học */}
              <div>
                <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                  ĐƯỜNG DẪN TRANG ĐĂNG KÝ HỌC
                </label>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  placeholder="https://mekongskills.vn/python-backend"
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
                />
              </div>

              {/* Ghi chú */}
              <p className="text-xs text-slate-500 font-medium pt-1">
                Khóa học sẽ ở trạng thái Chờ duyệt cho đến khi quản trị viên phê duyệt.
              </p>

              {/* Bộ nút hành động */}
              <div className="pt-3 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 rounded-full border border-[#0d5f57] text-[#0d5f57] font-bold text-xs uppercase tracking-wider hover:bg-slate-50 cursor-pointer"
                >
                  HỦY
                </button>
                <button
                  type="submit"
                  className="px-7 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider shadow-md shadow-teal-900/15 cursor-pointer"
                >
                  ĐĂNG KHÓA HỌC
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

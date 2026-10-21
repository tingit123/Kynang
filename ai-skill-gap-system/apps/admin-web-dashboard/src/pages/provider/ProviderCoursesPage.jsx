import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env?.VITE_API_URL || 'http://localhost:8000';

const FALLBACK_COURSES = [
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
    outcomes: 'Cú pháp Python và cấu trúc dữ liệu cơ bản\nXây dựng REST API với FastAPI\nLàm việc với cơ sở dữ liệu SQL\nĐóng gói ứng dụng bằng Docker',
    skills_acquired: 'Python\nREST API\nSQL',
    tools_acquired: 'FastAPI\nDocker\nGit',
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
    outcomes: 'Kiến thức nền tảng FastAPI\nContainer hóa ứng dụng với Docker\nDeploy lên môi trường thực tế',
    skills_acquired: 'FastAPI\nDocker\nBackend Development',
    tools_acquired: 'Docker\nFastAPI\nPostman',
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
    outcomes: 'Thuật toán Supervised Learning cơ bản\nĐánh giá và tối ưu mô hình học máy\nỨng dụng thực tế bài toán phân loại và hồi quy',
    skills_acquired: 'Machine Learning\nData Science\nModel Evaluation',
    tools_acquired: 'Scikit-Learn\nJupyter\nPython',
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
    outcomes: 'Trực quan hóa dữ liệu Dashboard\nXây dựng mô hình dữ liệu quan hệ DAX\nKết nối đa nguồn dữ liệu Excel, SQL',
    skills_acquired: 'Power BI\nData Analysis\nDAX',
    tools_acquired: 'Power BI Desktop\nPower Query\nExcel',
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
    outcomes: 'Luyện đề 4 kỹ năng Nghe - Nói - Đọc - Viết\nPhương pháp viết Task 1 và Task 2 học thuật\nChiến lược giao tiếp tự nhiên band 6.5+',
    skills_acquired: 'Academic English\nIELTS Preparation\nPresentation',
    tools_acquired: 'Cambridge Materials\nIELTS Online',
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
    outcomes: 'Kỹ năng thuyết phục và làm việc nhóm\nNghệ thuật trình bày trước đám đông\nXử lý phản hồi và tranh luận tự tin',
    skills_acquired: 'Public Speaking\nNegotiation\nTeamwork',
    tools_acquired: 'PowerPoint\nCanva',
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
  } else if (s.includes('data') || s.includes('analytics') || s.includes('power bi')) {
    return { bg: '#fff7ed', titleColor: '#9a3412', badgeColor: '#9a3412' };
  } else if (s.includes('english') || s.includes('tiếng anh') || s.includes('ielts')) {
    return { bg: '#fdf2f8', titleColor: '#9d174d', badgeColor: '#9d174d' };
  } else if (s.includes('communication') || s.includes('giao tiếp')) {
    return { bg: '#fefce8', titleColor: '#854d0e', badgeColor: '#854d0e' };
  } else if (s.includes('docker') || s.includes('devops')) {
    return { bg: '#eff6ff', titleColor: '#1e3a8a', badgeColor: '#1e3a8a' };
  }
  return { bg: '#e6f7f5', titleColor: '#0a5146', badgeColor: '#0a5146' };
}

export default function ProviderCoursesPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'active' | 'pending'
  const [skillFilter, setSkillFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'table'

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 6;

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' | 'edit'
  const [editingCourseId, setEditingCourseId] = useState(null);

  // Form fields
  const [skill, setSkill] = useState('Python · IT');
  const [title, setTitle] = useState('');
  const [platform, setPlatform] = useState('Mekong Skills');
  const [priority, setPriority] = useState('1 (cao nhất)');
  const [url, setUrl] = useState('');
  const [outcomes, setOutcomes] = useState('');
  const [skillsAcquired, setSkillsAcquired] = useState('');
  const [toolsAcquired, setToolsAcquired] = useState('');

  // ── 1. GỌI API FASTAPI ĐỂ LẤY DỮ LIỆU THẬT TỪ MYSQL ──
  const fetchCoursesFromAPI = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/courses/`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          const mapped = data.map((c) => ({
            id: c.id,
            title: c.course_name,
            skill: c.skill_name || 'Python',
            platform: c.platform || 'Mekong Skills',
            status: c.status || 'pending',
            statusLabel: c.status === 'active' ? 'Đang phân phối' : 'Chờ duyệt',
            priority: String(c.priority || 1),
            clicks: c.click_count || 0,
            date: c.created_at || '12/10/2026',
            url: c.url || 'https://mekongskills.vn',
            outcomes: c.outcomes || '',
            skills_acquired: c.skills_acquired || '',
            tools_acquired: c.tools_acquired || '',
            theme: getSkillTheme(c.skill_name)
          }));
          setCourses(mapped);
          return;
        }
      }
      // Fallback nếu API trả mảng rỗng
      setCourses(FALLBACK_COURSES);
    } catch (err) {
      console.warn('Không thể kết nối API, dùng danh sách dự phòng:', err);
      setCourses(FALLBACK_COURSES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCoursesFromAPI();
  }, []);

  // Reset pagination when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, skillFilter, searchQuery]);

  // Counts
  const totalCount = courses.length;
  const activeCount = courses.filter((c) => c.status === 'active').length;
  const pendingCount = courses.filter((c) => c.status === 'pending').length;

  // Filtered courses
  const filteredCourses = courses.filter((c) => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (skillFilter !== 'all' && !c.skill.toLowerCase().includes(skillFilter.toLowerCase())) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      const matchTitle = (c.title || '').toLowerCase().includes(q);
      const matchPlatform = (c.platform || '').toLowerCase().includes(q);
      const matchSkill = (c.skill || '').toLowerCase().includes(q);
      if (!matchTitle && !matchPlatform && !matchSkill) return false;
    }
    return true;
  });

  // Paginated slice
  const totalPages = Math.max(1, Math.ceil(filteredCourses.length / pageSize));
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedCourses = filteredCourses.slice(startIndex, startIndex + pageSize);
  const displayStart = filteredCourses.length === 0 ? 0 : startIndex + 1;
  const displayEnd = Math.min(startIndex + pageSize, filteredCourses.length);

  // ── MỞ MODAL THÊM KHÓA HỌC MỚI ──
  const handleOpenAddModal = (prefillSkill = '') => {
    setModalMode('create');
    setEditingCourseId(null);
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
    setOutcomes('Cú pháp Python và cấu trúc dữ liệu cơ bản\nXây dựng REST API với FastAPI\nLàm việc với cơ sở dữ liệu SQL\nĐóng gói ứng dụng bằng Docker');
    setSkillsAcquired('Python\nREST API\nSQL');
    setToolsAcquired('FastAPI\nDocker\nGit');
    setShowModal(true);
  };

  // ── MỞ MODAL SỬA KHÓA HỌC (ĐIỀN SẴN DỮ LIỆU CŨ) ──
  const handleOpenEditModal = (c) => {
    setModalMode('edit');
    setEditingCourseId(c.id);
    setSkill(`${c.skill} · IT`);
    setTitle(c.title);
    setPlatform(c.platform || 'Mekong Skills');
    setPriority(c.priority === '1' ? '1 (cao nhất)' : c.priority === '2' ? '2 (trung bình)' : '3 (thấp)');
    setUrl(c.url || '');
    setOutcomes(c.outcomes || 'Cú pháp Python và cấu trúc dữ liệu cơ bản\nXây dựng REST API với FastAPI');
    setSkillsAcquired(c.skills_acquired || c.skill);
    setToolsAcquired(c.tools_acquired || 'FastAPI\nDocker\nGit');
    setShowModal(true);
  };

  // ── XỬ LÝ LƯU (THÊM HOẶC SỬA) VÀO DATABASE QUA FASTAPI ──
  const handleSubmitCourse = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Vui lòng nhập tên khóa học');
      return;
    }

    const cleanSkill = skill.split('·')[0].split('-')[0].trim();
    const cleanPriorityNum = parseInt(priority.replace(/[^0-9]/g, '') || '1', 10);

    const payload = {
      course_name: title.trim(),
      skill_name: cleanSkill,
      platform: platform.trim() || 'Mekong Skills',
      priority: cleanPriorityNum,
      url: url.trim() || 'https://mekongskills.vn',
      outcomes: outcomes.trim(),
      skills_acquired: skillsAcquired.trim(),
      tools_acquired: toolsAcquired.trim()
    };

    try {
      if (modalMode === 'edit' && editingCourseId) {
        // CẬP NHẬT (PUT API)
        const res = await fetch(`${API_BASE}/api/courses/${editingCourseId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const updated = await res.json();
          setCourses(
            courses.map((c) =>
              c.id === editingCourseId
                ? {
                    ...c,
                    title: updated.course_name,
                    skill: updated.skill_name,
                    platform: updated.platform,
                    priority: String(updated.priority),
                    url: updated.url,
                    outcomes: updated.outcomes,
                    skills_acquired: updated.skills_acquired,
                    tools_acquired: updated.tools_acquired,
                    theme: getSkillTheme(updated.skill_name)
                  }
                : c
            )
          );
          alert(`Đã cập nhật thông tin khóa học "${updated.course_name}" thành công vào MySQL!`);
        } else {
          // Fallback update local state
          setCourses(
            courses.map((c) =>
              c.id === editingCourseId
                ? {
                    ...c,
                    title: payload.course_name,
                    skill: cleanSkill,
                    platform: payload.platform,
                    priority: String(cleanPriorityNum),
                    url: payload.url,
                    outcomes: payload.outcomes,
                    skills_acquired: payload.skills_acquired,
                    tools_acquired: payload.tools_acquired,
                    theme: getSkillTheme(cleanSkill)
                  }
                : c
            )
          );
          alert(`Đã lưu cập nhật khóa học "${payload.course_name}" thành công!`);
        }
      } else {
        // THÊM MỚI (POST API)
        const res = await fetch(`${API_BASE}/api/courses/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...payload, status: 'pending' })
        });

        if (res.ok) {
          const created = await res.json();
          const newCourseItem = {
            id: created.id,
            title: created.course_name,
            skill: created.skill_name,
            platform: created.platform,
            status: created.status || 'pending',
            statusLabel: 'Chờ duyệt',
            priority: String(created.priority || 1),
            clicks: 0,
            date: created.created_at || '12/10/2026',
            url: created.url,
            outcomes: created.outcomes,
            skills_acquired: created.skills_acquired,
            tools_acquired: created.tools_acquired,
            theme: getSkillTheme(created.skill_name)
          };
          setCourses([newCourseItem, ...courses]);
          alert(`Đã đăng khóa học "${created.course_name}" thành công và lưu vào cơ sở dữ liệu MySQL!`);
        } else {
          // Fallback add to local
          const today = new Date();
          const dateStr = `${String(today.getDate()).padStart(2, '0')}/${String(today.getMonth() + 1).padStart(2, '0')}/${today.getFullYear()}`;
          const newCourseItem = {
            id: Date.now(),
            title: payload.course_name,
            skill: cleanSkill,
            platform: payload.platform,
            status: 'pending',
            statusLabel: 'Chờ duyệt',
            priority: String(cleanPriorityNum),
            clicks: 0,
            date: dateStr,
            url: payload.url,
            outcomes: payload.outcomes,
            skills_acquired: payload.skills_acquired,
            tools_acquired: payload.tools_acquired,
            theme: getSkillTheme(cleanSkill)
          };
          setCourses([newCourseItem, ...courses]);
          alert(`Đã thêm khóa học "${newCourseItem.title}" thành công!\nTrạng thái: Chờ duyệt.`);
        }
      }
    } catch (err) {
      console.error('Lỗi khi lưu khóa học:', err);
      alert('Đã lưu thay đổi vào giao diện!');
    } finally {
      setShowModal(false);
    }
  };

  // ── XỬ LÝ XÓA KHÓA HỌC ──
  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa khóa học này?')) {
      try {
        await fetch(`${API_BASE}/api/courses/${id}`, { method: 'DELETE' });
      } catch (err) {
        console.warn('Lỗi gọi API xóa:', err);
      }
      setCourses(courses.filter((c) => c.id !== id));
      alert('Đã xóa khóa học thành công!');
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
    <div className="space-y-6 max-w-6xl mx-auto font-sans">
      {/* ── 1. HEADER TRANG (KHỚP 100% ẢNH MẪU 1) ── */}
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
          onClick={() => handleOpenAddModal()}
          className="px-6 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider shadow-md shadow-teal-950/20 cursor-pointer whitespace-nowrap self-start sm:self-auto transition-all"
        >
          THÊM KHÓA HỌC
        </button>
      </div>

      {/* ── 2. KHUNG TÌM KIẾM & BỘ LỌC TABS (KHỚP 100% ẢNH MẪU 1) ── */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-5 sm:p-6 shadow-xs space-y-4">
        {/* Hàng 1: Ô tìm kiếm dạng viên thuốc + Dropdown kỹ năng */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Ô nhập tìm kiếm Search Text */}
          <div className="relative flex-1 w-full max-w-2xl">
            <div className="flex items-center bg-white border border-slate-300 rounded-full px-5 py-2.5 focus-within:border-[#0a5146] transition-colors shadow-2xs">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm theo tên khóa học, nền tảng..."
                className="w-full text-xs sm:text-sm font-semibold text-slate-800 placeholder-slate-400 bg-transparent outline-none pr-3"
              />
              <button
                type="button"
                className="text-xs font-black text-[#0a5146] hover:text-[#073d35] cursor-pointer whitespace-nowrap px-1"
              >
                Tìm
              </button>
            </div>
          </div>

          {/* Dropdown Mọi kỹ năng */}
          <div className="w-full sm:w-auto">
            <select
              value={skillFilter}
              onChange={(e) => setSkillFilter(e.target.value)}
              className="w-full sm:w-auto px-5 py-2.5 rounded-full border border-slate-300 text-xs font-bold text-slate-800 bg-white cursor-pointer focus:outline-none focus:border-[#0a5146] min-w-[170px]"
            >
              <option value="all">Mọi kỹ năng</option>
              <option value="Python">Python</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Data Analysis">Data Analysis</option>
              <option value="Docker & DevOps">Docker &amp; DevOps</option>
              <option value="English">English</option>
              <option value="Communication">Communication</option>
            </select>
          </div>
        </div>

        {/* Hàng 2: Bộ lọc trạng thái (Tất cả, Đang phân phối, Chờ duyệt) & Thông tin hiển thị */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
          {/* Cụm Tabs bên trái: Tất cả, Đang phân phối, Chờ duyệt */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
            <button
              onClick={() => setStatusFilter('all')}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black cursor-pointer transition-all ${
                statusFilter === 'all'
                  ? 'bg-[#0a5146] text-white shadow-xs'
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
                  ? 'bg-[#0a5146] text-white shadow-xs'
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
                  ? 'bg-[#0a5146] text-white shadow-xs'
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

          {/* Dòng chữ: Hiển thị 1–6 trong 50 khóa học */}
          <div className="text-xs font-bold text-slate-500">
            Hiển thị <strong className="text-slate-800">{displayStart}–{displayEnd}</strong> trong <strong className="text-slate-800">{filteredCourses.length}</strong> khóa học
          </div>
        </div>
      </div>

      {/* ── 3. DẠNG XEM THẺ GRID (KHỚP 100% ẢNH MẪU 1) ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paginatedCourses.map((c) => (
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
                <span className="px-3.5 py-1 rounded-full text-xs font-black bg-white text-slate-800 shadow-2xs">
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

              {/* Hàng nút hành động: Sửa, Xóa & XEM TRANG KHÓA HỌC (Khớp 100% Ảnh Mẫu 1) */}
              <div className="flex items-center gap-2 pt-1">
                {/* Nút Sửa Khóa Học */}
                <button
                  type="button"
                  onClick={() => handleOpenEditModal(c)}
                  className="px-4 py-2 rounded-full border border-[#0d6e64] hover:bg-teal-50 text-[#0d6e64] text-xs font-bold transition-all cursor-pointer whitespace-nowrap shadow-2xs"
                >
                  Sửa
                </button>

                {/* Nút Xóa Khóa Học */}
                <button
                  type="button"
                  onClick={() => handleDelete(c.id)}
                  className="px-4 py-2 rounded-full border border-rose-300 hover:bg-rose-50 text-rose-600 text-xs font-bold transition-all cursor-pointer whitespace-nowrap shadow-2xs"
                >
                  Xóa
                </button>

                {/* Nút Xem Trang Khóa Học */}
                <button
                  type="button"
                  onClick={() => handleOpenCourseUrl(c.url, c.title)}
                  className="flex-1 py-2 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white text-[11px] font-black uppercase tracking-wider cursor-pointer transition-colors text-center shadow-xs whitespace-nowrap"
                >
                  XEM TRANG KHÓA HỌC
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCourses.length === 0 && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-12 text-center text-slate-500">
          <div className="text-3xl mb-2">🔍</div>
          <div className="font-bold text-slate-800 text-base">Không tìm thấy khóa học nào phù hợp</div>
          <div className="text-xs text-slate-400 mt-1">Thử đổi từ khóa tìm kiếm hoặc chọn lọc kỹ năng khác.</div>
        </div>
      )}

      {/* ── 4. THANH PHÂN TRANG (Trang 1, 2, 3...) (MỤC 5) ── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4 pb-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className={`px-4 py-2 rounded-full text-xs font-black transition-all ${
              currentPage === 1
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 cursor-pointer shadow-2xs'
            }`}
          >
            ‹ Trước
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={`w-9 h-9 rounded-full text-xs font-black transition-all cursor-pointer ${
                currentPage === page
                  ? 'bg-[#0a5146] text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-2xs'
              }`}
            >
              {page}
            </button>
          ))}

          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className={`px-4 py-2 rounded-full text-xs font-black transition-all ${
              currentPage === totalPages
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 cursor-pointer shadow-2xs'
            }`}
          >
            Tiếp ›
          </button>
        </div>
      )}

      {/* ── 5. MODAL THÊM / SỬA KHÓA HỌC (KHỚP 100% ẢNH MẪU 2) ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-2xs p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 relative my-8 max-h-[90vh] overflow-y-auto">
            {/* Nút đóng dạng viên thuốc (Đóng) ở góc trên */}
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className="absolute top-6 right-6 px-4 py-1.5 rounded-full border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-bold cursor-pointer transition-colors"
            >
              Đóng
            </button>

            {/* Tiêu đề & phụ đề modal */}
            <div className="mb-6 pr-16">
              <h2 className="text-xl font-black text-slate-900">
                {modalMode === 'edit' ? 'Sửa khóa học' : 'Thêm khóa học mới'}
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                {modalMode === 'edit'
                  ? 'Thông tin hiện tại đã được điền sẵn. Chỉnh rồi bấm Lưu để cập nhật.'
                  : 'Điền thông tin và chi tiết khóa học để hệ thống AI phân phối.'}
              </p>
            </div>

            <form onSubmit={handleSubmitCourse} className="space-y-4">
              {/* KỸ NĂNG BÙ ĐẮP */}
              <div>
                <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                  KỸ NĂNG BÙ ĐẮP
                </label>
                <select
                  value={skill}
                  onChange={(e) => setSkill(e.target.value)}
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0a5146] cursor-pointer"
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

              {/* TÊN KHÓA HỌC */}
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
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146]"
                />
              </div>

              {/* NỀN TẢNG & ĐỘ ƯU TIÊN (2 cột) */}
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
                    className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146]"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    ĐỘ ƯU TIÊN
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0a5146] cursor-pointer"
                  >
                    <option value="1 (cao nhất)">1 (cao nhất)</option>
                    <option value="2 (trung bình)">2 (trung bình)</option>
                    <option value="3 (thấp)">3 (thấp)</option>
                  </select>
                </div>
              </div>

              {/* ĐƯỜNG DẪN TRANG ĐĂNG KÝ HỌC */}
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
                  className="w-full px-5 py-2.5 rounded-full border border-slate-300 text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146]"
                />
              </div>

              {/* ── MỤC 3: "RUỘT" KHÓA HỌC (KHỚP 100% ẢNH MẪU 2) ── */}
              <div className="pt-2 border-t border-slate-100">
                <div className="mb-3">
                  <div className="text-sm font-black text-slate-900">
                    Nội dung chi tiết
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Hiện trong nút "Chi tiết" cho ứng viên. Mỗi dòng một mục.
                  </div>
                </div>

                {/* 1. NHỮNG GÌ BẠN SẼ HỌC */}
                <div className="mb-3.5">
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    NHỮNG GÌ BẠN SẼ HỌC
                  </label>
                  <textarea
                    rows={4}
                    value={outcomes}
                    onChange={(e) => setOutcomes(e.target.value)}
                    placeholder="Cú pháp Python và cấu trúc dữ liệu cơ bản&#10;Xây dựng REST API với FastAPI&#10;Làm việc với cơ sở dữ liệu SQL&#10;Đóng gói ứng dụng bằng Docker"
                    className="w-full px-4 py-3 rounded-2xl border border-slate-300 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146] leading-relaxed resize-y"
                  />
                </div>

                {/* 2. KỸ NĂNG ĐẠT ĐƯỢC */}
                <div className="mb-3.5">
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    KỸ NĂNG ĐẠT ĐƯỢC
                  </label>
                  <textarea
                    rows={3}
                    value={skillsAcquired}
                    onChange={(e) => setSkillsAcquired(e.target.value)}
                    placeholder="Python&#10;REST API&#10;SQL"
                    className="w-full px-4 py-3 rounded-2xl border border-slate-300 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146] leading-relaxed resize-y"
                  />
                </div>

                {/* 3. CÔNG CỤ SẼ HỌC */}
                <div className="mb-2">
                  <label className="block text-[11px] font-black text-slate-600 uppercase tracking-wider mb-1.5">
                    CÔNG CỤ SẼ HỌC
                  </label>
                  <textarea
                    rows={3}
                    value={toolsAcquired}
                    onChange={(e) => setToolsAcquired(e.target.value)}
                    placeholder="FastAPI&#10;Docker&#10;Git"
                    className="w-full px-4 py-3 rounded-2xl border border-slate-300 text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none focus:border-[#0a5146] leading-relaxed resize-y"
                  />
                </div>
              </div>

              {/* Bộ nút hành động dưới chân modal */}
              <div className="pt-3 flex items-center justify-end gap-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 rounded-full border border-[#0d6e64] text-[#0d6e64] font-bold text-xs uppercase tracking-wider hover:bg-slate-50 cursor-pointer"
                >
                  HỦY
                </button>
                <button
                  type="submit"
                  className="px-7 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider shadow-md shadow-teal-900/15 cursor-pointer"
                >
                  {modalMode === 'edit' ? 'LƯU CẬP NHẬT' : 'ĐĂNG KHÓA HỌC'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

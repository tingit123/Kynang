import React, { useState } from 'react';

const INITIAL_COURSES = [
  {
    id: 1,
    title: 'Python Backend thực chiến',
    skill: 'Python',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    clicks: 128
  },
  {
    id: 2,
    title: 'FastAPI & Docker cho người mới',
    skill: 'Python',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    clicks: 74
  },
  {
    id: 3,
    title: 'Nhập môn Machine Learning',
    skill: 'Machine Learning',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    clicks: 96
  },
  {
    id: 4,
    title: 'Phân tích dữ liệu với Power BI',
    skill: 'Data Analysis',
    platform: 'Mekong Skills',
    status: 'active',
    statusLabel: 'Đang phân phối',
    clicks: 61
  },
  {
    id: 5,
    title: 'IELTS 6.5 cho sinh viên',
    skill: 'English',
    platform: 'Mekong Skills',
    status: 'pending',
    statusLabel: 'Chờ duyệt',
    clicks: 0
  },
  {
    id: 6,
    title: 'Giao tiếp và thuyết trình',
    skill: 'Communication',
    platform: 'Mekong Skills',
    status: 'pending',
    statusLabel: 'Chờ duyệt',
    clicks: 0
  }
];

export default function ProviderCoursesPage() {
  const [courses, setCourses] = useState(INITIAL_COURSES);
  const [showModal, setShowModal] = useState(false);

  // Form states matching mockup
  const [skill, setSkill] = useState('Python - IT');
  const [title, setTitle] = useState('Python Backend thực chiến');
  const [platform, setPlatform] = useState('Mekong Skills');
  const [priority, setPriority] = useState('1 (cao nhất)');
  const [url, setUrl] = useState('https://mekongskills.vn/python-backend');

  const activeCount = courses.filter((c) => c.status === 'active').length;
  const pendingCount = courses.filter((c) => c.status === 'pending').length;

  const handleOpenModal = () => {
    setTitle('Python Backend thực chiến');
    setSkill('Python - IT');
    setPlatform('Mekong Skills');
    setPriority('1 (cao nhất)');
    setUrl('https://mekongskills.vn/python-backend');
    setShowModal(true);
  };

  const handleAddCourse = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const skillName = skill.split('-')[0].trim();
    const newCourse = {
      id: Date.now(),
      title: title.trim(),
      skill: skillName,
      platform: platform.trim() || 'Mekong Skills',
      status: 'pending',
      statusLabel: 'Chờ duyệt',
      clicks: 0
    };

    setCourses([...courses, newCourse]);
    setShowModal(false);
  };

  const handleDelete = (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa khóa học này?')) {
      setCourses(courses.filter((c) => c.id !== id));
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Quản lý khóa học
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Đăng khóa học và gắn kỹ năng để hệ thống AI gợi ý đúng người cần.
          </p>
        </div>
        <button
          onClick={handleOpenModal}
          className="px-6 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-extrabold text-xs uppercase tracking-wider shadow-md shadow-teal-900/15 cursor-pointer whitespace-nowrap self-start sm:self-auto"
        >
          THÊM KHÓA HỌC
        </button>
      </div>

      {/* ── 2. BẢNG KHÓA HỌC ĐÃ ĐĂNG (TABLE CARD) ── */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-7 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 mb-2 gap-2">
          <h2 className="text-base font-extrabold text-slate-900">
            Khóa học đã đăng
          </h2>
          <span className="text-xs text-slate-500 font-medium">
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
              {courses.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                  {/* Tên khóa học */}
                  <td className="py-4 pl-2 font-bold text-slate-900">
                    {c.title}
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
                  <td className="py-4 px-4 text-center font-bold text-slate-800">
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

      {/* ── 3. MODAL THÊM KHÓA HỌC MỚI (KHỚP 100% MOCKUP IMAGE 1) ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4">
          <div className="bg-white rounded-3xl p-7 sm:p-8 max-w-lg w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 relative">
            {/* Close button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-6 right-6 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center font-bold text-sm cursor-pointer"
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
                  <option value="Python - IT">Python - IT</option>
                  <option value="Machine Learning - IT">Machine Learning - IT</option>
                  <option value="Data Analysis - IT">Data Analysis - IT</option>
                  <option value="Docker & DevOps - IT">Docker &amp; DevOps - IT</option>
                  <option value="English - Ngoại ngữ">English - Ngoại ngữ</option>
                  <option value="Communication - Kỹ năng mềm">Communication - Kỹ năng mềm</option>
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
                  className="px-7 py-2.5 rounded-full bg-[#0a5146] hover:bg-[#073d35] text-white font-extrabold text-xs uppercase tracking-wider shadow-md shadow-teal-900/15 cursor-pointer"
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

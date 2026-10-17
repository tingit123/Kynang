import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const INDUSTRIES = [
  'IT & Công nghệ',
  'Du lịch & Khách sạn',
  'Logistics & Xuất nhập khẩu',
  'Kinh tế & Tài chính',
  'Nông nghiệp công nghệ cao'
];

/**
 * TASK 2: Quản Lý Tin Tuyển Dụng (EmployerJobsPage.jsx)
 * - Read: Gọi GET /api/jobs/my-jobs, render danh sách tin, hiển thị ngành, lương, tags kỹ năng.
 * - Create: Modal đăng tin, pre-fill công ty, xử lý nhập tag kỹ năng bằng phím Enter, gọi POST /api/jobs/ và tự động load lại.
 * - Delete: Nút xóa kèm confirm alert, gọi DELETE /api/jobs/{id}, cập nhật state bằng .filter().
 */
export default function EmployerJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form Fields
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('TP. Cần Thơ');
  const [industry, setIndustry] = useState('IT & Công nghệ');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [description, setDescription] = useState('');

  // Tag input for skills
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState([]);

  // Lấy sẵn tên công ty từ localStorage khi mở trang
  useEffect(() => {
    try {
      const rawUser = localStorage.getItem('current_user');
      if (rawUser) {
        const parsed = JSON.parse(rawUser);
        const defaultCompany = parsed.company_name || parsed.full_name || '';
        setCompany(defaultCompany);
      }
    } catch (e) {
      console.error('Lỗi đọc localStorage:', e);
    }
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  // 2.1. Đọc danh sách tin tuyển dụng của công ty (Read)
  const fetchMyJobs = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch(`${API_BASE}/api/jobs/my-jobs`, {
        headers: getAuthHeaders()
      });

      if (res.ok) {
        const data = await res.json();
        setJobs(Array.isArray(data) ? data : []);
      } else if (res.status === 401) {
        setErrorMsg('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      } else {
        setErrorMsg('Không thể tải danh sách tin tuyển dụng của công ty.');
      }
    } catch (err) {
      console.error('Lỗi kết nối my-jobs:', err);
      setErrorMsg('Lỗi kết nối máy chủ API backend khi tải danh sách tin.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyJobs();
  }, []);

  // 2.3. Xử lý Tags Kỹ năng (Nhấn Enter hoặc bấm Thêm để đưa vào mảng skills)
  const handleAddSkill = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCurrentSkill();
    }
  };

  const addCurrentSkill = () => {
    const trimmed = skillInput.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills([...skills, trimmed]);
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  // 2.4. Submit tin mới (Create)
  const handleSubmitJob = async (e) => {
    e.preventDefault();

    if (!title.trim() || !company.trim()) {
      alert('Vui lòng nhập đầy đủ tiêu đề tin và tên công ty.');
      return;
    }

    setSubmitting(true);

    const payload = {
      title: title.trim(),
      company: company.trim(),
      location: location.trim() || 'TP. Cần Thơ',
      industry,
      description: description.trim(),
      salary_min: salaryMin ? parseInt(salaryMin, 10) : null,
      salary_max: salaryMax ? parseInt(salaryMax, 10) : null,
      skills: skills
    };

    try {
      const res = await fetch(`${API_BASE}/api/jobs/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSuccessMsg('🎉 Đăng tin tuyển dụng thành công!');
        setIsModalOpen(false);

        // Reset form (giữ lại công ty)
        setTitle('');
        setSalaryMin('');
        setSalaryMax('');
        setDescription('');
        setSkills([]);
        setSkillInput('');

        // Tự động load lại danh sách mà không cần F5
        fetchMyJobs();

        setTimeout(() => setSuccessMsg(''), 4000);
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(errData.detail || 'Không thể đăng tin tuyển dụng. Vui lòng thử lại.');
      }
    } catch (err) {
      console.error('Lỗi khi gửi POST job:', err);
      alert('Lỗi kết nối máy chủ khi tạo tin tuyển dụng.');
    } finally {
      setSubmitting(false);
    }
  };

  // 2.5. Xóa tin tuyển dụng (Delete)
  const handleDeleteJob = async (jobId, jobTitle) => {
    const confirmed = window.confirm(`Bạn có chắc chắn muốn xóa vĩnh viễn tin tuyển dụng: "${jobTitle}"?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (res.ok) {
        setSuccessMsg(`🗑️ Đã xóa thành công tin tuyển dụng #${jobId}.`);
        // Dùng .filter() để loại Job đó khỏi State ngay lập tức
        setJobs(prevJobs => prevJobs.filter(j => j.id !== jobId));
        setTimeout(() => setSuccessMsg(''), 3500);
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(errData.detail || 'Không thể xóa tin tuyển dụng này.');
      }
    } catch (err) {
      console.error('Lỗi khi gọi DELETE job:', err);
      alert('Lỗi mạng khi xóa tin tuyển dụng.');
    }
  };

  const formatSalary = (min, max) => {
    if (!min && !max) return 'Thỏa thuận';
    if (min && !max) return `Từ ${(min / 1000000).toFixed(0)} triệu VNĐ`;
    if (!min && max) return `Lên tới ${(max / 1000000).toFixed(0)} triệu VNĐ`;
    return `${(min / 1000000).toFixed(0)} - ${(max / 1000000).toFixed(0)} triệu VNĐ`;
  };

  return (
    <div className="space-y-6">
      {/* ── HEADER TRANG VÀ NÚT TẠO TIN ── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 bg-sky-50 text-[#0284c7] rounded-xl text-xl">📝</span>
            <h1 className="text-xl sm:text-2xl font-black text-slate-800 tracking-tight">
              Quản Lý Tin Tuyển Dụng
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Đăng tin tuyển dụng và thiết lập các kỹ năng trọng tâm để AI so khớp với ứng viên tiềm năng
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold text-sm shadow-md shadow-sky-600/20 active:scale-98 transition-all cursor-pointer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span>+ Đăng Tin Mới</span>
        </button>
      </div>

      {/* Thông báo Thành công / Thất bại */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold rounded-xl flex items-center gap-2">
          <span>{successMsg}</span>
        </div>
      )}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-xl flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ── DANH SÁCH TIN TUYỂN DỤNG (READ) ── */}
      {loading ? (
        <div className="p-16 text-center bg-white rounded-2xl border border-slate-200 shadow-xs">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
          <p className="text-sm font-semibold text-slate-500">Đang tải danh sách tin tuyển dụng...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-16 text-center bg-white rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-5xl mb-3">📭</div>
          <h3 className="text-base font-extrabold text-slate-700">Chưa có tin tuyển dụng nào được đăng</h3>
          <p className="text-xs text-slate-400 mt-1 mb-5">
            Hãy bắt đầu đăng tin để tiếp cận mạng lưới ứng viên và kích hoạt chẩn đoán AI.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-5 py-2.5 bg-[#0284c7] hover:bg-[#0369a1] text-white text-xs font-bold rounded-xl shadow-xs transition-colors"
          >
            + Đăng Tin Đầu Tiên
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-2xl p-5 border border-slate-200 hover:border-sky-300 hover:shadow-lg transition-all duration-200 flex flex-col justify-between group"
            >
              <div>
                {/* Header Card: Ngành nghề & Nút Xóa */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 bg-sky-50 text-sky-700 rounded-lg border border-sky-100">
                    {job.industry || 'Ngành nghề'}
                  </span>
                  <button
                    onClick={() => handleDeleteJob(job.id, job.title)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                    title="Xóa tin tuyển dụng này"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Tiêu đề & Công ty */}
                <h3 className="text-base font-extrabold text-slate-800 group-hover:text-[#0284c7] transition-colors line-clamp-2">
                  {job.title}
                </h3>
                <div className="text-xs text-slate-500 font-medium mt-1.5 flex items-center gap-1.5">
                  <span className="truncate">🏢 {job.company}</span>
                  <span>•</span>
                  <span className="shrink-0">📍 {job.location || 'TP. Cần Thơ'}</span>
                </div>

                {/* Mức lương */}
                <div className="mt-3 text-xs font-bold text-emerald-700 bg-emerald-50/80 border border-emerald-100 px-3 py-1.5 rounded-lg inline-block">
                  💰 {formatSalary(job.salary_min, job.salary_max)}
                </div>

                {/* Mô tả tóm tắt */}
                {job.description && (
                  <p className="mt-3 text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {job.description}
                  </p>
                )}

                {/* Thẻ Kỹ năng yêu cầu (Tags) */}
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Kỹ năng yêu cầu:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {job.skills && job.skills.length > 0 ? (
                      job.skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-[11px] text-slate-400 italic">Chưa gắn thẻ kỹ năng</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer Thẻ */}
              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Mã tin: #{job.id}</span>
                <span className="font-bold text-emerald-600 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Đang mở tuyển
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── MODAL FORM ĐĂNG TIN MỚI (CREATE) ──                    */}
      {/* ══════════════════════════════════════════════════════════ */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[92vh] overflow-y-auto border border-slate-100 p-6 sm:p-8">
            {/* Header Modal */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
              <div>
                <h2 className="text-xl font-black text-slate-800">
                  ✨ Đăng Tin Tuyển Dụng Mới
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Điền các thông số công việc để hệ thống AI hỗ trợ tìm kiếm ứng viên chuẩn xác
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-400 hover:text-slate-700 hover:bg-slate-200 flex items-center justify-center transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitJob} className="space-y-4">
              {/* Tiêu đề tin */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Tiêu đề công việc <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Ví dụ: Lập trình viên Backend Python (FastAPI/Django)"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              {/* Tên công ty & Địa điểm */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Tên công ty <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Tên doanh nghiệp của bạn"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Địa điểm làm việc
                  </label>
                  <input
                    type="text"
                    placeholder="Ví dụ: TP. Cần Thơ / Hybrid"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
              </div>

              {/* Ngành nghề */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Ngành nghề trọng tâm <span className="text-rose-500">*</span>
                </label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15 bg-white cursor-pointer"
                >
                  {INDUSTRIES.map((ind) => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>

              {/* Mức lương (Min/Max) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Lương tối thiểu (VNĐ)
                  </label>
                  <input
                    type="number"
                    step="1000000"
                    placeholder="Ví dụ: 10000000"
                    value={salaryMin}
                    onChange={(e) => setSalaryMin(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Lương tối đa (VNĐ)
                  </label>
                  <input
                    type="number"
                    step="1000000"
                    placeholder="Ví dụ: 25000000"
                    value={salaryMax}
                    onChange={(e) => setSalaryMax(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
              </div>

              {/* Kỹ năng yêu cầu (Tag Input với phím Enter) */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Kỹ năng yêu cầu (Gõ và nhấn Enter để thêm)
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Ví dụ: Python, Docker, SQL, Giao tiếp..."
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyDown={handleAddSkill}
                    className="flex-1 px-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                  />
                  <button
                    type="button"
                    onClick={addCurrentSkill}
                    className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition-colors cursor-pointer"
                  >
                    + Thêm
                  </button>
                </div>

                {/* Danh sách Tags đã thêm */}
                {skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2.5 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    {skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-[#0284c7] text-white shadow-2xs"
                      >
                        <span>{skill}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSkill(skill)}
                          className="hover:text-rose-200 font-black text-xs leading-none"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Mô tả công việc */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Mô tả công việc chi tiết
                </label>
                <textarea
                  rows="4"
                  placeholder="Mô tả trách nhiệm công việc, quyền lợi, chế độ đãi ngộ..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              {/* Nút hành động Submit */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-bold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold text-xs shadow-md shadow-sky-600/20 active:scale-98 transition-all cursor-pointer disabled:opacity-60 flex items-center gap-2"
                >
                  {submitting ? 'Đang đăng tin...' : 'Hoàn Tất Đăng Tin'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

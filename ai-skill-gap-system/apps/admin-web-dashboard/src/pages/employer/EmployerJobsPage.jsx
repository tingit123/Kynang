import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const INDUSTRIES = [
  'IT & Công nghệ',
  'Du lịch & Khách sạn',
  'Logistics & XNK',
  'Kinh tế & Tài chính',
  'Nông nghiệp công nghệ cao'
];

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
  const [location, setLocation] = useState('Cần Thơ');
  const [industry, setIndustry] = useState('IT & Công nghệ');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [description, setDescription] = useState('');
  
  // Tag input for skills
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState([]);

  // Lấy tên công ty từ current_user nếu có
  useEffect(() => {
    try {
      const userRaw = localStorage.getItem('current_user');
      if (userRaw) {
        const u = JSON.parse(userRaw);
        if (u.company_name) setCompany(u.company_name);
      }
    } catch (e) {}
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  // 1. Gọi API Lấy danh sách tin
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
        setErrorMsg('Không thể tải danh sách tin tuyển dụng.');
      }
    } catch (err) {
      console.error(err);
      setErrorMsg('Lỗi kết nối máy chủ khi tải danh sách tin.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyJobs();
  }, []);

  // Xử lý thêm tag kỹ năng
  const handleAddSkill = (e) => {
    if (e.key === 'Enter' || e.type === 'click') {
      e.preventDefault();
      const trimmed = skillInput.trim();
      if (trimmed && !skills.includes(trimmed)) {
        setSkills([...skills, trimmed]);
        setSkillInput('');
      }
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  // 2. Gọi API Tạo tin mới
  const handleSubmitJob = async (e) => {
    e.preventDefault();
    if (!title.trim() || !company.trim()) {
      alert('Vui lòng nhập tiêu đề và tên công ty.');
      return;
    }

    setSubmitting(true);
    const payload = {
      title: title.trim(),
      company: company.trim(),
      location: location.trim() || 'Cần Thơ',
      industry,
      description: description.trim(),
      salary_min: salaryMin ? parseInt(salaryMin, 10) : null,
      salary_max: salaryMax ? parseInt(salaryMax, 10) : null,
      skills
    };

    try {
      const res = await fetch(`${API_BASE}/api/jobs/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSuccessMsg('🎉 Đã đăng tin tuyển dụng thành công!');
        setIsModalOpen(false);
        // Reset form
        setTitle('');
        setSalaryMin('');
        setSalaryMax('');
        setDescription('');
        setSkills([]);
        // Tự động fetch lại danh sách
        fetchMyJobs();
        setTimeout(() => setSuccessMsg(''), 4000);
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || 'Không thể tạo tin tuyển dụng.');
      }
    } catch (err) {
      console.error(err);
      alert('Lỗi kết nối khi gửi thông tin đăng tin.');
    } finally {
      setSubmitting(false);
    }
  };

  // 3. Gọi API Xóa tin
  const handleDeleteJob = async (jobId, jobTitle) => {
    const confirmed = window.confirm(`Bạn có chắc chắn muốn xóa tin tuyển dụng "${jobTitle}" không?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (res.ok) {
        setSuccessMsg('🗑️ Đã xóa tin tuyển dụng thành công.');
        setJobs(jobs.filter(j => j.id !== jobId));
        setTimeout(() => setSuccessMsg(''), 3000);
      } else {
        alert('Không thể xóa tin tuyển dụng này.');
      }
    } catch (err) {
      console.error(err);
      alert('Lỗi kết nối khi xóa tin.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-800 flex items-center gap-2">
            <span>📝</span> Quản Lý Tin Tuyển Dụng
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Đăng tin tìm kiếm nhân sự chất lượng cao và đồng bộ yêu cầu kỹ năng với hệ thống AI
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white font-bold text-sm shadow-md shadow-sky-600/20 active:scale-95 transition-all cursor-pointer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span>Đăng tin mới</span>
        </button>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold rounded-xl flex items-center gap-2 animate-in fade-in">
          <span>{successMsg}</span>
        </div>
      )}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-xl flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Danh sách Tin Tuyển Dụng */}
      {loading ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200/80">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
          <p className="text-sm font-medium text-slate-500">Đang tải danh sách tin tuyển dụng...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200/80">
          <div className="text-4xl mb-3">📭</div>
          <h3 className="text-base font-bold text-slate-700">Chưa có tin tuyển dụng nào</h3>
          <p className="text-xs text-slate-400 mt-1 mb-4">Hãy bắt đầu tạo tin tuyển dụng đầu tiên của doanh nghiệp bạn.</p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 bg-[#0284c7] text-white text-xs font-bold rounded-lg hover:bg-[#0369a1] transition-colors"
          >
            + Đăng tin ngay
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-2xl p-5 border border-slate-200/80 hover:border-sky-300 hover:shadow-lg transition-all flex flex-col justify-between group"
            >
              <div>
                {/* Header Card */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 bg-sky-50 text-sky-700 rounded-lg border border-sky-100">
                    {job.industry || 'Ngành nghề'}
                  </span>
                  <button
                    onClick={() => handleDeleteJob(job.id, job.title)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                    title="Xóa tin này"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Title & Company */}
                <h3 className="text-base font-extrabold text-slate-800 group-hover:text-sky-700 transition-colors line-clamp-2">
                  {job.title}
                </h3>
                <p className="text-xs text-slate-500 font-medium mt-1 flex items-center gap-1.5">
                  <span>🏢 {job.company}</span>
                  <span>•</span>
                  <span>📍 {job.location || 'Cần Thơ'}</span>
                </p>

                {/* Salary */}
                <div className="mt-3 text-xs font-bold text-emerald-700 bg-emerald-50/70 border border-emerald-100 px-3 py-1.5 rounded-lg inline-block">
                  💰 {job.salary_min && job.salary_max
                    ? `${(job.salary_min / 1000000).toFixed(0)} - ${(job.salary_max / 1000000).toFixed(0)} triệu VNĐ`
                    : 'Thỏa thuận'}
                </div>

                {/* Description snippet */}
                {job.description && (
                  <p className="mt-3 text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {job.description}
                  </p>
                )}

                {/* Skills Tags */}
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Kỹ năng yêu cầu:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {job.skills && job.skills.length > 0 ? (
                      job.skills.map((s, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200"
                        >
                          {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-[11px] text-slate-400 italic">Chưa gắn tag kỹ năng</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Mã tin: #{job.id}</span>
                <span className="font-semibold text-sky-600">Đang tuyển</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── MODAL ĐĂNG TIN MỚI ── */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-100 p-6 sm:p-8">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
              <div>
                <h2 className="text-xl font-black text-slate-800">
                  ✨ Đăng Tin Tuyển Dụng Mới
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Điền chi tiết yêu cầu công việc để ứng viên nộp hồ sơ</p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-400 hover:text-slate-700 hover:bg-slate-200 flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitJob} className="space-y-4">
              {/* Tiêu đề */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Tiêu đề công việc <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Ví dụ: Kỹ sư Lập trình Backend Python (FastAPI/Django)"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              {/* Công ty & Địa điểm */}
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
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Địa điểm làm việc
                  </label>
                  <input
                    type="text"
                    placeholder="Ví dụ: Ninh Kiều, Cần Thơ"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
              </div>

              {/* Ngành nghề & Mức lương */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Ngành nghề <span className="text-rose-500">*</span>
                  </label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15 bg-white"
                  >
                    {INDUSTRIES.map((ind, idx) => (
                      <option key={idx} value={ind}>{ind}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Lương tối thiểu (VNĐ)
                  </label>
                  <input
                    type="number"
                    placeholder="10000000"
                    value={salaryMin}
                    onChange={(e) => setSalaryMin(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Lương tối đa (VNĐ)
                  </label>
                  <input
                    type="number"
                    placeholder="25000000"
                    value={salaryMax}
                    onChange={(e) => setSalaryMax(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                  />
                </div>
              </div>

              {/* Input Kỹ năng dạng Tags */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Kỹ năng yêu cầu (Nhập và nhấn Enter để thêm)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ví dụ: Python, Docker, SQL, Tiếng Anh..."
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyDown={handleAddSkill}
                    className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-colors"
                  >
                    + Thêm
                  </button>
                </div>
                {/* Danh sách Tags đã thêm */}
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {skills.map((s, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1.5 px-3 py-1 bg-sky-50 text-sky-800 text-xs font-bold rounded-full border border-sky-200"
                    >
                      {s}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(s)}
                        className="text-sky-500 hover:text-rose-600 font-bold"
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                  {skills.length === 0 && (
                    <span className="text-xs text-slate-400 italic">Chưa có kỹ năng nào được gắn</span>
                  )}
                </div>
              </div>

              {/* Mô tả công việc */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Mô tả công việc & Yêu cầu chi tiết
                </label>
                <textarea
                  rows={4}
                  placeholder="Mô tả các trách nhiệm chính, quyền lợi, chế độ đãi ngộ..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15"
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-sm font-semibold hover:bg-slate-50 transition-colors"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white text-sm font-bold shadow-md shadow-sky-600/20 active:scale-95 transition-all disabled:opacity-60"
                >
                  {submitting ? 'Đang tạo tin...' : 'Đăng Tin Ngay'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

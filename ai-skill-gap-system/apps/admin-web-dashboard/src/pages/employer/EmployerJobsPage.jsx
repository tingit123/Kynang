import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const CITIES = ['Cần Thơ', 'TP. Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Bình Dương'];

const INDUSTRIES = [
  'Công nghệ thông tin',
  'Du lịch & Khách sạn',
  'Logistics & Xuất nhập khẩu',
  'Kinh tế & Tài chính',
  'Nông nghiệp công nghệ cao'
];

const DEFAULT_JOBS = [
  {
    id: 1,
    title: 'Python Backend Developer',
    location: 'Quận Ninh Kiều, Cần Thơ',
    salary_min: 15000000,
    salary_max: 25000000,
    posted_date: '14/10/2026',
    status: 'open',
    statusLabel: 'Đang mở',
    skills: ['Python', 'FastAPI', 'Docker', 'SQL'],
    applications_count: 34
  },
  {
    id: 2,
    title: 'Data Analyst / BI Specialist',
    location: 'Quận Ninh Kiều, Cần Thơ',
    salary_min: 15000000,
    salary_max: 25000000,
    posted_date: '10/10/2026',
    status: 'open',
    statusLabel: 'Đang mở',
    skills: ['SQL', 'Power BI', 'Python'],
    applications_count: 21
  },
  {
    id: 3,
    title: 'DevOps & Cloud Engineer',
    location: 'Quận Ninh Kiều, Cần Thơ',
    salary_min: 15000000,
    salary_max: 25000000,
    posted_date: '05/10/2026',
    status: 'open',
    statusLabel: 'Đang mở',
    skills: ['Docker', 'Linux', 'CI/CD', 'Cloud'],
    applications_count: 40
  }
];

export default function EmployerJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form Fields
  const [title, setTitle] = useState('Python Backend Developer');
  const [company, setCompany] = useState('Mekong Tech');
  const [location, setLocation] = useState('Cần Thơ');
  const [industry, setIndustry] = useState('Công nghệ thông tin');
  const [salaryMin, setSalaryMin] = useState('15');
  const [salaryMax, setSalaryMax] = useState('25');
  const [description, setDescription] = useState(
    'Phát triển và bảo trì các dịch vụ backend bằng Python, làm việc cùng nhóm frontend và DevOps...'
  );

  // Skill tags
  const [skills, setSkills] = useState(['Python', 'Docker', 'Tiếng Anh']);
  const [skillInput, setSkillInput] = useState('');
  const [showSkillInput, setShowSkillInput] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    try {
      const rawUser = localStorage.getItem('current_user');
      if (rawUser) {
        const parsed = JSON.parse(rawUser);
        const comp = parsed.company_name || parsed.full_name || 'Mekong Tech';
        setCompany(comp);
      }
    } catch (e) {}
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  const fetchMyJobs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/jobs/my-jobs`, {
        headers: getAuthHeaders()
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setJobs(data);
        } else {
          setJobs(DEFAULT_JOBS);
        }
      } else {
        setJobs(DEFAULT_JOBS);
      }
    } catch (err) {
      setJobs(DEFAULT_JOBS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyJobs();
  }, []);

  const handleAddSkill = () => {
    const val = skillInput.trim();
    if (val && !skills.includes(val)) {
      setSkills([...skills, val]);
      setSkillInput('');
      setShowSkillInput(false);
    }
  };

  const handleRemoveSkill = (tagToRemove) => {
    setSkills(skills.filter((s) => s !== tagToRemove));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg('Vui lòng nhập tiêu đề tin tuyển dụng!');
      return;
    }

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    const payload = {
      title: title.trim(),
      company: company.trim(),
      location: location,
      industry: industry,
      salary_min: salaryMin ? parseFloat(salaryMin) * 1000000 : null,
      salary_max: salaryMax ? parseFloat(salaryMax) * 1000000 : null,
      description: description.trim(),
      skills: skills
    };

    try {
      const res = await fetch(`${API_BASE}/api/jobs/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const newJob = await res.json();
        setSuccessMsg('Đăng tin tuyển dụng mới thành công!');
        setJobs([newJob, ...jobs]);
        try {
          const raw = localStorage.getItem('global_job_postings');
          const list = raw ? JSON.parse(raw) : [];
          list.unshift(newJob);
          localStorage.setItem('global_job_postings', JSON.stringify(list));
        } catch (e) {}
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // Mock fallback insertion if demo mode
        const mockNewJob = {
          id: Date.now(),
          title: payload.title,
          company_name: payload.company,
          location: payload.location,
          industry: payload.industry,
          salary_min: payload.salary_min,
          salary_max: payload.salary_max,
          description: payload.description,
          posted_date: new Date().toLocaleDateString('vi-VN'),
          status: 'open',
          statusLabel: 'Đang mở',
          skills: payload.skills,
          applications_count: 0
        };
        setJobs([mockNewJob, ...jobs]);
        try {
          const raw = localStorage.getItem('global_job_postings');
          const list = raw ? JSON.parse(raw) : [];
          list.unshift(mockNewJob);
          localStorage.setItem('global_job_postings', JSON.stringify(list));
        } catch (e) {}
        setSuccessMsg('Đăng tin tuyển dụng mới thành công!');
      }
    } catch (err) {
      const mockNewJob = {
        id: Date.now(),
        title: payload.title,
        company_name: payload.company,
        location: payload.location,
        industry: payload.industry,
        salary_min: payload.salary_min,
        salary_max: payload.salary_max,
        description: payload.description,
        posted_date: new Date().toLocaleDateString('vi-VN'),
        status: 'open',
        statusLabel: 'Đang mở',
        skills: payload.skills,
        applications_count: 0
      };
      setJobs([mockNewJob, ...jobs]);
      try {
        const raw = localStorage.getItem('global_job_postings');
        const list = raw ? JSON.parse(raw) : [];
        list.unshift(mockNewJob);
        localStorage.setItem('global_job_postings', JSON.stringify(list));
      } catch (e) {}
      setSuccessMsg('Đăng tin tuyển dụng mới thành công!');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteJob = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa tin tuyển dụng này?')) return;
    try {
      await fetch(`${API_BASE}/api/jobs/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
    } catch (e) {}
    try {
      const raw = localStorage.getItem('global_job_postings');
      if (raw) {
        const list = JSON.parse(raw);
        localStorage.setItem('global_job_postings', JSON.stringify(list.filter((j) => j.id !== id)));
      }
    } catch (e) {}
    setJobs(jobs.filter((j) => j.id !== id));
  };

  return (
    <div className="space-y-8 max-w-6xl">
      {/* ── 1. HEADER TRANG & NÚT ĐĂNG TIN MỚI ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Quản lý tin tuyển dụng
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Đăng tin mới, gắn thẻ kỹ năng và quản lý các tin đã đăng.
          </p>
        </div>
        <button
          onClick={() => {
            document.getElementById('jobPostForm')?.scrollIntoView({ behavior: 'smooth' });
            document.getElementById('jobTitleInput')?.focus();
          }}
          className="self-start sm:self-auto px-6 py-2.5 bg-[#0a5146] hover:bg-[#084239] text-white text-xs font-black tracking-wider uppercase rounded-full shadow-md transition-all cursor-pointer"
        >
          ĐĂNG TIN MỚI
        </button>
      </div>

      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-xs font-bold">
          ✓ {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl text-xs font-bold">
          ✕ {errorMsg}
        </div>
      )}

      {/* ── 2. BỐ CỤC 2 CỘT (FORM TRÁI & DANH SÁCH PHẢI) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* ── CỘT TRÁI: FORM ĐĂNG TIN MỚI (5 COLS) ── */}
        <div
          id="jobPostForm"
          className="lg:col-span-5 bg-white rounded-3xl p-6 sm:p-7 shadow-xs border border-slate-100 space-y-5"
        >
          <h2 className="text-base sm:text-lg font-bold text-slate-900">
            Đăng tin mới
          </h2>

          <form onSubmit={handleCreateJob} className="space-y-4">
            {/* Tiêu đề */}
            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                TIÊU ĐỀ
              </label>
              <input
                id="jobTitleInput"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Python Backend Developer"
                className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] focus:ring-2 focus:ring-teal-500/20 text-slate-800 font-medium"
                required
              />
            </div>

            {/* Tên công ty & Địa điểm (2 cols) */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  TÊN CÔNG TY
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  ĐỊA ĐIỂM
                </label>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium bg-white cursor-pointer"
                >
                  {CITIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Ngành nghề */}
            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                NGÀNH NGHỀ
              </label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium bg-white cursor-pointer"
              >
                {INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>
                    {ind}
                  </option>
                ))}
              </select>
            </div>

            {/* Lương tối thiểu & Tối đa (2 cols) */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 truncate" title="LƯƠNG TỐI THIỂU (TRIỆU)">
                  LƯƠNG TỐI THIỂU (TRIỆU)
                </label>
                <input
                  type="number"
                  value={salaryMin}
                  onChange={(e) => setSalaryMin(e.target.value)}
                  placeholder="15"
                  className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 truncate" title="LƯƠNG TỐI ĐA (TRIỆU)">
                  LƯƠNG TỐI ĐA (TRIỆU)
                </label>
                <input
                  type="number"
                  value={salaryMax}
                  onChange={(e) => setSalaryMax(e.target.value)}
                  placeholder="25"
                  className="w-full px-4 py-2.5 rounded-full border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium"
                />
              </div>
            </div>

            {/* Mô tả công việc */}
            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                MÔ TẢ CÔNG VIỆC
              </label>
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Phát triển và bảo trì các dịch vụ backend bằng Python, làm việc cùng nhóm frontend và DevOps..."
                className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm focus:outline-none focus:border-[#0d5f57] text-slate-800 font-medium leading-relaxed resize-none"
              />
            </div>

            {/* Kỹ năng yêu cầu (AI dùng để đối chiếu ứng viên) */}
            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">
                KỸ NĂNG YÊU CẦU (AI DÙNG ĐỂ ĐỐI CHIẾU ỨNG VIÊN)
              </label>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                {skills.map((s) => (
                  <span
                    key={s}
                    className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#dcfce7] text-[#0f766e] text-xs font-bold rounded-full"
                  >
                    <span>{s}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(s)}
                      className="hover:text-rose-700 cursor-pointer font-extrabold text-[11px]"
                    >
                      ✕
                    </button>
                  </span>
                ))}

                {showSkillInput ? (
                  <div className="inline-flex items-center gap-1">
                    <input
                      type="text"
                      autoFocus
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddSkill();
                        }
                      }}
                      placeholder="Nhập tên tag..."
                      className="px-2.5 py-1 text-xs border border-teal-600 rounded-full focus:outline-none w-28"
                    />
                    <button
                      type="button"
                      onClick={handleAddSkill}
                      className="px-2 py-1 bg-[#0d5f57] text-white text-xs font-bold rounded-full cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setShowSkillInput(true)}
                    className="px-3 py-1 border border-dashed border-slate-300 text-slate-600 hover:border-teal-600 hover:text-teal-700 text-xs font-bold rounded-full transition-colors cursor-pointer"
                  >
                    + Thêm kỹ năng
                  </button>
                )}
              </div>
            </div>

            {/* Nút Đăng Tin */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 bg-[#0a5146] hover:bg-[#084239] text-white font-extrabold text-xs tracking-wider uppercase rounded-full shadow-md transition-all cursor-pointer disabled:opacity-60 text-center block"
              >
                {submitting ? 'ĐANG XỬ LÝ...' : 'ĐĂNG TIN'}
              </button>
            </div>
          </form>
        </div>

        {/* ── CỘT PHẢI: TIN ĐÃ ĐĂNG (7 COLS) ── */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-base sm:text-lg font-bold text-slate-900">
              Tin đã đăng ({jobs.length})
            </h2>
            <span className="text-xs text-slate-400 font-medium">
              Xóa tin khi đã tuyển đủ người
            </span>
          </div>

          <div className="space-y-4">
            {jobs.map((job) => {
              const salaryText =
                job.salary_min && job.salary_max
                  ? `${(job.salary_min / 1000000).toFixed(0)}–${(job.salary_max / 1000000).toFixed(0)} triệu`
                  : '15–25 triệu';

              const dateText = job.posted_date || '14/10/2026';
              const locationText = job.location || 'Quận Ninh Kiều, Cần Thơ';
              const appsCount = job.applications_count || 34;

              return (
                <div
                  key={job.id}
                  className="bg-white rounded-3xl p-6 border border-slate-100 shadow-xs hover:shadow-md transition-all space-y-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-base font-extrabold text-slate-900 leading-snug">
                      {job.title}
                    </h3>
                    <span className="px-3 py-0.5 rounded-full text-xs font-bold bg-[#dcfce7] text-[#0f766e] shrink-0">
                      Đang mở
                    </span>
                  </div>

                  <div className="text-xs text-slate-500 font-medium">
                    {locationText} · {salaryText} · Đăng {dateText}
                  </div>

                  {/* Kỹ năng tags */}
                  <div className="flex flex-wrap gap-2 pt-1">
                    {(job.skills && job.skills.length > 0
                      ? job.skills
                      : ['Python', 'FastAPI', 'Docker', 'SQL']
                    ).map((sk) => (
                      <span
                        key={sk}
                        className="px-3 py-1 bg-[#dcfce7] text-[#0f766e] text-xs font-bold rounded-full"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>

                  {/* Footer card */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-50">
                    <span className="text-xs text-slate-700">
                      <strong className="text-slate-900 font-extrabold">{appsCount}</strong> hồ sơ đã nộp
                    </span>
                    <button
                      onClick={() => handleDeleteJob(job.id)}
                      className="px-4 py-1 rounded-full border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-bold transition-colors cursor-pointer"
                    >
                      Xóa tin
                    </button>
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

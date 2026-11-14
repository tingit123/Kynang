import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SEED_JOBS = [
  {
    id: 1,
    title: 'Python Backend Developer',
    company: 'Mekong Tech',
    avatar: 'M',
    avatarBg: '#0d9488',
    salary: '15–25 triệu',
    salaryDetail: '15–25 triệu / tháng',
    location: 'Quận Ninh Kiều, Cần Thơ',
    postedTime: '3 ngày trước',
    industry: 'IT',
    industryLabel: 'IT & Công nghệ',
    skills: ['Python', 'FastAPI', 'Docker', 'SQL', 'Git', 'REST API'],
    description:
      'Phát triển và bảo trì các dịch vụ backend bằng Python, làm việc cùng nhóm frontend và DevOps. Thiết kế REST API, tối ưu truy vấn cơ sở dữ liệu và triển khai bằng Docker.',
    companyAbout:
      'Mekong Tech là công ty phần mềm tại Cần Thơ, hơn 80 kỹ sư, tập trung xây dựng sản phẩm cho thị trường ĐBSCL. Chúng tôi coi trọng đào tạo nội bộ và lộ trình thăng tiến rõ ràng.'
  },
  {
    id: 2,
    title: 'Data Analyst / BI Specialist',
    company: 'Viettel Digital Cần Thơ',
    avatar: 'V',
    avatarBg: '#0f766e',
    salary: '12–20 triệu',
    salaryDetail: '12–20 triệu / tháng',
    location: 'Quận Cái Răng, Cần Thơ',
    postedTime: '5 ngày trước',
    industry: 'IT',
    industryLabel: 'IT & Công nghệ',
    skills: ['SQL', 'Power BI', 'Python', 'Excel'],
    description:
      'Xây dựng các dashboard trực quan hóa dữ liệu kinh doanh, phân tích xu hướng tiêu dùng và chuẩn bị báo cáo định kỳ cho ban giám đốc.',
    companyAbout:
      'Viettel Digital Cần Thơ dẫn đầu về các giải pháp số cho các doanh nghiệp và cơ quan nhà nước tại vùng Tây Nam Bộ.'
  },
  {
    id: 3,
    title: 'DevOps & Cloud Engineer',
    company: 'FPT Software Cần Thơ',
    avatar: 'F',
    avatarBg: '#0d9488',
    salary: '20–35 triệu',
    salaryDetail: '20–35 triệu / tháng',
    location: 'KCN Trà Nóc, Cần Thơ',
    postedTime: '1 tuần trước',
    industry: 'IT',
    industryLabel: 'IT & Công nghệ',
    skills: ['Docker', 'Linux', 'CI/CD', 'AWS', 'Kubernetes'],
    description:
      'Vận hành hệ thống CI/CD trên nền tảng đám mây, tự động hóa quy trình triển khai phần mềm và đảm bảo độ sẵn sàng cao của hệ thống.',
    companyAbout:
      'FPT Software Cần Thơ là trung tâm sản xuất phần mềm chiến lược cho thị trường Nhật Bản và APAC tại miền Tây Nam Bộ.'
  },
  {
    id: 4,
    title: 'Frontend Developer (React)',
    company: 'TMA Solutions Cần Thơ',
    avatar: 'T',
    avatarBg: '#0f766e',
    salary: '15–30 triệu',
    salaryDetail: '15–30 triệu / tháng',
    location: 'Khu Công Nghệ Cao, Cần Thơ',
    postedTime: '1 tuần trước',
    industry: 'IT',
    industryLabel: 'IT & Công nghệ',
    skills: ['ReactJS', 'TypeScript', 'Git', 'Tailwind', 'REST API'],
    description:
      'Phát triển các ứng dụng Web SPA hiện đại sử dụng ReactJS và TailwindCSS, tối ưu trải nghiệm người dùng và hiệu năng trình duyệt.',
    companyAbout:
      'TMA Solutions là công ty phần mềm hàng đầu Việt Nam với văn phòng hiện đại tại trung tâm Cần Thơ.'
  },
  {
    id: 5,
    title: 'Chuyên viên Xuất nhập khẩu',
    company: 'Cảng Cái Cui',
    avatar: 'C',
    avatarBg: '#0d9488',
    salary: '10–18 triệu',
    salaryDetail: '10–18 triệu / tháng',
    location: 'Quận Cái Răng, Cần Thơ',
    postedTime: '2 tuần trước',
    industry: 'logistics',
    industryLabel: 'Logistics & XNK',
    skills: ['Customs Compliance', 'English', 'Logistics Operations', 'Documentation'],
    description:
      'Thực hiện thủ tục hải quan xuất nhập khẩu hàng hóa, theo dõi lịch tàu và phối hợp với các hãng vận tải quốc tế.',
    companyAbout:
      'Cảng Cái Cui là cảng biển nước sâu lớn nhất ĐBSCL, trung tâm logistics kết nối nông sản đồng bằng ra thế giới.'
  }
];

const DEFAULT_CANDIDATE = {
  id: 3,
  name: 'Nguyễn Văn An',
  email: 'sinhvien@ctu.edu.vn',
  phone: '0912 345 678',
  university: 'Sinh viên CNTT năm 4 · Đại học Cần Thơ',
  skills: ['Python', 'SQL', 'Git', 'REST API', 'JavaScript', 'HTML/CSS']
};

export default function CandidateJobsPage() {
  const navigate = useNavigate();

  // Candidate Profile
  const [candidate, setCandidate] = useState(() => {
    try {
      const raw = localStorage.getItem('current_user');
      if (raw) {
        const u = JSON.parse(raw);
        return {
          ...DEFAULT_CANDIDATE,
          ...u,
          skills: u.skills || DEFAULT_CANDIDATE.skills
        };
      }
    } catch (e) {}
    return DEFAULT_CANDIDATE;
  });

  // Jobs List (Seed + Any Jobs Posted by Employers)
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(1);

  // Search & Filter state
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchIndustry, setSearchIndustry] = useState('all');
  const [searchLocation, setSearchLocation] = useState('all');
  const [activeCategoryPill, setActiveCategoryPill] = useState('all');

  // Application state
  const [appliedJobIds, setAppliedJobIds] = useState([3]); // Seed job 3 applied as in mockup
  const [savedJobIds, setSavedJobIds] = useState([]);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [showAppliedDrawer, setShowAppliedDrawer] = useState(false);
  const [applyNote, setApplyNote] = useState(
    'Tôi rất hào hứng với cơ hội này tại Mekong Tech và tự tin có thể hoàn thành tốt các nhiệm vụ được giao.'
  );

  // Load jobs and merge with employer postings
  useEffect(() => {
    let allJobs = [...SEED_JOBS];
    try {
      const rawPostings = localStorage.getItem('global_job_postings');
      if (rawPostings) {
        const extraJobs = JSON.parse(rawPostings);
        if (Array.isArray(extraJobs) && extraJobs.length > 0) {
          // Put new employer jobs at front if not already included
          const existingIds = new Set(allJobs.map((j) => j.id));
          extraJobs.forEach((ej) => {
            if (!existingIds.has(ej.id)) {
              allJobs.unshift({
                id: ej.id,
                title: ej.title,
                company: ej.company_name || ej.company || 'Doanh nghiệp Cần Thơ',
                avatar: (ej.company_name || 'D').charAt(0).toUpperCase(),
                avatarBg: '#0d9488',
                salary: `${Math.round((ej.salary_min || 15000000) / 1000000)}–${Math.round((ej.salary_max || 25000000) / 1000000)} triệu`,
                salaryDetail: `${Math.round((ej.salary_min || 15000000) / 1000000)}–${Math.round((ej.salary_max || 25000000) / 1000000)} triệu / tháng`,
                location: ej.location || 'Cần Thơ',
                postedTime: 'Vừa xong',
                industry: ej.industry || 'IT',
                industryLabel: ej.industry === 'logistics' ? 'Logistics & XNK' : 'IT & Công nghệ',
                skills: Array.isArray(ej.skills) ? ej.skills : ['Python', 'Docker'],
                description: ej.description || 'Tuyển dụng nhân sự chất lượng cao tại Cần Thơ.',
                companyAbout: ej.company_description || 'Doanh nghiệp hàng đầu tại khu vực ĐBSCL.'
              });
            }
          });
        }
      }
    } catch (e) {}

    // Load applied IDs from global_job_applications
    try {
      const rawApps = localStorage.getItem('global_job_applications');
      if (rawApps) {
        const apps = JSON.parse(rawApps);
        const myApps = apps.filter((a) => a.candidate_email === candidate.email || a.candidate_name === candidate.name);
        const ids = myApps.map((a) => a.job_id);
        setAppliedJobIds((prev) => Array.from(new Set([...prev, ...ids])));
      }
    } catch (e) {}

    setJobs(allJobs);
  }, [candidate.email, candidate.name]);

  // Skill Match Calculation
  const calculateMatch = (jobSkills = []) => {
    if (!jobSkills || jobSkills.length === 0) return { percent: 100, owned: [], missing: [] };
    const mySkillsLower = (candidate.skills || []).map((s) => s.toLowerCase().trim());
    
    const owned = [];
    const missing = [];

    jobSkills.forEach((skill) => {
      const sLower = skill.toLowerCase().trim();
      const hasSkill = mySkillsLower.some((myS) => myS === sLower || sLower.includes(myS) || myS.includes(sLower));
      if (hasSkill) {
        owned.push(skill);
      } else {
        missing.push(skill);
      }
    });

    const percent = Math.round((owned.length / jobSkills.length) * 100);
    return { percent, owned, missing };
  };

  // Filter Jobs
  const filteredJobs = jobs.filter((job) => {
    // Keyword
    if (searchKeyword.trim()) {
      const kw = searchKeyword.toLowerCase();
      const matchTitle = job.title.toLowerCase().includes(kw);
      const matchComp = job.company.toLowerCase().includes(kw);
      const matchSkills = job.skills.some((s) => s.toLowerCase().includes(kw));
      if (!matchTitle && !matchComp && !matchSkills) return false;
    }

    // Industry dropdown
    if (searchIndustry !== 'all') {
      if (job.industry !== searchIndustry && job.industryLabel !== searchIndustry) return false;
    }

    // Category Pill
    if (activeCategoryPill !== 'all') {
      if (activeCategoryPill === 'it' && job.industry !== 'IT') return false;
      if (activeCategoryPill === 'tourism' && job.industry !== 'tourism') return false;
      if (activeCategoryPill === 'logistics' && job.industry !== 'logistics') return false;
      if (activeCategoryPill === 'economics' && job.industry !== 'economics') return false;
      if (activeCategoryPill === 'agriculture' && job.industry !== 'agriculture') return false;
    }

    // Location
    if (searchLocation !== 'all') {
      if (!job.location.includes(searchLocation)) return false;
    }

    return true;
  });

  // Selected Job object
  const selectedJob = filteredJobs.find((j) => j.id === selectedJobId) || filteredJobs[0] || jobs[0];
  const selectedMatch = selectedJob ? calculateMatch(selectedJob.skills) : { percent: 0, owned: [], missing: [] };
  const isSelectedApplied = selectedJob ? appliedJobIds.includes(selectedJob.id) : false;
  const isSelectedSaved = selectedJob ? savedJobIds.includes(selectedJob.id) : false;

  // Handle Application Submit
  const handleConfirmApply = () => {
    if (!selectedJob) return;

    const newApp = {
      id: `app_${Date.now()}`,
      job_id: selectedJob.id,
      job_title: selectedJob.title,
      company_name: selectedJob.company,
      candidate_id: candidate.id || 3,
      candidate_name: candidate.name,
      candidate_email: candidate.email,
      candidate_phone: candidate.phone,
      applied_date: 'Hôm nay',
      match_score: selectedMatch.percent,
      skills_owned: selectedMatch.owned,
      skills_missing: selectedMatch.missing,
      note: applyNote,
      status: 'Mới nộp'
    };

    // Save to global_job_applications (for Employer Portal)
    try {
      const raw = localStorage.getItem('global_job_applications');
      const list = raw ? JSON.parse(raw) : [];
      list.unshift(newApp);
      localStorage.setItem('global_job_applications', JSON.stringify(list));
    } catch (e) {}

    setAppliedJobIds((prev) => [...prev, selectedJob.id]);
    setShowApplyModal(false);
    alert(
      `Ứng tuyển thành công vị trí "${selectedJob.title}" tại ${selectedJob.company}!\n\nHồ sơ cùng phân tích CV (Phù hợp ${selectedMatch.percent}%) đã được chuyển thẳng tới Ban Tuyển Dụng.`
    );
  };

  const handleToggleSaveJob = (id) => {
    setSavedJobIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 antialiased -mt-6 sm:-mt-8">
      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── 1. HERO BANNER & SEARCH BAR (DARK TEAL THEME - KHỚP ẢNH MẪU) ── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <section className="bg-[#094741] text-white pt-10 pb-8 px-4 sm:px-6 lg:px-8 shadow-md">
        <div className="max-w-7xl mx-auto text-center">
          {/* Header Title */}
          <h1 className="text-3xl sm:text-4xl lg:text-[40px] font-black tracking-tight mb-2">
            Việc làm tại <span className="text-[#5eead4]">Cần Thơ &amp; ĐBSCL</span>
          </h1>
          <p className="text-sm sm:text-base text-teal-100/90 font-medium max-w-2xl mx-auto mb-8">
            Tin tuyển dụng từ doanh nghiệp trong khu vực, kèm mức phù hợp với hồ sơ kỹ năng của bạn.
          </p>

          {/* Floating Rounded Search Bar */}
          <div className="bg-white rounded-full p-2 sm:p-2.5 shadow-2xl max-w-4xl mx-auto flex flex-col md:flex-row items-center gap-2 md:gap-0 border border-teal-900/10 text-left">
            {/* Field 1: Từ khóa */}
            <div className="flex-1 px-5 py-1.5 w-full md:w-auto">
              <label className="block text-[10px] font-black text-slate-400 uppercase tracking-wider mb-0.5">
                TỪ KHÓA
              </label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="Vị trí, tên công ty, kỹ năng"
                className="w-full text-xs sm:text-sm font-semibold text-slate-800 placeholder-slate-400 focus:outline-none bg-transparent"
              />
            </div>

            <div className="hidden md:block w-px h-8 bg-slate-200"></div>

            {/* Field 2: Ngành */}
            <div className="px-5 py-1.5 w-full md:w-auto md:min-w-[170px]">
              <label className="block text-[10px] font-black text-slate-400 uppercase tracking-wider mb-0.5">
                NGÀNH
              </label>
              <select
                value={searchIndustry}
                onChange={(e) => setSearchIndustry(e.target.value)}
                className="w-full text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none bg-transparent cursor-pointer"
              >
                <option value="all">Tất cả</option>
                <option value="IT">IT &amp; Công nghệ</option>
                <option value="tourism">Du lịch &amp; Khách sạn</option>
                <option value="logistics">Logistics &amp; XNK</option>
                <option value="economics">Kinh tế &amp; Tài chính</option>
                <option value="agriculture">Nông nghiệp</option>
              </select>
            </div>

            <div className="hidden md:block w-px h-8 bg-slate-200"></div>

            {/* Field 3: Địa điểm */}
            <div className="px-5 py-1.5 w-full md:w-auto md:min-w-[150px]">
              <label className="block text-[10px] font-black text-slate-400 uppercase tracking-wider mb-0.5">
                ĐỊA ĐIỂM
              </label>
              <select
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                className="w-full text-xs sm:text-sm font-semibold text-slate-800 focus:outline-none bg-transparent cursor-pointer"
              >
                <option value="all">Tất cả</option>
                <option value="Cần Thơ">Cần Thơ</option>
                <option value="Hậu Giang">Hậu Giang</option>
                <option value="An Giang">An Giang</option>
                <option value="Vĩnh Long">Vĩnh Long</option>
              </select>
            </div>

            {/* Search Button */}
            <button
              onClick={() => {}}
              className="w-full md:w-auto px-8 py-3 rounded-full bg-[#0d5f57] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider transition-all cursor-pointer whitespace-nowrap shadow-md"
            >
              TÌM VIỆC
            </button>
          </div>

          {/* Quick Category Filter Pills */}
          <div className="max-w-5xl mx-auto mt-6 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => setActiveCategoryPill('all')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'all'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                Tất cả
              </button>

              <button
                onClick={() => setActiveCategoryPill('it')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'it'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                IT &amp; Công nghệ
              </button>

              <button
                onClick={() => setActiveCategoryPill('tourism')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'tourism'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                Du lịch &amp; Khách sạn
              </button>

              <button
                onClick={() => setActiveCategoryPill('logistics')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'logistics'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                Logistics &amp; XNK
              </button>

              <button
                onClick={() => setActiveCategoryPill('economics')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'economics'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                Kinh tế &amp; Tài chính
              </button>

              <button
                onClick={() => setActiveCategoryPill('agriculture')}
                className={`px-4 py-1.5 rounded-full font-bold transition-all cursor-pointer ${
                  activeCategoryPill === 'agriculture'
                    ? 'bg-[#06332e] text-white border border-[#5eead4]/60'
                    : 'bg-white text-slate-700 hover:bg-teal-50'
                }`}
              >
                Nông nghiệp
              </button>
            </div>

            {/* Total Results Summary */}
            <div className="text-teal-100/80 font-medium">
              <strong className="text-white">{filteredJobs.length} việc làm</strong> · sắp xếp theo mức phù hợp
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── 2. MAIN 2-COLUMN LAYOUT: JOB CARDS (LEFT) & DETAIL (RIGHT) ─── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* ──── CỘT TRÁI (LƯỚI DANH SÁCH TIN TUYỂN DỤNG - 5 COLS) ──── */}
          <div className="lg:col-span-5 space-y-4">
            {filteredJobs.length === 0 ? (
              <div className="bg-white rounded-3xl p-8 border border-slate-200 text-center text-slate-500">
                Không tìm thấy việc làm phù hợp với tiêu chí tìm kiếm.
              </div>
            ) : (
              filteredJobs.map((job) => {
                const match = calculateMatch(job.skills);
                const isSelected = selectedJob && selectedJob.id === job.id;
                const isApplied = appliedJobIds.includes(job.id);

                return (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJobId(job.id)}
                    className={`bg-white rounded-3xl p-5 border cursor-pointer transition-all relative ${
                      isSelected
                        ? 'border-[#0a5146] shadow-md ring-2 ring-[#0a5146]/20'
                        : 'border-slate-200/80 hover:border-teal-400 hover:shadow-xs'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 mb-2.5">
                      <div className="flex items-center gap-3">
                        <div
                          style={{ backgroundColor: job.avatarBg || '#0d9488' }}
                          className="w-11 h-11 rounded-2xl text-white font-black text-lg flex items-center justify-center shrink-0 shadow-xs"
                        >
                          {job.avatar}
                        </div>
                        <div>
                          <h3 className="text-base font-black text-slate-900 leading-snug line-clamp-1">
                            {job.title}
                          </h3>
                          <div className="text-xs font-bold text-slate-500 mt-0.5">
                            {job.company}
                          </div>
                        </div>
                      </div>

                      {/* Match Badge */}
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-black shrink-0 ${
                          match.percent >= 60
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200/60'
                            : match.percent >= 40
                            ? 'bg-amber-50 text-amber-800 border border-amber-200/60'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        Phù hợp {match.percent}%
                      </span>
                    </div>

                    {/* Meta Info: Lương, Địa điểm, Ngày đăng */}
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 font-semibold mb-3">
                      <span className="font-extrabold text-emerald-700">{job.salary}</span>
                      <span>·</span>
                      <span>{job.location}</span>
                      <span>·</span>
                      <span>{job.postedTime}</span>
                    </div>

                    {/* Skill Tags & Applied Badge */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {job.skills.slice(0, 4).map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.skills.length > 4 && (
                          <span className="text-[10px] text-slate-400 font-bold">
                            +{job.skills.length - 4}
                          </span>
                        )}
                      </div>

                      {/* Đã ứng tuyển Badge */}
                      {isApplied && (
                        <span className="px-3 py-0.5 rounded-full text-[11px] font-black bg-emerald-700 text-white shrink-0 shadow-2xs">
                          Đã ứng tuyển
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* ──── CỘT PHẢI (CHI TIẾT VIỆC LÀM - 7 COLS) ──── */}
          <div className="lg:col-span-7">
            {selectedJob ? (
              <div className="bg-white rounded-3xl p-7 border border-slate-200/90 shadow-sm sticky top-24">
                {/* Header Chi tiết */}
                <div className="flex items-start gap-4 mb-5">
                  <div
                    style={{ backgroundColor: selectedJob.avatarBg || '#0d9488' }}
                    className="w-14 h-14 rounded-2xl text-white font-black text-2xl flex items-center justify-center shrink-0 shadow-xs"
                  >
                    {selectedJob.avatar}
                  </div>
                  <div className="flex-1">
                    <div className="text-[11px] font-black uppercase tracking-wider text-[#0d5f57] mb-1">
                      {selectedJob.company}
                    </div>
                    <h2 className="text-2xl font-black text-slate-900 leading-tight">
                      {selectedJob.title}
                    </h2>
                  </div>
                </div>

                {/* Badges: Lương, Địa điểm, Ngày đăng */}
                <div className="flex flex-wrap items-center gap-2 mb-6">
                  <span className="px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-800 text-xs font-bold">
                    {selectedJob.salaryDetail || selectedJob.salary}
                  </span>
                  <span className="px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-800 text-xs font-bold">
                    {selectedJob.location}
                  </span>
                  <span className="px-3.5 py-1.5 rounded-full bg-slate-100 text-slate-800 text-xs font-bold">
                    Đăng {selectedJob.postedTime}
                  </span>
                </div>

                {/* Bộ nút hành động: ỨNG TUYỂN NGAY & LƯU TIN */}
                <div className="flex items-center gap-3 pb-7 border-b border-slate-100 mb-6">
                  {isSelectedApplied ? (
                    <button
                      disabled
                      className="px-7 py-3 rounded-full bg-emerald-700 text-white font-black text-xs uppercase tracking-wider flex items-center gap-2 cursor-default shadow-xs"
                    >
                      <span>✓ ĐÃ ỨNG TUYỂN</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => setShowApplyModal(true)}
                      className="px-7 py-3 rounded-full bg-[#0d5f57] hover:bg-[#073d35] text-white font-black text-xs uppercase tracking-wider flex items-center gap-2 cursor-pointer transition-all shadow-md shadow-teal-950/20"
                    >
                      <span>ỨNG TUYỂN NGAY</span>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <polyline points="9 18 15 12 9 6" />
                      </svg>
                    </button>
                  )}

                  <button
                    onClick={() => handleToggleSaveJob(selectedJob.id)}
                    className={`px-6 py-3 rounded-full text-xs font-black uppercase tracking-wider transition-all cursor-pointer border ${
                      isSelectedSaved
                        ? 'bg-rose-50 border-rose-300 text-rose-600'
                        : 'bg-white border-[#0d5f57] text-[#0d5f57] hover:bg-slate-50'
                    }`}
                  >
                    {isSelectedSaved ? 'ĐÃ LƯU TIN' : 'LƯU TIN'}
                  </button>
                </div>

                {/* ── PHÂN TÍCH SO KHỚP KỸ NĂNG CỦA BẠN (KHỚP 100% ẢNH MẪU) ── */}
                <div className="bg-slate-50/70 rounded-2xl p-5 border border-slate-200/80 mb-6">
                  <div className="flex items-center justify-between mb-2.5">
                    <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider">
                      Kỹ năng yêu cầu so với hồ sơ của bạn
                    </h4>
                    <span className="text-xs font-black text-[#0d5f57]">
                      Bạn có {selectedMatch.owned.length} / {selectedJob.skills.length}
                    </span>
                  </div>

                  {/* Dual Progress Bar */}
                  <div className="w-full bg-slate-200 rounded-full h-2 mb-4 overflow-hidden">
                    <div
                      style={{ width: `${selectedMatch.percent}%` }}
                      className="bg-[#0d5f57] h-full rounded-full transition-all duration-500"
                    ></div>
                  </div>

                  {/* Danh sách thẻ kỹ năng Có / Chưa có */}
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    {selectedJob.skills.map((skill, idx) => {
                      const has = selectedMatch.owned.includes(skill);
                      return has ? (
                        <span
                          key={idx}
                          className="px-3.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200/70 flex items-center gap-1.5"
                        >
                          <span>{skill}</span>
                        </span>
                      ) : (
                        <span
                          key={idx}
                          className="px-3.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200/70 flex items-center gap-1.5"
                        >
                          <span>{skill} - chưa có</span>
                        </span>
                      );
                    })}
                  </div>

                  {/* Note AI */}
                  <p className="text-[11.5px] text-slate-500 leading-relaxed font-medium">
                    Khi ứng tuyển, bản phân tích CV của bạn (phù hợp {selectedMatch.percent}%) được gửi kèm để nhà tuyển dụng xem trực tiếp trên hệ thống.
                  </p>
                </div>

                {/* Mô tả công việc */}
                <div className="mb-6">
                  <h4 className="text-sm font-black text-slate-900 mb-2">
                    Mô tả công việc
                  </h4>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                    {selectedJob.description}
                  </p>
                </div>

                {/* Về công ty */}
                <div>
                  <h4 className="text-sm font-black text-slate-900 mb-2">
                    Về công ty
                  </h4>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                    {selectedJob.companyAbout}
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </main>

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── 3. MODAL ỨNG TUYỂN (GỬI THẲNG CHO DOANH NGHIỆP) ────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      {showApplyModal && selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-2xs p-4">
          <div className="bg-white rounded-3xl p-7 max-w-lg w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 relative">
            <button
              onClick={() => setShowApplyModal(false)}
              className="absolute top-6 right-6 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center font-bold text-sm cursor-pointer"
            >
              ✕
            </button>

            <h3 className="text-lg font-black text-slate-900 mb-1">
              Ứng tuyển {selectedJob.title}
            </h3>
            <p className="text-xs text-slate-500 font-semibold mb-5">
              Gửi hồ sơ tới {selectedJob.company}
            </p>

            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 mb-4 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Ứng viên:</span>
                <strong className="text-slate-900">{candidate.name}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Email:</span>
                <span className="text-slate-700">{candidate.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-semibold">Đánh giá AI:</span>
                <span className="font-extrabold text-emerald-700">
                  Phù hợp {selectedMatch.percent}% ({selectedMatch.owned.length}/{selectedJob.skills.length} kỹ năng)
                </span>
              </div>
            </div>

            <div className="mb-5">
              <label className="block text-xs font-black text-slate-700 uppercase tracking-wider mb-1.5">
                Lời nhắn cho nhà tuyển dụng
              </label>
              <textarea
                rows={3}
                value={applyNote}
                onChange={(e) => setApplyNote(e.target.value)}
                className="w-full p-3.5 rounded-2xl border border-slate-300 text-xs font-semibold text-slate-800 focus:outline-none focus:border-[#0d5f57]"
              />
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowApplyModal(false)}
                className="px-6 py-2.5 rounded-full border border-slate-300 text-slate-600 text-xs font-bold uppercase cursor-pointer hover:bg-slate-50"
              >
                Hủy
              </button>
              <button
                onClick={handleConfirmApply}
                className="px-6 py-2.5 rounded-full bg-[#0d5f57] hover:bg-[#073d35] text-white text-xs font-black uppercase tracking-wider cursor-pointer shadow-md"
              >
                Xác nhận nộp hồ sơ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════ */}
      {/* ── 4. DRAWER DANH SÁCH VIỆC ĐÃ ỨNG TUYỂN ───────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════════ */}
      {showAppliedDrawer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-2xs p-4">
          <div className="bg-white rounded-3xl p-7 max-w-xl w-full shadow-2xl border border-slate-200 animate-in zoom-in-95 relative max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="text-lg font-black text-slate-900">
                  Việc làm đã ứng tuyển ({appliedJobIds.length})
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Theo dõi trạng thái phản hồi từ các nhà tuyển dụng
                </p>
              </div>
              <button
                onClick={() => setShowAppliedDrawer(false)}
                className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center font-bold text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-3 flex-1">
              {appliedJobIds.map((id) => {
                const j = jobs.find((item) => item.id === id);
                if (!j) return null;
                const m = calculateMatch(j.skills);
                return (
                  <div key={id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between gap-3">
                    <div>
                      <h4 className="text-sm font-black text-slate-900">{j.title}</h4>
                      <div className="text-xs font-bold text-slate-500">{j.company} · {j.location}</div>
                      <div className="text-[11px] font-semibold text-emerald-700 mt-1">Độ phù hợp: {m.percent}%</div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                      Đã gửi hồ sơ
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="pt-3 border-t border-slate-100 text-right">
              <button
                onClick={() => setShowAppliedDrawer(false)}
                className="px-6 py-2 rounded-full bg-[#0d5f57] text-white text-xs font-bold uppercase cursor-pointer"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

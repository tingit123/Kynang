import React, { useState, useEffect } from 'react';

const CANDIDATES_DATA = [
  {
    id: 1,
    name: 'Trần Thị Bích Ngọc',
    email: 'ngoc.tran@email.com',
    appliedDate: '15/10',
    matchScore: 83,
    title: 'Sinh viên CNTT năm 4 · Đại học Cần Thơ',
    skillsOwned: ['Python', 'SQL', 'FastAPI', 'Git', 'Docker'],
    skillsMissing: ['Kubernetes'],
    aiComment:
      'Ứng viên có kỹ năng thực tế rất tốt, hoàn thành các dự án backend với Python & FastAPI đạt chất lượng cao. Đã nắm vững Docker, hoàn toàn phù hợp để đảm nhận ngay công việc.'
  },
  {
    id: 2,
    name: 'Nguyễn Văn An',
    email: 'an.nguyen@email.com',
    appliedDate: '14/10',
    matchScore: 67,
    title: 'Sinh viên CNTT năm 4 · Đại học Cần Thơ',
    skillsOwned: ['Python', 'SQL', 'Git', 'REST API'],
    skillsMissing: ['FastAPI', 'Docker'],
    aiComment:
      'Ứng viên nắm chắc nền tảng Python và cơ sở dữ liệu, đã có dự án REST API. Còn thiếu FastAPI và Docker nhưng nền tảng đủ để đào tạo thêm trong thời gian thử việc.'
  },
  {
    id: 3,
    name: 'Lê Minh Quân',
    email: 'quan.le@email.com',
    appliedDate: '14/10',
    matchScore: 50,
    title: 'Kỹ sư phần mềm mới tốt nghiệp · Cần Thơ',
    skillsOwned: ['Python', 'Git', 'Linux'],
    skillsMissing: ['SQL', 'FastAPI', 'Docker'],
    aiComment:
      'Ứng viên có kiến thức lập trình cơ bản tốt, tư duy logic vững. Cần bồi dưỡng thêm kiến thức về hệ quản trị cơ sở dữ liệu và triển khai container.'
  },
  {
    id: 4,
    name: 'Phạm Gia Hân',
    email: 'han.pham@email.com',
    appliedDate: '13/10',
    matchScore: 33,
    title: 'Sinh viên năm 3 · ĐH FPT Cần Thơ',
    skillsOwned: ['Git', 'HTML/CSS'],
    skillsMissing: ['Python', 'SQL', 'FastAPI', 'Docker'],
    aiComment:
      'Kỹ năng hiện tại chưa sát với yêu cầu backend thực tế của vị trí. Khoảng cách kỹ năng lớn, cần thêm thời gian tích lũy đồ án chuyên sâu.'
  }
];

export default function EmployerCandidatesPage() {
  const [candidatesList, setCandidatesList] = useState(CANDIDATES_DATA);
  const [selectedJob, setSelectedJob] = useState('Python Backend Developer · 34 hồ sơ');
  const [selectedCandidate, setSelectedCandidate] = useState(CANDIDATES_DATA[1]); // Default Nguyen Van An as in mockup
  const [invitedList, setInvitedList] = useState([]);
  const [rejectedList, setRejectedList] = useState([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('global_job_applications');
      if (raw) {
        const apps = JSON.parse(raw);
        if (Array.isArray(apps) && apps.length > 0) {
          const formatted = apps.map((a, idx) => ({
            id: a.id || `app_${idx}`,
            name: a.candidate_name,
            email: a.candidate_email,
            appliedDate: a.applied_date || 'Hôm nay',
            matchScore: a.match_score || 67,
            title: 'Sinh viên CNTT năm 4 · Đại học Cần Thơ',
            skillsOwned: a.skills_owned || ['Python', 'SQL', 'Git', 'REST API'],
            skillsMissing: a.skills_missing || ['FastAPI', 'Docker'],
            aiComment: a.note
              ? `Lời nhắn từ ứng viên: "${a.note}". Hệ thống đánh giá độ khớp kỹ năng đạt ${a.match_score}%.`
              : 'Ứng viên nắm chắc nền tảng kỹ năng cốt lõi. Hồ sơ được AI đối soát trực tiếp.'
          }));

          const existingEmails = new Set(formatted.map((c) => c.email));
          const remaining = CANDIDATES_DATA.filter((c) => !existingEmails.has(c.email));
          const merged = [...formatted, ...remaining];
          setCandidatesList(merged);
          setSelectedCandidate(merged[0]);
        }
      }
    } catch (e) {}
  }, [selectedJob]);

  const handleInvite = (candidate) => {
    setInvitedList((prev) => [...prev, candidate.id]);
    window.location.href = `mailto:${candidate.email}?subject=Thư mời phỏng vấn - Mekong Tech&body=Chào ${candidate.name}, Mekong Tech trân trọng mời bạn tham gia buổi phỏng vấn vị trí Backend Developer.`;
  };

  const handleReject = (candidate) => {
    if (window.confirm(`Bạn có chắc chắn muốn từ chối hồ sơ của ${candidate.name}?`)) {
      setRejectedList((prev) => [...prev, candidate.id]);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl">
      {/* ── 1. HEADER TRANG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Quản lý ứng viên
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Xem hồ sơ theo từng tin, đọc bản tóm tắt CV do AI phân tích và mời phỏng vấn.
        </p>
      </div>

      {/* ── 2. BỘ LỌC THEO TIN TUYỂN DỤNG ── */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider shrink-0">
          LỌC THEO TIN TUYỂN DỤNG
        </label>
        <select
          value={selectedJob}
          onChange={(e) => setSelectedJob(e.target.value)}
          className="px-4 py-2.5 rounded-full border border-slate-200 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-[#0d5f57] shadow-2xs max-w-md w-full cursor-pointer"
        >
          <option value="Python Backend Developer · 34 hồ sơ">
            Python Backend Developer · 34 hồ sơ
          </option>
          <option value="Data Analyst / BI Specialist · 21 hồ sơ">
            Data Analyst / BI Specialist · 21 hồ sơ
          </option>
          <option value="DevOps & Cloud Engineer · 40 hồ sơ">
            DevOps & Cloud Engineer · 40 hồ sơ
          </option>
        </select>
      </div>

      {/* ── 3. BỐ CỤC 2 CỘT (DANH SÁCH TRÁI & CHI TIẾT AI PHẢI) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* ── CỘT TRÁI: DANH SÁCH ỨNG VIÊN (5 COLS) ── */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-base font-bold text-slate-900">Ứng viên</h2>
            <span className="text-xs text-slate-400 font-medium">
              Xếp theo mức phù hợp
            </span>
          </div>

          <div className="space-y-3">
            {candidatesList.map((c) => {
              const isSelected = selectedCandidate.id === c.id;
              const isInvited = invitedList.includes(c.id);
              const isRejected = rejectedList.includes(c.id);

              // Badge colors based on score
              let badgeCls = 'bg-[#dcfce7] text-[#0f766e]';
              if (c.matchScore < 40) badgeCls = 'bg-[#ffe4e6] text-[#e11d48]';
              else if (c.matchScore < 60) badgeCls = 'bg-[#fef3c7] text-[#b45309]';
              else if (c.matchScore < 75) badgeCls = 'bg-[#fef9c3] text-[#a16207]';

              return (
                <div
                  key={c.id}
                  onClick={() => setSelectedCandidate(c)}
                  className={`bg-white rounded-2xl p-4.5 cursor-pointer transition-all flex items-center justify-between gap-3 shadow-2xs ${
                    isSelected
                      ? 'border-2 border-[#0d5f57] shadow-sm ring-1 ring-[#0d5f57]/10'
                      : 'border border-slate-150 hover:border-slate-300 hover:shadow-xs'
                  } ${isRejected ? 'opacity-50' : ''}`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-extrabold text-slate-900 truncate flex items-center gap-2">
                      <span>{c.name}</span>
                      {isInvited && (
                        <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">
                          Đã mời
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 font-medium mt-0.5 truncate">
                      {c.email} · Nộp {c.appliedDate}
                    </div>
                  </div>

                  <div className="shrink-0">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-xl text-xs font-black ${badgeCls}`}
                    >
                      {c.matchScore}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── CỘT PHẢI: CHI TIẾT CV SNAPSHOT · AI PHÂN TÍCH (7 COLS) ── */}
        <div className="lg:col-span-7 bg-white rounded-3xl p-7 border border-slate-100 shadow-xs space-y-6">
          {/* Header CV & Độ Khớp */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-xs font-black text-[#0d5f57] uppercase tracking-wider">
                CV SNAPSHOT · AI PHÂN TÍCH
              </div>
              <h2 className="text-2xl font-black text-slate-900 mt-1">
                {selectedCandidate.name}
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 font-medium mt-0.5">
                {selectedCandidate.title}
              </p>
            </div>

            <div className="text-right shrink-0">
              <div className="text-3xl sm:text-4xl font-black text-[#0d5f57]">
                {selectedCandidate.matchScore}%
              </div>
              <div className="text-xs text-slate-500 font-medium mt-0.5">
                phù hợp với tin này
              </div>
            </div>
          </div>

          {/* Thanh Tiến Trình Khớp (Progress Bar) */}
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-[#0d5f57] h-full rounded-full transition-all duration-300"
              style={{ width: `${selectedCandidate.matchScore}%` }}
            />
          </div>

          {/* 2 Khối Kỹ Năng (Kỹ năng đã có & Kỹ năng còn thiếu) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Box 1: Kỹ năng đã có */}
            <div className="bg-[#f8fafc] rounded-2xl p-5 border border-slate-100 space-y-3">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Kỹ năng đã có
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedCandidate.skillsOwned.map((sk) => (
                  <span
                    key={sk}
                    className="px-3 py-1 bg-[#dcfce7] text-[#0f766e] text-xs font-bold rounded-full"
                  >
                    {sk}
                  </span>
                ))}
              </div>
            </div>

            {/* Box 2: Kỹ năng còn thiếu */}
            <div className="bg-[#f8fafc] rounded-2xl p-5 border border-slate-100 space-y-3">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Kỹ năng còn thiếu
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedCandidate.skillsMissing.length > 0 ? (
                  selectedCandidate.skillsMissing.map((sk) => (
                    <span
                      key={sk}
                      className="px-3 py-1 bg-[#ffe4e6] text-[#e11d48] text-xs font-bold rounded-full"
                    >
                      {sk}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400 font-medium italic">
                    Không thiếu kỹ năng nào
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Nhận xét của AI */}
          <div className="bg-[#f8fafc] rounded-2xl p-5 border border-slate-100 space-y-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Nhận xét của AI
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-medium">
              {selectedCandidate.aiComment}
            </p>
          </div>

          {/* Nút Hành Động (Gửi Email Mời Phỏng Vấn & Từ chối) */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => handleInvite(selectedCandidate)}
              className="px-6 py-3 bg-[#0a5146] hover:bg-[#084239] text-white font-extrabold text-xs tracking-wider uppercase rounded-full shadow-md transition-all cursor-pointer inline-flex items-center gap-2"
            >
              GỬI EMAIL MỜI PHỎNG VẤN
            </button>
            <button
              onClick={() => handleReject(selectedCandidate)}
              className="px-6 py-3 border border-rose-200 text-rose-600 hover:bg-rose-50 font-bold text-xs rounded-full transition-colors cursor-pointer"
            >
              Từ chối
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

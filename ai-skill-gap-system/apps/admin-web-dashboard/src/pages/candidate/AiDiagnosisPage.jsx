import React, { useState, useMemo } from 'react';
import { IT_ROLES, IT_SKILL_CATEGORIES, INDUSTRIES } from '../../data/itProfileData';

const DEFAULT_COURSES = [
  { skill: 'Python', title: 'Python for Everybody Specialization', provider: 'Coursera × University of Michigan', platform: 'Coursera', duration: '3 tháng', price: 'Miễn phí (Audit)', url: 'https://www.coursera.org/specializations/python' },
  { skill: 'SQL', title: 'The Complete SQL Bootcamp 2026', provider: 'Udemy × Jose Portilla', platform: 'Udemy', duration: '9 giờ', price: '249.000đ', url: 'https://www.udemy.com/course/the-complete-sql-bootcamp/' },
  { skill: 'Docker', title: 'Docker & Kubernetes: The Practical Guide', provider: 'Udemy × Academind', platform: 'Udemy', duration: '23 giờ', price: '299.000đ', url: 'https://www.udemy.com' },
  { skill: 'React.js', title: 'React - The Complete Guide (incl Next.js)', provider: 'Udemy × Maximilian Schwarzmüller', platform: 'Udemy', duration: '68 giờ', price: '279.000đ', url: 'https://www.udemy.com' },
  { skill: 'Machine Learning', title: 'Machine Learning Specialization', provider: 'DeepLearning.AI × Andrew Ng', platform: 'Coursera', duration: '2 tháng', price: 'Miễn phí (Audit)', url: 'https://www.coursera.org' },
  { skill: 'FastAPI', title: 'Modern APIs with FastAPI and Python', provider: 'Talk Python Training', platform: 'Talk Python', duration: '12 giờ', price: '350.000đ', url: 'https://talkpython.fm' },
  { skill: 'Manual Testing', title: 'Software Testing Bootcamp (QA)', provider: 'Udemy Academy', platform: 'Udemy', duration: '14 giờ', price: '249.000đ', url: 'https://www.udemy.com' }
];

export default function AiDiagnosisPage() {
  // ── Form States ──
  const [fullName, setFullName] = useState('Nguyễn Văn An');
  const [currentRole, setCurrentRole] = useState('Sinh viên năm cuối CNTT / Thực tập sinh');
  const [experienceLevel, setExperienceLevel] = useState('4');

  // Bước 1: Mục tiêu ngành nghề (Industry)
  const [selectedIndustry, setSelectedIndustry] = useState('IT');

  // Bước 2: Chức vụ mục tiêu (Target Role) - Cascading theo Industry
  const [targetRoleId, setTargetRoleId] = useState('software-engineer');

  // Bước 3: Kỹ năng hiện có (Current Skills) - Multi-select hoạt động độc lập
  const [selectedSkills, setSelectedSkills] = useState(['Python', 'Object-Oriented Programming (OOP)', 'Git', 'SQL']);
  const [skillSearchQuery, setSkillSearchQuery] = useState('');

  // ── AI Result States ──
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // Danh sách Role khả dụng theo Industry
  const availableRoles = useMemo(() => {
    if (selectedIndustry === 'IT') {
      return IT_ROLES;
    }
    return [];
  }, [selectedIndustry]);

  // Object role mục tiêu đang chọn
  const activeTargetRole = useMemo(() => {
    return availableRoles.find(r => r.id === targetRoleId) || availableRoles[0] || null;
  }, [availableRoles, targetRoleId]);

  // Danh sách 12 Categories và Kỹ năng khả dụng theo Industry
  const availableCategories = useMemo(() => {
    if (selectedIndustry === 'IT') {
      return IT_SKILL_CATEGORIES;
    }
    return [];
  }, [selectedIndustry]);

  // Lọc kỹ năng theo search query
  const filteredCategories = useMemo(() => {
    const q = skillSearchQuery.trim().toLowerCase();
    if (!q) return availableCategories;

    return availableCategories
      .map(cat => ({
        ...cat,
        skills: cat.skills.filter(s => s.toLowerCase().includes(q))
      }))
      .filter(cat => cat.skills.length > 0);
  }, [availableCategories, skillSearchQuery]);

  // Handlers
  const handleIndustryChange = (e) => {
    const newInd = e.target.value;
    setSelectedIndustry(newInd);
    if (newInd === 'IT') {
      setTargetRoleId(IT_ROLES[0].id);
    } else {
      setTargetRoleId('');
      setSelectedSkills([]);
    }
  };

  // Chọn / bỏ chọn kỹ năng độc lập, không tự động trigger phân tích
  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const removeSkill = (skill) => {
    setSelectedSkills(selectedSkills.filter(s => s !== skill));
  };

  // Kích hoạt phân tích AI - Chỉ chạy khi người dùng bấm nút Submit
  const handleRunDiagnosis = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      setHasAnalyzed(true);
    }, 600);
  };

  // Tính toán kết quả Gap
  const targetRequiredSkills = activeTargetRole ? (activeTargetRole.mustSkills || []) : [];
  const matchedSkills = targetRequiredSkills.filter(s =>
    selectedSkills.some(userSkill => userSkill.toLowerCase() === s.toLowerCase())
  );
  const missingSkills = targetRequiredSkills.filter(s =>
    !selectedSkills.some(userSkill => userSkill.toLowerCase() === s.toLowerCase())
  );
  const matchPct = targetRequiredSkills.length > 0
    ? Math.round((matchedSkills.length / targetRequiredSkills.length) * 100)
    : 0;

  // Lọc khóa học phù hợp với kỹ năng thiếu
  const recommendedCourses = useMemo(() => {
    if (missingSkills.length === 0) return DEFAULT_COURSES.slice(0, 3);
    const matched = DEFAULT_COURSES.filter(c =>
      missingSkills.some(m => c.skill.toLowerCase().includes(m.toLowerCase()) || m.toLowerCase().includes(c.skill.toLowerCase()))
    );
    return matched.length > 0 ? matched : DEFAULT_COURSES.slice(0, 3);
  }, [missingSkills]);

  return (
    <div className="max-w-7xl mx-auto space-y-6" style={{ fontFamily: "'Be Vietnam Pro', system-ui, sans-serif" }}>
      {/* ── TIÊU ĐỀ CHÍNH THEO ẢNH MẪU ── */}
      <div className="text-center space-y-2 mb-8">
        <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
          Gợi ý nghề nghiệp &amp; <span className="text-[#48e5c2]">kỹ năng còn thiếu</span>
        </h1>
        <p className="text-teal-100/90 text-sm max-w-xl mx-auto">
          Chọn ngành, tick kỹ năng bạn có. AI chẩn đoán lỗ hổng và kê đơn khóa học bù đắp ngay.
        </p>
      </div>

      {/* ── KHU VỰC CHÍNH: 2 CỘT ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* ── CỘT TRÁI: FORM CASCADING "HỒ SƠ CỦA BẠN" (5 CỘT TRÊN 12) ── */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 shadow-2xl space-y-4 text-slate-800">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h2 className="text-sm font-extrabold text-[#0f172a] uppercase tracking-wider flex items-center gap-2">
              <span>HỒ SƠ CỦA BẠN</span>
            </h2>
            <button
              type="button"
              onClick={() => {
                setFullName('Nguyễn Văn An');
                setCurrentRole('Sinh viên CNTT');
                setExperienceLevel('4');
                setSelectedSkills(['Python', 'SQL', 'Git', 'HTML', 'CSS']);
              }}
              className="text-[11px] font-bold text-[#0f766e] bg-[#ccfbf1] hover:bg-[#99f6e4] px-3 py-1 rounded-full border border-[#5eead4] transition-colors"
            >
              Sinh viên CNTT (mẫu)
            </button>
          </div>

          {/* TRƯỜNG 0: Họ và tên */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Họ và tên
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Nhập họ và tên..."
              className="w-full px-4 py-2.5 rounded-full border border-slate-200 focus:border-[#5eead4] focus:ring-2 focus:ring-[#ccfbf1] outline-none text-xs font-semibold text-slate-800"
            />
          </div>

          {/* BƯỚC 1: Mục tiêu ngành nghề hướng tới */}
          <div className="p-3.5 rounded-2xl bg-[#f0fdfa] border border-[#ccfbf1] space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-extrabold text-[#0f766e] uppercase tracking-wider">
                1. Mục tiêu ngành nghề hướng tới
              </label>
              <span className="text-[10px] bg-[#ccfbf1] text-[#0f766e] px-2 py-0.5 rounded-full font-extrabold">Bắt buộc</span>
            </div>
            <select
              value={selectedIndustry}
              onChange={handleIndustryChange}
              className="w-full px-4 py-2.5 rounded-full border border-[#99f6e4] focus:border-[#0d9488] outline-none text-xs text-slate-800 bg-white font-bold cursor-pointer"
            >
              {INDUSTRIES.map(ind => (
                <option key={ind.value} value={ind.value}>{ind.label}</option>
              ))}
            </select>
          </div>

          {/* BƯỚC 2: Chức vụ mục tiêu (Target Role) */}
          <div className="p-3.5 rounded-2xl bg-[#f0fdfa] border border-[#5eead4] space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-extrabold text-[#0f766e] uppercase tracking-wider">
                2. Chức vụ mục tiêu
              </label>
              <span className="text-[10px] bg-[#ccfbf1] text-[#0f766e] px-2 py-0.5 rounded-full font-extrabold">
                {availableRoles.length} chức vụ
              </span>
            </div>

            {availableRoles.length > 0 ? (
              <>
                <select
                  value={targetRoleId}
                  onChange={(e) => setTargetRoleId(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-full border border-[#5eead4] focus:border-[#0f766e] outline-none text-xs font-bold text-slate-800 bg-white cursor-pointer"
                >
                  {availableRoles.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name} ({r.nameVN})
                    </option>
                  ))}
                </select>

                {activeTargetRole && (
                  <div className="pt-1 text-xs space-y-1.5">
                    <div className="text-[11px] font-bold text-[#0f766e]">
                      Kỹ năng chuẩn hóa vị trí ({activeTargetRole.mustSkills.length} kỹ năng):
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {activeTargetRole.mustSkills.map(sk => (
                        <span key={sk} className="text-[10px] bg-[#e6fffa] border border-[#a7f3d0] text-[#065f46] px-2.5 py-0.5 rounded-full font-bold">
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="p-3 bg-white rounded-xl border border-slate-200 text-xs text-slate-400 italic text-center">
                Không có dữ liệu chức vụ cho ngành này.
              </div>
            )}
          </div>

          {/* BƯỚC 3: Kỹ năng hiện tại đang có */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-extrabold text-[#0f766e] uppercase tracking-wider">
                3. Kỹ năng hiện tại bạn có
              </label>
              <span className="text-[10px] font-extrabold text-[#0f766e] bg-[#ccfbf1] px-2.5 py-0.5 rounded-full border border-[#99f6e4]">
                Đã chọn: {selectedSkills.length}
              </span>
            </div>

            {/* Danh sách kỹ năng đã chọn */}
            <div className="min-h-[44px] p-2 bg-[#f0fdfa] rounded-2xl border-1.5 border-dashed border-[#5eead4] flex flex-wrap gap-1.5 items-center">
              {selectedSkills.length > 0 ? (
                selectedSkills.map((sk) => (
                  <span
                    key={sk}
                    onClick={() => removeSkill(sk)}
                    className="inline-flex items-center bg-[#dff6f1] hover:bg-[#ccfbf1] text-[#06453f] text-[11px] font-bold px-3 py-1 rounded-full cursor-pointer transition-colors border border-[#bbf2e8] shadow-2xs"
                    title="Bấm để xóa"
                  >
                    <span>{sk}</span>
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-[#0d9488] italic pl-2">
                  Bấm các kỹ năng bên dưới để chọn...
                </span>
              )}
            </div>

            {/* Ô tìm kiếm kỹ năng */}
            {selectedIndustry === 'IT' && (
              <div className="space-y-2">
                <input
                  type="text"
                  value={skillSearchQuery}
                  onChange={(e) => setSkillSearchQuery(e.target.value)}
                  placeholder="🔍 Tìm nhanh kỹ năng..."
                  className="w-full px-3.5 py-2 text-xs rounded-full border border-slate-200 focus:border-[#5eead4] outline-none text-slate-800"
                />

                {/* Danh mục kỹ năng */}
                <div className="max-h-60 overflow-y-auto space-y-2.5 pr-1 border border-slate-100 rounded-2xl p-2.5 bg-slate-50/50">
                  {filteredCategories.map((cat, idx) => (
                    <div key={idx} className="bg-white rounded-xl p-2 border border-slate-100 shadow-2xs space-y-1">
                      <div className="text-[10px] font-extrabold text-[#0f172a] uppercase tracking-wider flex items-center justify-between">
                        <span>{cat.category}</span>
                        <span className="text-slate-400 font-normal">({cat.skills.length})</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {cat.skills.map((skillName) => {
                          const isSelected = selectedSkills.includes(skillName);
                          return (
                            <button
                              key={skillName}
                              type="button"
                              onClick={() => toggleSkill(skillName)}
                              className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold transition-all ${
                                isSelected
                                  ? 'bg-[#ccfbf1] text-[#0f766e] border border-[#5eead4] shadow-2xs'
                                  : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'
                              }`}
                            >
                              {isSelected ? '✓ ' : '+ '}
                              {skillName}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Hai trường Chức vụ lúc trước & Năm học trong Grid 2 cột */}
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-100">
            <div className="space-y-1">
              <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">
                Chức vụ lúc trước
              </label>
              <input
                type="text"
                value={currentRole}
                onChange={(e) => setCurrentRole(e.target.value)}
                placeholder="VD: Sinh viên..."
                className="w-full h-9 px-3 rounded-full border border-slate-200 focus:border-[#5eead4] text-xs text-slate-800 outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">
                Năm học / Kinh nghiệm
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full h-9 px-3 rounded-full border border-slate-200 focus:border-[#5eead4] text-xs text-slate-800 bg-white outline-none cursor-pointer font-medium"
              >
                <option value="1">Năm 1</option>
                <option value="2">Năm 2</option>
                <option value="3">Năm 3</option>
                <option value="4">Năm 4</option>
                <option value="5">Đã tốt nghiệp</option>
                <option value="6">1-3 năm kn</option>
              </select>
            </div>
          </div>

          {/* NÚT SUBMIT THEME TEAL */}
          <button
            onClick={handleRunDiagnosis}
            disabled={analyzing || !activeTargetRole}
            className="w-full h-12 mt-4 rounded-full border-none text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all cursor-pointer active:scale-[0.99]"
            style={{
              background: '#0d5f57',
              boxShadow: '0 6px 20px rgba(13, 95, 87, 0.4)'
            }}
          >
            {analyzing ? (
              <span>Đang chẩn đoán khoảng cách kỹ năng...</span>
            ) : (
              <>
                <span>AI CHẨN ĐOÁN &amp; KÊ ĐƠN KHÓA HỌC</span>
                <span className="w-5 h-5 rounded-full bg-white text-[#0d5f57] flex items-center justify-center text-[10px] font-black">
                  ❯
                </span>
              </>
            )}
          </button>

          {/* KHỐI CÁCH ĐỌC KẾT QUẢ THEO ĐÚNG ẢNH MẪU */}
          <div className="mt-4 p-3.5 bg-[#f0fdfa] border border-[#ccfbf1] rounded-2xl text-xs leading-relaxed">
            <div className="font-extrabold text-[#0f766e] mb-1 text-xs">Cách đọc kết quả</div>
            <div className="text-slate-700"><strong>Đã có:</strong> kỹ năng bạn đã có so với yêu cầu</div>
            <div className="text-slate-700"><strong>Đang thiếu (Gap):</strong> kỹ năng bạn còn thiếu</div>
            <div className="text-slate-700"><strong>Khóa học gợi ý:</strong> bù đắp trực tiếp từng Gap</div>
          </div>
        </div>

        {/* ── CỘT PHẢI: KẾT QUẢ PHÂN TÍCH AI (7 CỘT TRÊN 12) ── */}
        <div className="lg:col-span-7 space-y-6">
          {!hasAnalyzed ? (
            <div className="bg-white rounded-3xl p-16 shadow-2xl text-center flex flex-col items-center justify-center min-h-[480px]">
              <div className="w-18 h-18 border-2.5 border-dashed border-[#5eead4] bg-[#f0fdfa] rounded-full flex items-center justify-center mb-6"></div>
              <h3 className="text-lg font-extrabold text-[#0f172a] mb-2">Chưa có kết quả phân tích</h3>
              <p className="text-slate-500 text-xs max-w-sm mx-auto leading-relaxed">
                Điền hồ sơ bên trái và bấm "AI chẩn đoán &amp; kê đơn khóa học" để xem mức phù hợp, kỹ năng còn thiếu và lộ trình học.
              </p>
            </div>
          ) : (
            <div className="space-y-6 animate-fadeIn">
              {/* Thẻ Điểm Đánh Giá & Tỷ Lệ Phù Hợp */}
              <div className="bg-white rounded-3xl p-6 shadow-2xl space-y-4 text-slate-800">
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
                  <div>
                    <span className="text-xs font-bold text-[#0f766e] uppercase tracking-wider">🎯 Chức vụ bạn đã chọn đánh giá</span>
                    <h3 className="text-xl font-extrabold text-slate-900 mt-1">
                      {fullName} ➔ {activeTargetRole?.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">{activeTargetRole?.nameVN}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-black text-[#0d5f57]">{matchPct}%</span>
                    <div className="text-xs font-semibold text-slate-500">Mức độ phù hợp</div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-3 rounded-full transition-all duration-700 bg-gradient-to-r from-[#0d5f57] to-[#14b8a6]"
                    style={{ width: `${matchPct}%` }}
                  />
                </div>

                {/* 2 Nhóm Kỹ Năng: Có & Thiếu */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {/* Đã có */}
                  <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2">
                    <div className="text-xs font-extrabold text-emerald-800 uppercase flex items-center gap-1.5">
                      <span>✓</span> Kỹ năng đã đáp ứng ({matchedSkills.length})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {matchedSkills.length > 0 ? (
                        matchedSkills.map(s => (
                          <span key={s} className="bg-emerald-100 text-emerald-900 font-bold text-xs px-2.5 py-1 rounded-full">
                            {s}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-slate-400 italic">Chưa trùng khớp</span>
                      )}
                    </div>
                  </div>

                  {/* Đang thiếu (Gap) */}
                  <div className="p-4 rounded-2xl bg-rose-50/70 border border-rose-200 space-y-2">
                    <div className="text-xs font-extrabold text-rose-800 uppercase flex items-center gap-1.5">
                      <span>✕</span> Kỹ năng còn thiếu ({missingSkills.length})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {missingSkills.length > 0 ? (
                        missingSkills.map(s => (
                          <span key={s} className="bg-rose-100 text-rose-900 font-bold text-xs px-2.5 py-1 rounded-full">
                            {s}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-emerald-700 font-bold">Đã đáp ứng đủ 100%!</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Danh sách Khóa Học Kê Đơn Bù Đắp */}
              <div className="bg-white rounded-3xl p-6 shadow-2xl space-y-4 text-slate-800">
                <div>
                  <h3 className="text-base font-extrabold text-[#0f766e] flex items-center gap-2">
                    <span>💊</span> Kê Đơn Khóa Học — Bù Đắp Lỗ Hổng Kỹ Năng
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">Khóa học thực chiến giúp bạn nâng cao năng lực cho vị trí {activeTargetRole?.name}</p>
                </div>

                <div className="space-y-3">
                  {recommendedCourses.map((c, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border border-teal-100 hover:border-[#5eead4] transition-all bg-[#f0fdfa] flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-2xs"
                    >
                      <div className="space-y-1">
                        <div className="inline-block text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 border border-rose-200">
                          Bù đắp kỹ năng: {c.skill}
                        </div>
                        <h4 className="text-sm font-bold text-slate-900">{c.title}</h4>
                        <div className="text-xs text-slate-500 flex flex-wrap gap-3">
                          <span>Nguồn: <strong>{c.provider}</strong></span>
                          <span>Thời lượng: <strong>{c.duration}</strong></span>
                          <span className="font-bold text-emerald-600">Học phí: {c.price}</span>
                        </div>
                      </div>

                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="px-4 py-2 bg-[#0d5f57] hover:bg-[#094741] text-white rounded-full text-xs font-bold text-center whitespace-nowrap self-start md:self-auto shadow-sm"
                      >
                        Vào Học Ngay ↗
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

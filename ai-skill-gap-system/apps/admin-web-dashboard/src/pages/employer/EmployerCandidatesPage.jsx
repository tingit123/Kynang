import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * TASK 3: Quản Lý Ứng Viên (EmployerCandidatesPage.jsx)
 * - 3.1. Dropdown chọn Job: Gọi GET /api/jobs/my-jobs, hiển thị ID và Title trong <select>.
 * - 3.2. Load Ứng viên: Khi đổi selectedJobId, gọi GET /api/jobs/{job_id}/applications -> render Table (Tên, Email, Ngày nộp, Trạng thái).
 * - 3.3. Đọc CV AI: Bấm nút "Xem CV" mở Modal lớn.
 * - 3.4. Modal CV: Phân tích chuỗi JSON từ cv_snapshot_text (Match %, Kỹ năng có/thiếu, Tóm tắt AI) và nút "Gửi Email" (mailto link).
 */
export default function EmployerCandidatesPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [applications, setApplications] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingApps, setLoadingApps] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // CV Modal State
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  // 3.1. Dropdown chọn Job: Lấy danh sách Job của công ty
  useEffect(() => {
    const fetchJobs = async () => {
      setLoadingJobs(true);
      setErrorMsg('');
      try {
        const res = await fetch(`${API_BASE}/api/jobs/my-jobs`, {
          headers: getAuthHeaders()
        });

        if (res.ok) {
          const data = await res.json();
          const list = Array.isArray(data) ? data : [];
          setJobs(list);
          if (list.length > 0) {
            setSelectedJobId(list[0].id.toString());
          }
        } else {
          setErrorMsg('Không thể tải danh sách tin tuyển dụng của công ty.');
        }
      } catch (err) {
        console.error('Lỗi khi tải danh sách job:', err);
        setErrorMsg('Lỗi kết nối máy chủ khi tải danh sách tin tuyển dụng.');
      } finally {
        setLoadingJobs(false);
      }
    };

    fetchJobs();
  }, []);

  // 3.2. Load Ứng viên: Khi selectedJobId thay đổi, gọi API lấy danh sách hồ sơ
  useEffect(() => {
    if (!selectedJobId) {
      setApplications([]);
      return;
    }

    const fetchApplications = async () => {
      setLoadingApps(true);
      setErrorMsg('');
      try {
        const res = await fetch(`${API_BASE}/api/jobs/${selectedJobId}/applications`, {
          headers: getAuthHeaders()
        });

        if (res.ok) {
          const data = await res.json();
          setApplications(Array.isArray(data) ? data : []);
        } else {
          setApplications([]);
        }
      } catch (err) {
        console.error('Lỗi khi tải danh sách hồ sơ:', err);
        setApplications([]);
      } finally {
        setLoadingApps(false);
      }
    };

    fetchApplications();
  }, [selectedJobId]);

  const selectedJob = jobs.find(j => j.id.toString() === selectedJobId);

  // 3.4. Hàm bóc tách chuỗi JSON từ cv_snapshot_text
  const parseCvSnapshot = (snapshotText) => {
    if (!snapshotText) return null;
    try {
      const parsed = typeof snapshotText === 'object' ? snapshotText : JSON.parse(snapshotText);
      return parsed;
    } catch (e) {
      // Nếu không phải chuỗi JSON thì hiển thị dưới dạng raw text
      return { raw_text: snapshotText };
    }
  };

  const cvData = selectedCandidate ? parseCvSnapshot(selectedCandidate.cv_snapshot_text) : null;

  return (
    <div className="space-y-6">
      {/* ── HEADER & BỘ LỌC CHỌN JOB ── */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="p-2 bg-sky-50 text-[#0284c7] rounded-xl text-xl">📑</span>
          <h1 className="text-xl sm:text-2xl font-black text-slate-800 tracking-tight">
            Quản Lý Ứng Viên Ứng Tuyển
          </h1>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Theo dõi danh sách hồ sơ ứng viên theo từng vị trí tuyển dụng và đánh giá mức độ tương thích kỹ năng AI
        </p>

        {/* 3.1. Dropdown chọn Job */}
        <div className="mt-5 pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-600 shrink-0">
            Xem hồ sơ ứng viên cho tin:
          </label>
          {loadingJobs ? (
            <div className="text-xs text-slate-400 font-semibold animate-pulse">
              Đang tải danh sách tin tuyển dụng...
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-xs text-slate-400 italic font-semibold">
              Chưa có tin tuyển dụng nào được tạo.
            </div>
          ) : (
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-slate-300 text-sm font-bold text-slate-800 bg-white focus:outline-none focus:border-[#0284c7] focus:ring-3 focus:ring-sky-500/15 max-w-lg w-full shadow-xs cursor-pointer"
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  #{job.id} • {job.title} ({job.industry})
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-sm font-semibold rounded-xl">
          {errorMsg}
        </div>
      )}

      {/* ── 3.2. BẢNG DANH SÁCH ỨNG VIÊN ── */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="font-black text-slate-800 text-base flex items-center gap-2">
            <span>Danh sách hồ sơ nhận được</span>
            <span className="text-xs font-bold px-2.5 py-0.5 bg-sky-100 text-[#0284c7] rounded-full">
              {applications.length} hồ sơ
            </span>
          </div>
          {selectedJob && (
            <div className="text-xs text-slate-500 hidden sm:block">
              Vị trí tuyển: <strong className="text-slate-800 font-bold">{selectedJob.title}</strong>
            </div>
          )}
        </div>

        {loadingApps ? (
          <div className="p-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
            <p className="text-sm font-semibold text-slate-500">Đang tải hồ sơ ứng viên...</p>
          </div>
        ) : applications.length === 0 ? (
          <div className="p-16 text-center">
            <div className="text-5xl mb-3">📬</div>
            <h3 className="text-base font-extrabold text-slate-700">Chưa có hồ sơ nào nộp vào vị trí này</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              {jobs.length === 0
                ? 'Vui lòng đăng tin tuyển dụng trước để ứng viên có thể nộp hồ sơ.'
                : 'Tin tuyển dụng đang được công khai. Hệ thống sẽ tự động cập nhật ngay khi có ứng viên mới nộp đơn.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100 font-extrabold">
                <tr>
                  <th className="py-3.5 px-5">#</th>
                  <th className="py-3.5 px-5">Tên ứng viên</th>
                  <th className="py-3.5 px-5">Email liên hệ</th>
                  <th className="py-3.5 px-5">Ngày nộp đơn</th>
                  <th className="py-3.5 px-5">Trạng thái hồ sơ</th>
                  <th className="py-3.5 px-5 text-center">Đánh giá AI</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app, idx) => (
                  <tr key={app.id || idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5 font-bold text-slate-400">{idx + 1}</td>
                    
                    {/* Tên ứng viên */}
                    <td className="py-3.5 px-5 font-black text-slate-800">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-linear-to-br from-[#0284c7] to-sky-600 text-white font-bold text-xs flex items-center justify-center shrink-0 shadow-2xs">
                          {(app.candidate_name || 'U').charAt(0).toUpperCase()}
                        </div>
                        <span>{app.candidate_name || 'Ứng viên tiềm năng'}</span>
                      </div>
                    </td>

                    {/* Email */}
                    <td className="py-3.5 px-5 text-slate-600 font-semibold">
                      {app.candidate_email}
                    </td>

                    {/* Ngày nộp */}
                    <td className="py-3.5 px-5 text-xs text-slate-500 font-medium">
                      {app.applied_at ? new Date(app.applied_at).toLocaleDateString('vi-VN') : 'Gần đây'}
                    </td>

                    {/* Trạng thái */}
                    <td className="py-3.5 px-5">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {app.status || 'Đã nộp'}
                      </span>
                    </td>

                    {/* 3.3. Nút Xem CV AI */}
                    <td className="py-3.5 px-5 text-center">
                      <button
                        onClick={() => setSelectedCandidate(app)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#0284c7] hover:bg-[#0369a1] text-white text-xs font-bold shadow-xs transition-colors cursor-pointer"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <span>Xem CV AI</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════ */}
      {/* ── 3.3 & 3.4. MODAL XEM CHI TIẾT CV & PHÂN TÍCH AI ──     */}
      {/* ══════════════════════════════════════════════════════════ */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col border border-slate-100 overflow-hidden">
            {/* Header Modal */}
            <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-2xl bg-[#0284c7] text-white font-black text-lg flex items-center justify-center shadow-xs">
                  {(selectedCandidate.candidate_name || 'U').charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-800">
                    {selectedCandidate.candidate_name || 'Hồ sơ Ứng viên'}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    Email: <span className="text-slate-700 font-semibold">{selectedCandidate.candidate_email}</span> • Ngày nộp: {selectedCandidate.applied_at ? new Date(selectedCandidate.applied_at).toLocaleString('vi-VN') : 'Hôm nay'}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCandidate(null)}
                className="w-8 h-8 rounded-full bg-white text-slate-400 hover:text-slate-700 border border-slate-200 flex items-center justify-center transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Nội dung Modal: Phân tích JSON từ cv_snapshot_text */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              {/* Thẻ AI Header */}
              <div className="flex items-center justify-between bg-sky-50 border border-sky-200 p-3.5 rounded-2xl text-sky-950">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🤖</span>
                  <span className="font-extrabold text-sm">Trích Xuất Hồ Sơ & Đánh Giá Tương Thích AI:</span>
                </div>
                <span className="text-xs font-bold px-3 py-1 bg-white text-[#0284c7] rounded-xl shadow-2xs border border-sky-100">
                  {selectedCandidate.status || 'Hồ sơ hợp lệ'}
                </span>
              </div>

              {/* Nếu parse được JSON có trường match_score hoặc skills */}
              {cvData && !cvData.raw_text ? (
                <div className="space-y-4">
                  {/* Điểm tương thích % (Match score) nếu có */}
                  {(cvData.match_score !== undefined || cvData.match_percentage !== undefined) && (
                    <div className="p-4 bg-linear-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl flex items-center justify-between">
                      <div>
                        <div className="text-xs font-bold text-emerald-800 uppercase tracking-wider">
                          Độ Phù Hợp Kỹ Năng Với Vị Trí
                        </div>
                        <div className="text-2xl font-black text-emerald-600 mt-0.5">
                          {cvData.match_score ?? cvData.match_percentage}%
                        </div>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-emerald-500 text-white font-black flex items-center justify-center text-sm shadow-md">
                        ✓ AI
                      </div>
                    </div>
                  )}

                  {/* Kỹ năng đáp ứng (Matched Skills) */}
                  {cvData.matched_skills && Array.isArray(cvData.matched_skills) && (
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                      <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <span className="text-emerald-600 font-bold">✓</span> Kỹ năng ứng viên sở hữu (Khớp với tin tuyển dụng):
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {cvData.matched_skills.map((s, idx) => (
                          <span key={idx} className="px-2.5 py-1 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-lg border border-emerald-200">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Kỹ năng còn thiếu (Missing Skills) */}
                  {cvData.missing_skills && Array.isArray(cvData.missing_skills) && (
                    <div className="p-4 bg-rose-50/70 border border-rose-200 rounded-2xl">
                      <div className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <span className="text-rose-600 font-bold">!</span> Kỹ năng cần bổ sung / còn thiếu:
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {cvData.missing_skills.map((s, idx) => (
                          <span key={idx} className="px-2.5 py-1 bg-white text-rose-700 font-bold text-xs rounded-lg border border-rose-200">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Tóm tắt CV / Trích đoạn */}
                  {cvData.summary && (
                    <div className="p-4 bg-white border border-slate-200 rounded-2xl">
                      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                        Tóm tắt năng lực nổi bật:
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed font-medium">
                        {cvData.summary}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                /* Raw text hoặc JSON dạng chuỗi */
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-slate-700 leading-relaxed font-mono text-xs whitespace-pre-wrap max-h-96 overflow-y-auto shadow-inner">
                  {selectedCandidate.cv_snapshot_text || (
                    <span className="font-sans text-slate-400 italic">
                      Ứng viên không có bản chụp văn bản hồ sơ chi tiết.
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer: Gửi Email qua mailto */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <a
                href={`mailto:${selectedCandidate.candidate_email}?subject=${encodeURIComponent(`[${selectedJob?.company || 'Doanh nghiệp'}] Thư mời phỏng vấn vị trí ${selectedJob?.title || ''}`)}&body=${encodeURIComponent(`Chào bạn ${selectedCandidate.candidate_name},\n\nChúng tôi đã nhận được hồ sơ của bạn cho vị trí ${selectedJob?.title || ''}. Chúng tôi rất ấn tượng với năng lực của bạn và trân trọng mời bạn tham gia buổi phỏng vấn...\n\nTrân trọng,\n${selectedJob?.company || 'Phòng Nhân Sự'}`)}`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors cursor-pointer"
              >
                <span>✉️</span>
                <span>Gửi Email Mời Phỏng Vấn</span>
              </a>

              <button
                type="button"
                onClick={() => setSelectedCandidate(null)}
                className="px-5 py-2.5 bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs rounded-xl transition-colors cursor-pointer"
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

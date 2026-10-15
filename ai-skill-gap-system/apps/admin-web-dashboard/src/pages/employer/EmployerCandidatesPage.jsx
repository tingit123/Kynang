import React, { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  // 1. Lấy danh sách tin tuyển dụng của công ty
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
          setErrorMsg('Không thể tải danh sách tin tuyển dụng.');
        }
      } catch (err) {
        console.error(err);
        setErrorMsg('Lỗi kết nối khi tải danh sách tin.');
      } finally {
        setLoadingJobs(false);
      }
    };

    fetchJobs();
  }, []);

  // 2. Lấy danh sách ứng viên của tin được chọn
  useEffect(() => {
    if (!selectedJobId) {
      setApplications([]);
      return;
    }

    const fetchApplications = async () => {
      setLoadingApps(true);
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
        console.error(err);
        setApplications([]);
      } finally {
        setLoadingApps(false);
      }
    };

    fetchApplications();
  }, [selectedJobId]);

  const selectedJob = jobs.find(j => j.id.toString() === selectedJobId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <h1 className="text-xl sm:text-2xl font-black text-slate-800 flex items-center gap-2">
          <span>📑</span> Quản Lý Ứng Viên Ứng Tuyển
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Theo dõi hồ sơ ứng viên nộp vào từng tin tuyển dụng và đánh giá mức độ tương thích kỹ năng AI
        </p>

        {/* Filter Dropdown */}
        <div className="mt-5 flex flex-col sm:flex-row sm:items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-600 shrink-0">
            Xem hồ sơ theo tin:
          </label>
          {loadingJobs ? (
            <div className="text-xs text-slate-400">Đang tải danh sách tin...</div>
          ) : jobs.length === 0 ? (
            <div className="text-xs text-slate-400 italic">Bạn chưa đăng tin tuyển dụng nào</div>
          ) : (
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-800 bg-white focus:outline-none focus:border-sky-500 focus:ring-3 focus:ring-sky-500/15 max-w-md w-full shadow-xs cursor-pointer"
            >
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  #{job.id} - {job.title} ({job.industry})
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

      {/* Bảng Danh Sách Ứng Viên */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="font-extrabold text-slate-800 text-base flex items-center gap-2">
            <span>Danh sách hồ sơ</span>
            <span className="text-xs font-bold px-2 py-0.5 bg-sky-100 text-sky-800 rounded-full">
              {applications.length} ứng viên
            </span>
          </div>
          {selectedJob && (
            <div className="text-xs text-slate-500 hidden sm:block">
              Vị trí: <strong className="text-slate-700">{selectedJob.title}</strong>
            </div>
          )}
        </div>

        {loadingApps ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-sky-500 border-t-transparent mb-3" />
            <p className="text-sm font-medium text-slate-500">Đang tải hồ sơ ứng viên...</p>
          </div>
        ) : applications.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-4xl mb-3">📬</div>
            <h3 className="text-base font-bold text-slate-700">Chưa có ứng viên nào nộp hồ sơ</h3>
            <p className="text-xs text-slate-400 mt-1">
              {jobs.length === 0
                ? 'Hãy đăng tin tuyển dụng trước để bắt đầu nhận hồ sơ.'
                : 'Tin tuyển dụng này hiện chưa có ứng viên nộp đơn. Hãy kiên nhẫn chờ hoặc chia sẻ tin tuyển dụng.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100">
                <tr>
                  <th className="py-3 px-4 font-bold">#</th>
                  <th className="py-3 px-4 font-bold">Tên ứng viên</th>
                  <th className="py-3 px-4 font-bold">Email</th>
                  <th className="py-3 px-4 font-bold">Ngày nộp</th>
                  <th className="py-3 px-4 font-bold">Trạng thái</th>
                  <th className="py-3 px-4 font-bold text-center">Hành động</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app, idx) => (
                  <tr key={app.id || idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-medium text-slate-400">{idx + 1}</td>
                    <td className="py-3 px-4 font-bold text-slate-800">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-800 font-bold text-xs flex items-center justify-center">
                          {(app.candidate_name || 'U').charAt(0).toUpperCase()}
                        </div>
                        <span>{app.candidate_name || 'Ứng viên'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-medium">
                      {app.candidate_email}
                    </td>
                    <td className="py-3 px-4 text-xs text-slate-500">
                      {app.applied_at ? new Date(app.applied_at).toLocaleDateString('vi-VN') : 'Mới nộp'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                        {app.status || 'Đã nộp'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => setSelectedCandidate(app)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0284c7] hover:bg-[#0369a1] text-white text-xs font-bold shadow-xs transition-colors cursor-pointer"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <span>Xem CV</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── MODAL XEM CHI TIẾT CV & PHÂN TÍCH AI ── */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col border border-slate-100 overflow-hidden">
            {/* Modal Header */}
            <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#0284c7] text-white font-black text-base flex items-center justify-center">
                  {(selectedCandidate.candidate_name || 'U').charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-800">
                    {selectedCandidate.candidate_name}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    Email: <span className="text-slate-700">{selectedCandidate.candidate_email}</span> • Ngày nộp: {selectedCandidate.applied_at ? new Date(selectedCandidate.applied_at).toLocaleString('vi-VN') : 'Hôm nay'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="w-8 h-8 rounded-full bg-white text-slate-400 hover:text-slate-700 border border-slate-200 flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Modal Body: CV Snapshot */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4 font-sans text-sm">
              <div className="flex items-center justify-between bg-sky-50 border border-sky-200 p-3.5 rounded-xl text-sky-900">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🤖</span>
                  <span className="font-bold text-xs sm:text-sm">Bản chụp hồ sơ & Trích xuất kỹ năng bằng AI:</span>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 bg-white text-sky-700 rounded-lg shadow-2xs">
                  {selectedCandidate.status || 'Ứng viên tiềm năng'}
                </span>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-slate-700 leading-relaxed font-mono text-xs whitespace-pre-wrap max-h-96 overflow-y-auto shadow-inner">
                {selectedCandidate.cv_snapshot_text ? (
                  selectedCandidate.cv_snapshot_text
                ) : (
                  <span className="font-sans text-slate-400 italic">
                    Ứng viên chưa đính kèm nội dung văn bản chi tiết trong bản chụp hồ sơ.
                  </span>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <a
                href={`mailto:${selectedCandidate.candidate_email}?subject=Thư mời phỏng vấn vị trí ${selectedJob?.title || ''}`}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors"
              >
                ✉️ Gửi Email Mời Phỏng Vấn
              </a>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="px-5 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs rounded-xl transition-colors"
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

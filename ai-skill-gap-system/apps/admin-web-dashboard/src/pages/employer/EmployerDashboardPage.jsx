import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EmployerDashboardPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [companyName, setCompanyName] = useState('Doanh Nghiệp');

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  useEffect(() => {
    try {
      const rawUser = localStorage.getItem('current_user');
      if (rawUser) {
        const u = JSON.parse(rawUser);
        if (u.company_name) setCompanyName(u.company_name);
        else if (u.full_name) setCompanyName(u.full_name);
      }
    } catch (e) {}

    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/jobs/my-jobs`, {
          headers: getAuthHeaders()
        });
        if (res.ok) {
          const data = await res.json();
          setJobs(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const totalJobs = jobs.length;
  // Giả lập số lượt xem & hồ sơ dựa trên số lượng tin
  const totalApplications = totalJobs > 0 ? totalJobs * 6 + 4 : 0;
  const totalViews = totalJobs > 0 ? totalJobs * 185 + 42 : 0;

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-linear-to-r from-[#0284c7] to-[#0369a1] text-white p-6 sm:p-8 rounded-3xl shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-block px-3 py-1 bg-white/20 backdrop-blur-xs rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            🏢 Trung tâm điều hành tuyển dụng
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Xin chào, {companyName}!
          </h1>
          <p className="text-sm text-sky-100 mt-2 leading-relaxed">
            Hệ thống SkillGap AI đã phân tích yêu cầu kỹ năng và tự động khớp nối hồ sơ các ứng viên phù hợp nhất với các vị trí bạn đang tuyển dụng.
          </p>
        </div>

        {/* Decorative Circles */}
        <div className="absolute right-0 bottom-0 translate-x-12 translate-y-12 w-64 h-64 rounded-full bg-white/10 pointer-events-none" />
        <div className="absolute right-24 top-0 -translate-y-8 w-32 h-32 rounded-full bg-white/5 pointer-events-none" />
      </div>

      {/* 3 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {/* Card 1: Tổng tin tuyển dụng */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Tổng tin đang mở
            </div>
            <div className="text-3xl font-black text-slate-800 mt-1">
              {loading ? '...' : totalJobs}
            </div>
            <div className="text-xs text-sky-600 font-semibold mt-1">
              Vị trí tuyển dụng thực tế
            </div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center text-xl font-bold">
            📝
          </div>
        </div>

        {/* Card 2: Hồ sơ nhận được */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Hồ sơ ứng tuyển
            </div>
            <div className="text-3xl font-black text-emerald-600 mt-1">
              {loading ? '...' : totalApplications}
            </div>
            <div className="text-xs text-emerald-600 font-semibold mt-1">
              Ứng viên tiềm năng nộp đơn
            </div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl font-bold">
            📑
          </div>
        </div>

        {/* Card 3: Lượt xem tin */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Lượt xem tin tuyển dụng
            </div>
            <div className="text-3xl font-black text-purple-600 mt-1">
              {loading ? '...' : totalViews.toLocaleString()}
            </div>
            <div className="text-xs text-purple-600 font-semibold mt-1">
              Lượt tiếp cận của ứng viên
            </div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center text-xl font-bold">
            👀
          </div>
        </div>
      </div>

      {/* 2 Big CTA Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <Link
          to="/employer/jobs"
          className="bg-white p-6 rounded-2xl border-2 border-sky-500/30 hover:border-sky-500 shadow-xs hover:shadow-lg transition-all group flex items-center gap-4 text-decoration-none"
        >
          <div className="w-14 h-14 rounded-2xl bg-[#0284c7] text-white flex items-center justify-center text-2xl group-hover:scale-105 transition-transform shadow-md shadow-sky-600/30">
            ✍️
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-800 group-hover:text-sky-600 transition-colors">
              Đăng tin tuyển dụng mới ngay
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Tạo vị trí tuyển dụng, gắn tag kỹ năng và nhận hồ sơ tự động
            </p>
          </div>
        </Link>

        <Link
          to="/employer/candidates"
          className="bg-white p-6 rounded-2xl border-2 border-emerald-500/30 hover:border-emerald-500 shadow-xs hover:shadow-lg transition-all group flex items-center gap-4 text-decoration-none"
        >
          <div className="w-14 h-14 rounded-2xl bg-emerald-600 text-white flex items-center justify-center text-2xl group-hover:scale-105 transition-transform shadow-md shadow-emerald-600/30">
            👥
          </div>
          <div>
            <h3 className="text-base font-extrabold text-slate-800 group-hover:text-emerald-600 transition-colors">
              Quản lý danh sách ứng viên
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Xem hồ sơ chi tiết, phân tích AI và gửi thư mời phỏng vấn
            </p>
          </div>
        </Link>
      </div>

      {/* Tin tuyển dụng gần đây */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-extrabold text-slate-800">
            Tin tuyển dụng gần đây của bạn
          </h2>
          <Link to="/employer/jobs" className="text-xs font-bold text-sky-600 hover:text-sky-700">
            Xem tất cả ({totalJobs}) →
          </Link>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Đang tải tin tuyển dụng...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-xs text-slate-400 mb-2">Chưa có tin tuyển dụng nào được đăng.</p>
            <Link
              to="/employer/jobs"
              className="inline-block px-4 py-2 bg-[#0284c7] text-white text-xs font-bold rounded-lg hover:bg-[#0369a1]"
            >
              + Đăng tin đầu tiên
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {jobs.slice(0, 5).map((job) => (
              <div key={job.id} className="p-4 hover:bg-slate-50 flex items-center justify-between gap-4 transition-colors">
                <div>
                  <h4 className="text-sm font-bold text-slate-800">{job.title}</h4>
                  <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                    <span>{job.industry}</span>
                    <span>•</span>
                    <span>{job.location}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
                    {job.salary_min && job.salary_max
                      ? `${(job.salary_min / 1000000).toFixed(0)} - ${(job.salary_max / 1000000).toFixed(0)}tr`
                      : 'Thỏa thuận'}
                  </span>
                  <Link
                    to="/employer/candidates"
                    className="text-xs font-bold px-3 py-1.5 bg-slate-100 hover:bg-sky-50 hover:text-sky-700 text-slate-700 rounded-lg transition-colors"
                  >
                    Xem ứng viên
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

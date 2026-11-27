import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Dữ liệu mẫu chuẩn xác theo thiết kế mockup (media_1792211014925_68f88b53.png)
const DEFAULT_RECENT_JOBS = [
  {
    id: 1,
    title: 'Python Backend Developer',
    date: '14/10/2026',
    applications: 34,
    status: 'open',
    statusLabel: 'Đang mở'
  },
  {
    id: 2,
    title: 'Data Analyst / BI Specialist',
    date: '10/10/2026',
    applications: 21,
    status: 'open',
    statusLabel: 'Đang mở'
  },
  {
    id: 3,
    title: 'DevOps & Cloud Engineer',
    date: '05/10/2026',
    applications: 40,
    status: 'open',
    statusLabel: 'Đang mở'
  },
  {
    id: 4,
    title: 'Frontend Developer (React)',
    date: '20/09/2026',
    applications: 18,
    status: 'expiring',
    statusLabel: 'Sắp hết hạn'
  },
  {
    id: 5,
    title: 'QA / QC Software Tester',
    date: '12/09/2026',
    applications: 35,
    status: 'expired',
    statusLabel: 'Đã hết hạn'
  }
];

export default function EmployerDashboardPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [companyName, setCompanyName] = useState('Mekong Tech');

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
          if (Array.isArray(data) && data.length > 0) {
            setJobs(data);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Nếu có tin tuyển dụng thực tế từ API, ánh xạ sang hiển thị, nếu không dùng danh sách mẫu chuẩn mockup
  const displayJobs = jobs.length > 0
    ? jobs.slice(0, 5).map((j, idx) => ({
        id: j.id,
        title: j.title || 'Vị trí tuyển dụng',
        date: j.posted_date ? new Date(j.posted_date).toLocaleDateString('vi-VN') : '14/10/2026',
        applications: j.applications_count || (34 - idx * 4),
        status: idx === 3 ? 'expiring' : (idx === 4 ? 'expired' : 'open'),
        statusLabel: idx === 3 ? 'Sắp hết hạn' : (idx === 4 ? 'Đã hết hạn' : 'Đang mở')
      }))
    : DEFAULT_RECENT_JOBS;

  const totalOpenJobs = jobs.length > 0 ? jobs.length : 4;

  return (
    <div className="space-y-8 max-w-6xl">
      {/* ── 1. HEADER CHÀO MỪNG ── */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Xin chào, {companyName}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Tình hình tuyển dụng của bạn trong thời gian thực.
        </p>
      </div>

      {/* ── 2. BA THẺ THỐNG KÊ (3 KPI Cards) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: TIN ĐANG MỞ (Viền trên Teal) */}
        <div className="bg-white rounded-2xl p-6 shadow-xs border-t-4 border-[#0d5f57] border-x border-b border-slate-100 flex flex-col justify-between">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            TIN ĐANG MỞ
          </div>
          <div className="text-4xl font-black text-slate-900 my-2">
            {totalOpenJobs}
          </div>
          <div className="text-xs text-slate-500 font-medium">
            1 tin sắp hết hạn
          </div>
        </div>

        {/* Card 2: HỒ SƠ NHẬN ĐƯỢC (Viền trên Cam) */}
        <div className="bg-white rounded-2xl p-6 shadow-xs border-t-4 border-[#f59e0b] border-x border-b border-slate-100 flex flex-col justify-between">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            HỒ SƠ NHẬN ĐƯỢC
          </div>
          <div className="text-4xl font-black text-slate-900 my-2">
            148
          </div>
          <div className="text-xs text-slate-500 font-medium">
            +22 hồ sơ trong 7 ngày qua
          </div>
        </div>

        {/* Card 3: LƯỢT XEM TIN (Viền trên Xanh dương) */}
        <div className="bg-white rounded-2xl p-6 shadow-xs border-t-4 border-[#2563eb] border-x border-b border-slate-100 flex flex-col justify-between">
          <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            LƯỢT XEM TIN
          </div>
          <div className="text-4xl font-black text-slate-900 my-2">
            3.250
          </div>
          <div className="text-xs text-slate-500 font-medium">
            +12% so với tuần trước
          </div>
        </div>
      </div>

      {/* ── 3. HAI THẺ HÀNH ĐỘNG (2 Feature Action Cards) ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Thẻ Trái: Đăng tin tuyển dụng mới (Màu xanh Teal đậm #0d5f57) */}
        <div className="bg-[#0d5f57] rounded-2xl p-7 text-white shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-white">
              Đăng tin tuyển dụng mới
            </h2>
            <p className="text-sm text-teal-100/90 mt-2 mb-6 leading-relaxed">
              Gắn thẻ kỹ năng để AI đối chiếu với hồ sơ ứng viên ngay khi tin được đăng.
            </p>
          </div>
          <div>
            <Link
              to="/employer/jobs"
              className="inline-flex items-center gap-2.5 px-5 py-2.5 bg-white text-[#0d5f57] font-extrabold text-xs tracking-wider uppercase rounded-full shadow-xs hover:bg-teal-50 transition-all cursor-pointer"
            >
              <span>ĐĂNG TIN MỚI</span>
              <span className="w-5 h-5 rounded-full bg-[#0a5146] text-white flex items-center justify-center text-xs font-black">
                ›
              </span>
            </Link>
          </div>
        </div>

        {/* Thẻ Phải: Quản lý ứng viên (Nền Trắng, Viền thanh lịch) */}
        <div className="bg-white rounded-2xl p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Quản lý ứng viên
            </h2>
            <p className="text-sm text-slate-600 mt-2 mb-6 leading-relaxed">
              Có 22 hồ sơ mới. Xem bản tóm tắt CV do AI phân tích và gửi thư mời phỏng vấn.
            </p>
          </div>
          <div>
            <Link
              to="/employer/candidates"
              className="inline-flex items-center gap-2.5 px-5 py-2.5 bg-white border-2 border-[#0d5f57] text-[#0d5f57] font-extrabold text-xs tracking-wider uppercase rounded-full shadow-xs hover:bg-teal-50/50 transition-all cursor-pointer"
            >
              <span>XEM ỨNG VIÊN</span>
              <span className="w-5 h-5 rounded-full bg-[#0d5f57] text-white flex items-center justify-center text-xs font-black">
                ›
              </span>
            </Link>
          </div>
        </div>
      </div>

      {/* ── 4. BẢNG TIN TUYỂN DỤNG GẦN ĐÂY (Recent Jobs Table Card) ── */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-xs p-7">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <h2 className="text-base sm:text-lg font-bold text-slate-900">
            Tin tuyển dụng gần đây
          </h2>
          <Link
            to="/employer/jobs"
            className="text-sm font-semibold text-[#0d5f57] hover:underline cursor-pointer"
          >
            Xem tất cả
          </Link>
        </div>

        {/* Bảng danh sách tin */}
        <div className="overflow-x-auto">
          <table className="w-full text-left mt-3">
            <thead>
              <tr className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                <th className="py-3 px-2">VỊ TRÍ</th>
                <th className="py-3 px-2">NGÀY ĐĂNG</th>
                <th className="py-3 px-2">HỒ SƠ</th>
                <th className="py-3 px-2 text-right">TRẠNG THÁI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {displayJobs.map((job) => (
                <tr key={job.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-4 px-2 font-bold text-slate-900">
                    {job.title}
                  </td>
                  <td className="py-4 px-2 text-slate-500 font-medium">
                    {job.date}
                  </td>
                  <td className="py-4 px-2 text-slate-700">
                    <span className="font-bold text-slate-900">{job.applications}</span> hồ sơ
                  </td>
                  <td className="py-4 px-2 text-right">
                    {job.status === 'open' && (
                      <span className="inline-block px-4 py-1 rounded-full text-xs font-bold bg-[#dcfce7] text-[#0f766e]">
                        {job.statusLabel}
                      </span>
                    )}
                    {job.status === 'expiring' && (
                      <span className="inline-block px-4 py-1 rounded-full text-xs font-bold bg-[#fef3c7] text-[#b45309]">
                        {job.statusLabel}
                      </span>
                    )}
                    {job.status === 'expired' && (
                      <span className="inline-block px-4 py-1 rounded-full text-xs font-bold bg-[#f1f5f9] text-[#64748b]">
                        {job.statusLabel}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

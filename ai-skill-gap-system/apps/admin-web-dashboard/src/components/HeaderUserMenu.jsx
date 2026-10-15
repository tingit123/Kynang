import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Cụm User Avatar + Tên + Nút Đăng xuất dùng chung cho Header của Admin, Employer, Provider.
 * Thay thế hoàn toàn các nút Đăng nhập / Đăng ký.
 */
export default function HeaderUserMenu({ roleBadgeText = 'Quản trị viên', defaultName = 'Người dùng' }) {
  const navigate = useNavigate();

  let currentUser = {
    full_name: defaultName,
    email: '',
    role: ''
  };

  try {
    const raw = localStorage.getItem('current_user');
    if (raw) currentUser = { ...currentUser, ...JSON.parse(raw) };
  } catch (e) {}

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    navigate('/');
  };

  const initialLetter = (currentUser.full_name || 'U').charAt(0).toUpperCase();

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
      {/* Thông tin người dùng & Avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '50%',
          backgroundColor: '#0fa39e',
          color: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          fontSize: '15px',
          boxShadow: '0 2px 6px rgba(15,163,158,0.3)'
        }}>
          {initialLetter}
        </div>
        <div style={{ lineHeight: 1.2 }}>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#1e293b' }}>
            {currentUser.full_name || defaultName}
          </div>
          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
            {roleBadgeText}
          </div>
        </div>
      </div>

      {/* Đường phân cách */}
      <div style={{ width: '1px', height: '24px', backgroundColor: '#e2e8f0' }} />

      {/* Nút Đăng Xuất */}
      <button
        onClick={handleLogout}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          backgroundColor: '#fff1f2',
          color: '#e11d48',
          border: '1px solid #fecdd3',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
        title="Đăng xuất khỏi hệ thống"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        <span>Đăng xuất</span>
      </button>
    </div>
  );
}

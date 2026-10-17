import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRouter from './router/AppRouter';

/**
 * Root Application Component
 * Khởi tạo BrowserRouter và nạp hệ thống định tuyến đa Layout
 */
export default function App() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}

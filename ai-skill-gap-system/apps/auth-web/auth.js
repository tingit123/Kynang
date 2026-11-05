/**
 * auth.js – Logic xác thực Đăng nhập & Đăng ký cho SkillGap AI
 * Kết nối FastAPI Core API qua credentials: 'include'
 */

document.addEventListener('DOMContentLoaded', () => {
  const config = window.APP_CONFIG || {
    API_BASE: 'http://localhost:8000',
    DASHBOARD_URL: 'http://localhost:8080'
  };

  // Các phần tử DOM chính
  const loginView = document.getElementById('login-view');
  const registerView = document.getElementById('register-view');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const toSignupBtn = document.getElementById('signup');
  const toLoginBtn = document.getElementById('to-login');
  const statusEl = document.getElementById('status');
  const loginSubmitBtn = document.getElementById('login-submit-btn');
  const registerSubmitBtn = document.getElementById('register-submit-btn');

  // Role selector chips
  const roleChips = document.querySelectorAll('.role-chip');
  const roleGroups = {
    worker: document.getElementById('fields-worker'),
    employer: document.getElementById('fields-employer'),
    course_provider: document.getElementById('fields-provider')
  };
  let selectedRole = 'worker';

  // Hiển thị thông báo
  function showStatus(message, type = '') {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.className = 'status';
    if (type) {
      statusEl.classList.add(type);
    }
  }

  function clearStatus() {
    if (!statusEl) return;
    statusEl.textContent = '';
    statusEl.className = 'status';
  }

  // Chuyển đổi View Đăng nhập <-> Đăng ký
  function switchView(target) {
    clearStatus();
    if (target === 'register') {
      loginView.setAttribute('hidden', '');
      registerView.removeAttribute('hidden');
    } else {
      registerView.setAttribute('hidden', '');
      loginView.removeAttribute('hidden');
    }
  }

  if (toSignupBtn) {
    toSignupBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('register');
    });
  }

  if (toLoginBtn) {
    toLoginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('login');
    });
  }

  // Chọn chức vụ
  roleChips.forEach(chip => {
    chip.addEventListener('click', () => {
      roleChips.forEach(c => {
        c.classList.remove('active');
        c.setAttribute('aria-checked', 'false');
      });
      chip.classList.add('active');
      chip.setAttribute('aria-checked', 'true');
      selectedRole = chip.dataset.role;

      // Ẩn/hiện trường tương ứng
      Object.entries(roleGroups).forEach(([role, group]) => {
        if (!group) return;
        if (role === selectedRole) {
          group.removeAttribute('hidden');
        } else {
          group.setAttribute('hidden', '');
        }
      });
    });
  });

  // Hiện/ẩn mật khẩu ở form Đăng ký (không làm ảnh hưởng đèn pin form Đăng nhập)
  document.querySelectorAll('.toggle-reg-pwd').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      btn.setAttribute('aria-label', isPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
      btn.setAttribute('aria-pressed', isPassword ? 'true' : 'false');
    });
  });

  // ── MỞ VIEW THEO THAM SỐ URL (?view=register hoặc ?view=login) ──
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const initialView = urlParams.get('view') || (window.location.hash === '#register' ? 'register' : 'login');
    if (initialView === 'register') {
      switchView('register');
      const initialRole = urlParams.get('role');
      if (initialRole) {
        const chipKey = (initialRole === 'course_provider' || initialRole === 'provider') ? 'provider' : initialRole;
        const targetChip = document.getElementById(`chip-${chipKey}`);
        if (targetChip) targetChip.click();
      }
    } else {
      switchView('login');
    }
  } catch(e) {}

  // Kiểm tra độ mạnh mật khẩu (tối thiểu 8 ký tự, có cả chữ và số)
  function isPasswordValid(password) {
    if (password.length < 8) return false;
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    return hasLetter && hasNumber;
  }

  // Kiểm tra email
  function isEmailValid(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // ── XỬ LÝ SUBMIT ĐĂNG NHẬP ──
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearStatus();

      const emailInput = document.getElementById('email');
      const passwordInput = document.getElementById('password');
      const email = emailInput ? emailInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value : '';

      if (!email || !password) {
        showStatus('Vui lòng nhập đầy đủ Email và Mật khẩu.', 'error');
        return;
      }

      if (loginSubmitBtn) loginSubmitBtn.disabled = true;
      showStatus('Đang đăng nhập, vui lòng chờ...');

      try {
        const response = await fetch(`${config.API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ email, password })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
          showStatus('Đăng nhập thành công! Đang chuyển hướng...', 'success');
          try {
            if (window.parent && window.parent !== window) {
              window.parent.postMessage({
                type: 'SKILLGAP_AUTH_SUCCESS',
                action: 'login',
                data: data
              }, '*');
              return;
            }
          } catch(e) {}
          setTimeout(() => {
            const roleRoute = data.role === 'admin' ? '/admin/dashboard' :
              (data.role === 'employer' ? '/employer/dashboard' :
              (data.role === 'course_provider' || data.role === 'provider' ? '/provider/gap-analytics' :
              '/'));
            window.location.href = `${config.DASHBOARD_URL}/#${roleRoute}`;
          }, 600);
        } else {
          const detail = data.detail || 'Email hoặc mật khẩu không đúng';
          showStatus(typeof detail === 'string' ? detail : JSON.stringify(detail), 'error');
        }
      } catch (err) {
        console.error('Lỗi kết nối login:', err);
        showStatus('Không thể kết nối đến máy chủ. Vui lòng thử lại sau.', 'error');
      } finally {
        if (loginSubmitBtn) loginSubmitBtn.disabled = false;
      }
    });
  }

  // ── XỬ LÝ SUBMIT ĐĂNG KÝ ──
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearStatus();

      const email = (document.getElementById('reg-email')?.value || '').trim();
      const password = document.getElementById('reg-password')?.value || '';
      const passwordConfirm = document.getElementById('reg-password-confirm')?.value || '';

      // Kiểm tra email
      if (!email || !isEmailValid(email)) {
        showStatus('Vui lòng nhập định dạng email hợp lệ.', 'error');
        return;
      }

      // Kiểm tra mật khẩu
      if (!isPasswordValid(password)) {
        showStatus('Mật khẩu phải có tối thiểu 8 ký tự, bao gồm cả chữ và số.', 'error');
        return;
      }

      if (password !== passwordConfirm) {
        showStatus('Mật khẩu nhập lại không khớp.', 'error');
        return;
      }

      // Payload dữ liệu
      const payload = {
        role: selectedRole,
        email: email,
        password: password
      };

      // Kiểm tra và bổ sung theo từng chức vụ
      if (selectedRole === 'worker') {
        const fullName = (document.getElementById('reg-worker-name')?.value || '').trim();
        if (!fullName) {
          showStatus('Vui lòng nhập họ và tên.', 'error');
          return;
        }
        payload.full_name = fullName;
      } else if (selectedRole === 'employer') {
        const companyName = (document.getElementById('reg-company-name')?.value || '').trim();
        const contactName = (document.getElementById('reg-contact-name')?.value || '').trim();
        const phone = (document.getElementById('reg-phone')?.value || '').trim();

        if (!companyName || !contactName || !phone) {
          showStatus('Vui lòng nhập đầy đủ tên công ty, người liên hệ và số điện thoại.', 'error');
          return;
        }
        payload.company_name = companyName;
        payload.contact_name = contactName;
        payload.phone = phone;
      } else if (selectedRole === 'course_provider') {
        const providerName = (document.getElementById('reg-provider-name')?.value || '').trim();
        const website = (document.getElementById('reg-website')?.value || '').trim();
        const description = (document.getElementById('reg-description')?.value || '').trim();

        if (!providerName) {
          showStatus('Vui lòng nhập tên đơn vị đào tạo.', 'error');
          return;
        }
        payload.provider_name = providerName;
        if (website) payload.website = website;
        if (description) payload.description = description;
      }

      if (registerSubmitBtn) registerSubmitBtn.disabled = true;
      showStatus('Đang tạo tài khoản, vui lòng chờ...');

      try {
        const response = await fetch(`${config.API_BASE}/api/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
          let successNotice = 'Đăng ký tài khoản thành công! Đang tự động đăng nhập...';
          if (selectedRole === 'employer' || selectedRole === 'course_provider') {
            successNotice = 'Đăng ký thành công! Tài khoản đang chờ quản trị viên duyệt.';
          }
          showStatus(successNotice, 'success');

          // Tự động đăng nhập
          try {
            const loginRes = await fetch(`${config.API_BASE}/api/auth/login`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({ email, password })
            });
            if (loginRes.ok) {
              const loginData = await loginRes.json().catch(() => ({}));
              try {
                if (window.parent && window.parent !== window) {
                  window.parent.postMessage({
                    type: 'SKILLGAP_AUTH_SUCCESS',
                    action: 'register',
                    data: loginData
                  }, '*');
                  return;
                }
              } catch(e) {}
              setTimeout(() => {
                const roleRoute = loginData.role === 'admin' ? '/admin/dashboard' :
                  (loginData.role === 'employer' ? '/employer/dashboard' :
                  (loginData.role === 'course_provider' || loginData.role === 'provider' ? '/provider/gap-analytics' :
                  '/'));
                window.location.href = `${config.DASHBOARD_URL}/#${roleRoute}`;
              }, 800);
              return;
            }
          } catch(e) {}

          // Fallback nếu không tự đăng nhập được: chuyển sang tab login
          setTimeout(() => {
            const loginEmailInput = document.getElementById('email');
            if (loginEmailInput) loginEmailInput.value = email;
            const loginPwdInput = document.getElementById('password');
            if (loginPwdInput) loginPwdInput.value = '';
            switchView('login');
            showStatus(successNotice + ' Vui lòng đăng nhập.', 'success');
          }, 1200);
        } else {
          const detail = data.detail || 'Đăng ký không thành công. Vui lòng thử lại.';
          showStatus(typeof detail === 'string' ? detail : JSON.stringify(detail), 'error');
        }
      } catch (err) {
        console.error('Lỗi kết nối register:', err);
        showStatus('Không thể kết nối đến máy chủ. Vui lòng thử lại sau.', 'error');
      } finally {
        if (registerSubmitBtn) registerSubmitBtn.disabled = false;
      }
    });
  }
});

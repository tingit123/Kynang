// Account tools from Kynang-main, integrated with Tin roles and persistent API.
let managedAccounts = [];

function accountText(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function accountRequest(path = '', options = {}) {
  const response = await fetch(`${API_BASE}/api/users/${path}`, {
    ...options, headers: getAuthHeaders(), credentials: 'include'
  });
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Không thể lưu tài khoản. Vui lòng kiểm tra thông tin.');
  return data;
}

async function renderAdmin() {
  const body = document.getElementById('adminUsersBody');
  if (!body) return;
  if (currentUser?.role !== 'admin' || currentUser.is_guest) {
    managedAccounts = [];
    body.innerHTML = '<tr><td colspan="7">Vui lòng đăng nhập bằng tài khoản quản trị.</td></tr>';
    return;
  }
  body.innerHTML = '<tr><td colspan="7">Đang tải tài khoản...</td></tr>';
  try {
    // Fetch every page so search, filters, and counters cover the whole directory.
    const accounts = [];
    let page;
    do {
      page = await accountRequest(`?limit=1000&offset=${accounts.length}`);
      accounts.push(...page);
    } while (page.length === 1000);
    managedAccounts = accounts;
    filterAdminUsers();
    for (const role of ['candidate', 'employer', 'provider']) {
      document.getElementById(`accountCount-${role}`).textContent = accounts.filter(u => u.role === role).length;
    }
  } catch (error) {
    managedAccounts = [];
    body.innerHTML = `<tr><td colspan="7">${accountText(error.message)}</td></tr>`;
  }
}

function filterAdminUsers() {
  const query = document.getElementById('adminUserSearch').value.toLowerCase().trim();
  const role = document.getElementById('adminRoleFilter').value;
  const status = document.getElementById('adminStatusFilter').value;
  const labels = {admin:'Quản trị viên', candidate:'Người lao động', employer:'Nhà tuyển dụng', provider:'Nhà cung cấp khóa học'};
  const accounts = managedAccounts.filter(u =>
    (!query || [u.id, u.full_name, u.email, u.company_name].some(v => String(v ?? '').toLowerCase().includes(query))) &&
    (role === 'all' || u.role === role) &&
    (status === 'all' || u.is_active === (status === 'active')));
  document.getElementById('accountCountBadge').textContent = `${accounts.length} tài khoản`;
  document.getElementById('adminUsersBody').innerHTML = accounts.map(u => `<tr>
    <td>${u.id}</td>
    <td><strong>${accountText(u.full_name)}</strong><div style="font-size:11px;color:var(--text2)">${accountText(u.email)}</div></td>
    <td><span class="chip">${labels[u.role] || accountText(u.role)}</span></td>
    <td>${accountText(u.company_name || '—')}</td>
    <td>${u.created_at ? accountText(new Date(u.created_at).toLocaleDateString('vi-VN')) : '—'}</td>
    <td>${u.is_active ? 'Hoạt động' : 'Đã khóa'}</td>
    <td><div style="display:flex;gap:4px;flex-wrap:wrap">
      <button class="action-btn" onclick="openEditUserModal(${u.id})">Sửa</button>
      <button class="action-btn" onclick="toggleUserStatus(${u.id})" ${u.id === currentUser.id ? 'disabled' : ''}>${u.is_active ? 'Khóa' : 'Mở'}</button>
      <button class="action-btn danger" onclick="deleteUser(${u.id})" ${u.id === currentUser.id ? 'disabled' : ''}>Xóa</button>
    </div></td></tr>`).join('') || '<tr><td colspan="7">Không tìm thấy tài khoản phù hợp.</td></tr>';
}

function openCreateUserModal() {
  document.getElementById('accountForm').reset();
  document.getElementById('accountEditId').value = '';
  document.getElementById('accountModalTitle').textContent = 'Thêm tài khoản mới';
  document.getElementById('accountFormPassword').required = true;
  document.getElementById('accountModal').classList.add('open');
}

function openEditUserModal(id) {
  const user = managedAccounts.find(u => u.id === id);
  if (!user) return;
  openCreateUserModal();
  document.getElementById('accountEditId').value = id;
  document.getElementById('accountModalTitle').textContent = `Chỉnh sửa tài khoản #${id}`;
  for (const [field, key] of Object.entries({Name:'full_name', Email:'email', Role:'role', Phone:'phone', Org:'company_name'})) {
    document.getElementById(`accountForm${field}`).value = user[key] || '';
  }
  document.getElementById('accountFormStatus').value = user.is_active ? 'active' : 'inactive';
  document.getElementById('accountFormPassword').required = false;
}

function closeAccountModal() {
  document.getElementById('accountModal').classList.remove('open');
}

async function handleSaveAccount(event) {
  event.preventDefault();
  const id = document.getElementById('accountEditId').value;
  const payload = {
    full_name: document.getElementById('accountFormName').value.trim(),
    email: document.getElementById('accountFormEmail').value.trim(),
    phone: document.getElementById('accountFormPhone').value.trim(),
    company_name: document.getElementById('accountFormOrg').value.trim(),
    role: document.getElementById('accountFormRole').value,
    is_active: document.getElementById('accountFormStatus').value === 'active'
  };
  const password = document.getElementById('accountFormPassword').value;
  if (password) payload.password = password;
  const button = document.getElementById('btnSaveAccount');
  button.disabled = true;
  try {
    const saved = await accountRequest(id, {method:id ? 'PUT' : 'POST', body:JSON.stringify(payload)});
    if (saved.id === currentUser.id) {
      currentUser = {...currentUser, ...saved};
      localStorage.setItem('current_user', JSON.stringify(currentUser));
      updateUserUI();
    }
    closeAccountModal();
    await renderAdmin();
    showToast('Đã lưu tài khoản.');
  } catch (error) { showToast(error.message, 'error'); }
  finally { button.disabled = false; }
}

async function toggleUserStatus(id) {
  const user = managedAccounts.find(u => u.id === id);
  if (!user) return;
  try {
    await accountRequest(id, {method:'PUT', body:JSON.stringify({is_active:!user.is_active})});
    await renderAdmin();
    showToast(user.is_active ? 'Đã khóa tài khoản.' : 'Đã mở tài khoản.');
  } catch (error) { showToast(error.message, 'error'); }
}

async function deleteUser(id) {
  const user = managedAccounts.find(u => u.id === id);
  if (!user || !confirm(`Xóa tài khoản ${user.full_name} (${user.email})?`)) return;
  try {
    await accountRequest(id, {method:'DELETE'});
    await renderAdmin();
    showToast('Đã xóa tài khoản.');
  } catch (error) { showToast(error.message, 'error'); }
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
  toast.textContent = message;
  toast.style.cssText = `position:fixed;bottom:24px;right:24px;z-index:100000;max-width:90vw;padding:14px 20px;border-radius:10px;color:white;background:${type === 'error' ? '#b91c1c' : '#087f78'};box-shadow:0 4px 20px #0003`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}

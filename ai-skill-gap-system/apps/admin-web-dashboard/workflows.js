// Persistent profile/course forms and navigable detail views.
const flowEscape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const flowSafeUrl = value => { try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch { return ''; } };
let flowSkills = [];
let profileRatings = [];
let flowModalTrigger = null;
let directoryMode = 'loading';
let detailRequestVersion = 0;
const visibleJobs = new Map();

async function flowRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}/api/${path}`, {...options, headers:getAuthHeaders(), credentials:'include'});
  const data = await response.json();
  if (!response.ok) {
    const message = typeof data.detail === 'string' ? data.detail : (data.detail || []).map(e => e.msg).join('; ');
    throw new Error(message || 'Không thể hoàn tất thao tác. Vui lòng thử lại.');
  }
  return data;
}

function flowAllowed(roles) {
  if (!localStorage.getItem('access_token') && !localStorage.getItem('token')) {
    openAuthModal('login');
    showToast('Vui lòng đăng nhập để lưu dữ liệu vào hệ thống.', 'error');
    return false;
  }
  if (currentUser.is_guest || !roles.includes(currentUser.role)) {
    showToast('Vui lòng đăng nhập bằng tài khoản có quyền thực hiện thao tác này.', 'error');
    return false;
  }
  return true;
}

function flowModal(title, subtitle, content) {
  flowModalTrigger = document.activeElement;
  const overlay = document.getElementById('workflowModal');
  overlay.innerHTML = `<div class="workflow-modal"><div class="workflow-modal-header"><div><h2 id="workflowTitle">${flowEscape(title)}</h2><p>${flowEscape(subtitle)}</p></div><button class="workflow-close" type="button" aria-label="Đóng biểu mẫu" onclick="closeWorkflowModal()">×</button></div>${content}</div>`;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
  overlay.querySelector('input, select, button')?.focus();
}

function closeWorkflowModal() {
  document.getElementById('workflowModal').classList.remove('open');
  document.body.style.overflow = '';
  flowModalTrigger?.focus();
}

function flowError(error) {
  const box = document.getElementById('workflowError');
  if (box) { box.textContent = error.message; box.scrollIntoView({block:'nearest'}); }
}

async function loadFlowSkills() {
  flowSkills = await flowRequest('skills/?limit=500');
  return flowSkills.map(s => `<option value="${s.id}">${flowEscape(s.skill_name)} · ${flowEscape(s.industry || 'Chung')}</option>`).join('');
}

async function openProfileCreate() {
  if (!flowAllowed(['admin'])) return;
  flowModal('Thêm hồ sơ người lao động', 'Lưu hồ sơ và mức tự đánh giá kỹ năng vào hệ thống.', '<p role="status">Đang tải danh mục kỹ năng...</p>');
  try {
    const options = await loadFlowSkills();
    if (!document.getElementById('workflowModal').classList.contains('open')) return;
    profileRatings = [];
    flowModal('Thêm hồ sơ người lao động', 'Các trường có dấu * là bắt buộc. Mã hồ sơ có thể được tạo tự động.', `
      <form class="workflow-form" onsubmit="submitWorkerProfile(event)">
        <div class="workflow-row"><label>Họ và tên *<input id="newWorkerName" required maxlength="100" autocomplete="name"></label><label>Mã hồ sơ<input id="newWorkerCode" maxlength="20" pattern="[A-Za-z0-9_-]+" placeholder="Để trống để tạo tự động"></label></div>
        <div class="workflow-row"><label>Chuyên ngành<input id="newWorkerMajor" maxlength="100" placeholder="Ví dụ: Công nghệ thông tin"></label><label>Trường / cơ sở đào tạo<input id="newWorkerSchool" maxlength="200"></label></div>
        <div class="workflow-row"><label>Năm học<select id="newWorkerYear"><option value="">Chưa cập nhật</option>${[1,2,3,4,5,6].map(y => `<option value="${y}">Năm ${y}</option>`).join('')}</select></label><label>Ngày đánh giá<input type="date" id="newWorkerDate"></label></div>
        <fieldset style="border:0;min-width:0"><legend style="font-size:14px;font-weight:700;margin-bottom:10px">Kỹ năng & mức tự đánh giá</legend><p class="workflow-muted" style="margin-bottom:10px">Thang điểm 0–100. Có thể bổ sung hồ sơ trước khi đánh giá kỹ năng.</p>
          <div class="rating-editor"><label>Kỹ năng<select id="profileSkillSelect">${options}</select></label><label>Điểm<input type="number" min="0" max="100" step="1" id="profileSkillRating" value="65"></label><button type="button" class="workflow-close" aria-label="Thêm kỹ năng" onclick="addProfileRating()">+</button></div>
          <div class="skill-rating-list" id="profileRatings" style="margin-top:12px"></div>
        </fieldset>
        <div id="workflowError" class="workflow-error" role="alert"></div>
        <div class="workflow-actions"><button type="button" class="btn btn-outline" onclick="closeWorkflowModal()">Hủy</button><button type="submit" id="workflowSave" class="btn btn-primary">Lưu hồ sơ</button></div>
      </form>`);
  } catch (error) {
    document.querySelector('#workflowModal .workflow-modal').innerHTML = `<h2>Chưa thể tải biểu mẫu</h2><p class="workflow-error">${flowEscape(error.message)}</p><button class="btn" onclick="closeWorkflowModal()">Đóng</button>`;
  }
}

function addProfileRating() {
  const id = Number(document.getElementById('profileSkillSelect').value);
  const raw = document.getElementById('profileSkillRating').value;
  const rating = Number(raw);
  if (!flowSkills.some(s => s.id === id) || raw === '' || !Number.isInteger(rating) || rating < 0 || rating > 100) {
    flowError(new Error('Chọn kỹ năng và nhập điểm nguyên từ 0 đến 100.')); return;
  }
  const existing = profileRatings.find(s => s.skill_id === id);
  if (existing) existing.self_rating = rating;
  else profileRatings.push({skill_id:id, self_rating:rating});
  renderProfileRatings();
}

function removeProfileRating(id) {
  profileRatings = profileRatings.filter(s => s.skill_id !== id);
  renderProfileRatings();
}

function renderProfileRatings() {
  document.getElementById('profileRatings').innerHTML = profileRatings.map(r => `<div class="skill-rating-item"><span>${flowEscape(flowSkills.find(s => s.id === r.skill_id)?.skill_name)} <strong>${r.self_rating}/100</strong></span><button type="button" class="action-btn" onclick="removeProfileRating(${r.skill_id})" aria-label="Bỏ kỹ năng ${flowEscape(flowSkills.find(s => s.id === r.skill_id)?.skill_name)}">Bỏ</button></div>`).join('');
  document.getElementById('workflowError').textContent = '';
}

async function submitWorkerProfile(event) {
  event.preventDefault();
  const button = document.getElementById('workflowSave'); button.disabled = true; button.textContent = 'Đang lưu...';
  const value = id => document.getElementById(id).value.trim();
  const payload = {full_name:value('newWorkerName'), student_code:value('newWorkerCode') || null, major:value('newWorkerMajor') || null, institution:value('newWorkerSchool') || null, year_of_study:Number(value('newWorkerYear')) || null, completed_at:value('newWorkerDate') || null, skills:profileRatings};
  try {
    const saved = await flowRequest('surveys/', {method:'POST', body:JSON.stringify(payload)});
    closeWorkflowModal(); workerPage = 1; workerSearchQuery = '';
    document.getElementById('workerSearchInput').value = '';
    await loadWorkerDirectory();
    showToast(`Đã lưu hồ sơ ${saved.full_name}.`);
  } catch (error) { flowError(error); }
  finally { button.disabled = false; button.textContent = 'Lưu hồ sơ'; }
}

async function loadWorkerDirectory() {
  const body = document.getElementById('workersTableBody');
  body.innerHTML = '<tr><td colspan="8" role="status">Đang tải hồ sơ...</td></tr>';
  try {
    const surveys = [];
    let page;
    do { page = await flowRequest(`surveys/?limit=500&offset=${surveys.length}`); surveys.push(...page); } while (page.length === 500);
    RAW_WORKERS = surveys.map(s => ({id:s.student_code, dbId:s.id, name:s.full_name, major:s.major || 'Chưa cập nhật', school:s.institution || 'Chưa cập nhật', skills:s.skills || [], match:s.recommended_role || 'Chưa đánh giá', status:s.skills?.length ? 'active' : 'pending'}));
    directoryMode = 'live'; renderWorkerDirectory();
    const quick = document.getElementById('recStudentQuick');
    if (quick) {
      quick.innerHTML = '<option value="">— Chọn hồ sơ đã lưu —</option>';
      for (const w of RAW_WORKERS) quick.add(new Option(`${w.id} - ${w.name}`, w.id));
    }
  } catch (error) {
    directoryMode = 'error';
    body.innerHTML = `<tr><td colspan="8"><p class="workflow-error">${flowEscape(error.message)}</p><button class="action-btn" onclick="loadWorkerDirectory()">Thử lại</button></td></tr>`;
  }
}

function renderWorkerDirectory() {
  if (directoryMode !== 'live') { loadWorkerDirectory(); return; }
  const query = (workerSearchQuery || '').toLowerCase();
  const list = RAW_WORKERS.filter(w => [w.id,w.name,w.major,w.school].some(v => String(v || '').toLowerCase().includes(query)));
  const size = 10, pages = Math.max(1,Math.ceil(list.length / size));
  workerPage = Math.max(1,Math.min(workerPage,pages));
  const start = (workerPage - 1) * size;
  const body = document.getElementById('workersTableBody');
  body.innerHTML = list.slice(start,start+size).map(w => `<tr><td>${flowEscape(w.id)}</td><td class="skill-name-cell">${flowEscape(w.name)}</td><td>${flowEscape(w.major)}</td><td>${flowEscape(w.school)}</td><td><div class="detail-tags">${w.skills.map(s => `<span>${flowEscape(s)}</span>`).join('') || '<span>Chưa đánh giá</span>'}</div></td><td>${flowEscape(w.match)}</td><td>${w.skills.length ? 'Có đánh giá kỹ năng' : 'Chưa đánh giá'}</td><td><button class="action-btn" data-worker-detail="${flowEscape(w.id)}">Chi tiết</button></td></tr>`).join('') || '<tr><td colspan="8" style="text-align:center;padding:36px">Chưa có hồ sơ phù hợp. Bấm “Thêm hồ sơ” để tạo hồ sơ đầu tiên.</td></tr>';
  const stats = document.querySelectorAll('#page-workers .admin-stat-val');
  if (stats.length === 3) { stats[0].textContent = RAW_WORKERS.length; stats[1].textContent = RAW_WORKERS.filter(w => w.skills.length).length; stats[2].textContent = RAW_WORKERS.filter(w => !w.skills.length).length; }
  document.getElementById('workersPagination').innerHTML = `<div>${list.length ? start+1 : 0}–${Math.min(start+size,list.length)} / ${list.length} hồ sơ</div><div style="display:flex;align-items:center;gap:10px"><button class="action-btn" ${workerPage<=1?'disabled':''} onclick="workerPage--;renderWorkerDirectory()">← Trước</button><span>${workerPage} / ${pages}</span><button class="action-btn" ${workerPage>=pages?'disabled':''} onclick="workerPage++;renderWorkerDirectory()">Sau →</button></div>`;
}

async function openCourseCreate() {
  if (!flowAllowed(['admin','provider'])) return;
  flowModal('Đăng khóa học mới', 'Liên kết khóa học với kỹ năng để người học tìm được chương trình phù hợp.', '<p role="status">Đang tải danh mục kỹ năng...</p>');
  try {
    const options = await loadFlowSkills();
    if (!document.getElementById('workflowModal').classList.contains('open')) return;
    flowModal('Đăng khóa học mới', currentUser.role === 'provider' ? 'Khóa học được lưu với trạng thái chờ duyệt.' : 'Khóa học do quản trị viên đăng được duyệt ngay.', `
      <form class="workflow-form" onsubmit="submitNewCourse(event)">
        <label>Tên khóa học *<input id="newCourseName" required maxlength="300" placeholder="Ví dụ: Python thực hành cho người mới"></label>
        <label>Kỹ năng bù đắp *<select id="newCourseSkill" required><option value="">— Chọn kỹ năng —</option>${options}</select></label>
        <label>Đơn vị đào tạo / nền tảng *<input id="newCoursePlatform" required maxlength="100" placeholder="Tên trung tâm hoặc nền tảng học"></label>
        <label>Liên kết khóa học *<input id="newCourseUrl" type="url" required maxlength="500" placeholder="https://..."></label>
        <p class="workflow-muted">Sử dụng liên kết http hoặc https đến trang giới thiệu / đăng ký khóa học.</p>
        <div id="workflowError" class="workflow-error" role="alert"></div><div class="workflow-actions"><button type="button" class="btn btn-outline" onclick="closeWorkflowModal()">Hủy</button><button class="btn btn-primary" id="workflowSave" type="submit">Đăng khóa học</button></div>
      </form>`);
  } catch (error) {
    document.querySelector('#workflowModal .workflow-modal').innerHTML = `<h2>Chưa thể tải biểu mẫu</h2><p class="workflow-error">${flowEscape(error.message)}</p><button class="btn" onclick="closeWorkflowModal()">Đóng</button>`;
  }
}

async function submitNewCourse(event) {
  event.preventDefault();
  const button = document.getElementById('workflowSave'); button.disabled = true; button.textContent = 'Đang đăng...';
  try {
    const url = flowSafeUrl(document.getElementById('newCourseUrl').value.trim());
    if (!url) throw new Error('Liên kết phải bắt đầu bằng http:// hoặc https://.');
    const saved = await flowRequest('courses/', {method:'POST', body:JSON.stringify({course_name:document.getElementById('newCourseName').value.trim(), skill_id:Number(document.getElementById('newCourseSkill').value), platform:document.getElementById('newCoursePlatform').value.trim(), url})});
    closeWorkflowModal(); resetCourseFilters();
    await loadSavedCourses();
    showToast(saved.status === 'approved' ? 'Đã đăng khóa học thành công.' : 'Đã lưu khóa học, đang chờ duyệt.');
  } catch (error) { flowError(error); }
  finally { button.disabled = false; button.textContent = 'Đăng khóa học'; }
}

async function loadSavedCourses() {
  try {
    const courses = await flowRequest('courses/');
    for (let i = COURSES_DATA.length-1; i>=0; i--) if (COURSES_DATA[i].dbId) COURSES_DATA.splice(i,1);
    COURSES_DATA.unshift(...courses.map(c => ({dbId:c.id,title:c.course_name,skill:c.skill_name,industry:c.industry,provider:c.platform,platform:c.platform,url:flowSafeUrl(c.url),duration:'Chưa cập nhật',price:'Xem tại trang khóa học',status:c.status})));
    coursesSkillDropdownPopulated = false;
    renderCourses();
  } catch (error) { showToast(`Chưa tải được khóa học đã lưu: ${error.message}`, 'error'); }
}

function openJobDetail(id) {
  const prefix = ['admin','employer'].includes(currentUser.role) ? `/${currentUser.role}/jobs` : '/jobs';
  navigate(`${prefix}/${encodeURIComponent(id)}`);
}

function renderDetailRoute(path) {
  const job = path.match(/^\/(?:(admin|employer)\/)?jobs\/([^/]+)\/?$/);
  const worker = path.match(/^\/admin\/workers\/([^/]+)\/?$/);
  if (!job && !worker) return false;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-record-detail').classList.add('active');
  const container = document.getElementById('recordDetailContent');
  container.innerHTML = '<div class="detail-panel" role="status">Đang tải thông tin chi tiết...</div>';
  const breadcrumb = document.getElementById('breadcrumbText');
  if (breadcrumb) breadcrumb.textContent = worker ? 'Chi tiết người lao động' : 'Chi tiết nhà tuyển dụng';
  const version = ++detailRequestVersion;
  const back = worker ? '/admin/workers' : job[1] ? `/${job[1]}/jobs` : '/jobs';
  loadRecordDetail(worker ? 'worker' : 'job', decodeURIComponent((worker || job)[worker ? 1 : 2]), back, version);
  return true;
}

function detailBack(path, label) {
  return `<a class="detail-back" href="${flowEscape(path)}" data-detail-back>← ${label}</a>`;
}

async function loadRecordDetail(type, id, back, version) {
  const container = document.getElementById('recordDetailContent');
  try {
    let data, demo = false;
    if (type === 'worker') data = await flowRequest(`surveys/${encodeURIComponent(id)}`);
    else {
      const job = visibleJobs.get(id) || RAW_JOBS.find(j => String(j.dbId || j.id) === id);
      if (/^\d+$/.test(id)) data = await flowRequest(`jobs/${id}`);
      else if (job) { data = {title:job.title,company:job.company,location:job.location,industry:job.industry,skills:job.skills,salary_label:job.salary}; demo = true; }
      else throw new Error('Không tìm thấy tin tuyển dụng.');
    }
    if (version !== detailRequestVersion) return;
    const e = flowEscape;
    if (type === 'worker') {
      const skills = data.skills || [];
      container.innerHTML = `${detailBack(back,'Danh sách người lao động')}<header class="detail-hero"><div class="detail-avatar">${e(data.full_name?.trim().split(/\s+/).map(s=>s[0]).slice(-2).join(''))}</div><div><div class="detail-eyebrow">Hồ sơ người lao động</div><h1>${e(data.full_name)}</h1><p class="workflow-muted">${e(data.student_code)} · ${e(data.major || 'Chưa cập nhật chuyên ngành')}</p></div></header>
        <div class="detail-columns"><section class="detail-panel"><h2>Kỹ năng & mức tự đánh giá</h2><p class="workflow-muted" style="margin-bottom:20px">Thang điểm 0–100; từ 65 điểm được đánh giá đạt mức thành thạo.</p>${skills.map(s=>`<div class="detail-rating"><span>${e(s.skill_name)}</span><progress value="${Number(s.rating)}" max="100" aria-label="${e(s.skill_name)}: ${Number(s.rating)} trên 100"></progress><strong>${Number(s.rating)}/100</strong></div>`).join('') || '<p class="workflow-muted">Hồ sơ chưa có đánh giá kỹ năng.</p>'}</section>
        <aside class="detail-panel"><h2>Thông tin hồ sơ</h2><dl class="detail-facts"><div><dt>Mã hồ sơ</dt><dd>${e(data.student_code)}</dd></div><div><dt>Chuyên ngành</dt><dd>${e(data.major || 'Chưa cập nhật')}</dd></div><div><dt>Trường / cơ sở đào tạo</dt><dd>${e(data.institution || 'Chưa cập nhật')}</dd></div><div><dt>Năm học</dt><dd>${data.year_of_study ? `Năm ${e(data.year_of_study)}` : 'Chưa cập nhật'}</dd></div><div><dt>Ngày đánh giá</dt><dd>${data.completed_at ? e(new Date(data.completed_at+'T00:00:00').toLocaleDateString('vi-VN')) : 'Chưa cập nhật'}</dd></div></dl></aside></div>`;
    } else {
      const salary = data.salary_label || (data.salary_min && data.salary_max ? `${(data.salary_min/1e6).toLocaleString('vi-VN')}–${(data.salary_max/1e6).toLocaleString('vi-VN')} triệu / tháng` : data.salary_min ? `Từ ${(data.salary_min/1e6).toLocaleString('vi-VN')} triệu / tháng` : 'Thỏa thuận');
      const source = flowSafeUrl(data.source_url);
      container.innerHTML = `${detailBack(back,'Danh sách nhà tuyển dụng')}${demo ? '<div class="detail-notice">Dữ liệu minh họa — tin này chưa có trong database.</div>' : ''}<header class="detail-hero"><div class="detail-avatar">${e((data.company || 'CT').slice(0,2).toUpperCase())}</div><div><div class="detail-eyebrow">Nhà tuyển dụng · Thông tin tuyển dụng</div><h1>${e(data.company)}</h1><p class="workflow-muted">${e(data.location || 'Chưa cập nhật địa điểm')} · ${e(data.industry || 'Chưa cập nhật ngành')}</p></div></header>
        <div class="detail-columns"><div><section class="detail-panel"><div class="detail-eyebrow">Vị trí đang tuyển</div><h2 style="font-size:23px">${e(data.title)}</h2><div class="detail-tags"><span>${e(salary)}</span><span>${e(data.location || 'Chưa cập nhật')}</span></div></section><section class="detail-panel"><h2>Mô tả công việc & yêu cầu</h2><div class="detail-prose">${e(data.description || 'Nhà tuyển dụng chưa cung cấp mô tả chi tiết cho tin này.')}</div></section><section class="detail-panel"><h2>Kỹ năng yêu cầu</h2><div class="detail-tags">${(data.skills || []).map(s=>`<span>${e(s)}</span>`).join('') || '<p class="workflow-muted">Chưa cập nhật danh sách kỹ năng.</p>'}</div></section></div>
        <aside><section class="detail-panel"><h2>Thông tin tuyển dụng</h2><dl class="detail-facts"><div><dt>Nhà tuyển dụng</dt><dd>${e(data.company)}</dd></div><div><dt>Ngành nghề</dt><dd>${e(data.industry || 'Chưa cập nhật')}</dd></div><div><dt>Mức lương</dt><dd>${e(salary)}</dd></div><div><dt>Ngày đăng</dt><dd>${data.posted_date ? e(new Date(data.posted_date+'T00:00:00').toLocaleDateString('vi-VN')) : 'Chưa cập nhật'}</dd></div><div><dt>Nguồn tin</dt><dd>${e(data.source_platform || 'Hệ thống SkillGap')}</dd></div></dl>${source ? `<a class="btn btn-primary" style="margin-top:22px;text-decoration:none;justify-content:center" href="${e(source)}" target="_blank" rel="noopener noreferrer">Xem tin tuyển dụng gốc ↗</a>` : '<p class="workflow-muted" style="margin-top:20px">Chưa có liên kết tuyển dụng bên ngoài.</p>'}</section></aside></div>`;
    }
    window.scrollTo({top:0,behavior:'instant'});
    container.querySelector('h1')?.setAttribute('tabindex','-1');
    container.querySelector('h1')?.focus({preventScroll:true});
  } catch (error) {
    if (version !== detailRequestVersion) return;
    container.innerHTML = `${detailBack(back,'Quay lại danh sách')}<section class="detail-panel"><h1>Chưa thể hiển thị chi tiết</h1><p class="workflow-error">${flowEscape(error.message)}</p><p class="workflow-muted">Hồ sơ có thể đã bị xóa hoặc kết nối máy chủ đang gián đoạn.</p></section>`;
  }
}

document.addEventListener('click', event => {
  if (event.target.closest('#sidebar .nav-item')) document.body.classList.remove('mobile-nav-open');
  const worker = event.target.closest('[data-worker-detail]');
  if (worker) navigate(`/admin/workers/${encodeURIComponent(worker.dataset.workerDetail)}`);
  const back = event.target.closest('[data-detail-back]');
  if (back && !event.ctrlKey && !event.metaKey) { event.preventDefault(); navigate(back.getAttribute('href')); }
  if (event.target.id === 'workflowModal') closeWorkflowModal();
});

document.addEventListener('keydown', event => {
  const overlay = document.getElementById('workflowModal');
  if (!overlay?.classList.contains('open')) return;
  if (event.key === 'Escape') { closeWorkflowModal(); return; }
  if (event.key !== 'Tab') return;
  const controls = [...overlay.querySelectorAll('button:not([disabled]),input,select,textarea,a[href]')].filter(el => el.offsetParent !== null);
  const first = controls[0], last = controls[controls.length-1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});

window.addEventListener('DOMContentLoaded', () => {
  loadSavedCourses();
});

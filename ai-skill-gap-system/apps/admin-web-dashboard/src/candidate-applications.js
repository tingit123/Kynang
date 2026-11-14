/* Real application submission. CV extraction stays local to the backend. */
(function () {
  const api = `http://${location.hostname || 'localhost'}:8000/api`;
  let generation = 0, submitting = false, previewUrl = null;
  const state = {jobs: null, applications: null};
  function resetFile() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    const input = document.getElementById('candApplyFile');
    if (input) input.value = '';
    const selected = document.getElementById('candApplySelected');
    if (selected) selected.hidden = true;
    const error = document.getElementById('candApplyFileError');
    if (error) error.textContent = '';
    const link = document.getElementById('candApplyPreview');
    if (link) link.removeAttribute('href');
  }
  function selectFile() {
    const input = document.getElementById('candApplyFile');
    const selected = document.getElementById('candApplySelected');
    const error = document.getElementById('candApplyFileError');
    const file = input.files[0];
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    selected.hidden = !file;
    error.textContent = '';
    document.getElementById('candApplyError').textContent = '';
    const link = document.getElementById('candApplyPreview');
    link.removeAttribute('href');
    link.hidden = true;
    if (!file) return true;
    document.getElementById('candApplyFilename').textContent = file.name;
    document.getElementById('candApplyFilesize').textContent = file.size < 1024*1024 ? `${(file.size/1024).toLocaleString('vi-VN',{maximumFractionDigits:1})} KB` : `${(file.size/1024/1024).toLocaleString('vi-VN',{maximumFractionDigits:2})} MB`;
    const message = !/\.(pdf|png|jpe?g|webp|txt)$/i.test(file.name) ? 'Chỉ nhận CV PDF, PNG, JPG, WEBP hoặc TXT.' :
      file.size === 0 ? 'Tệp CV rỗng. Hãy chọn lại tệp có nội dung.' : file.size > 5*1024*1024 ? 'CV không được vượt quá 5 MB.' : '';
    document.getElementById('candApplyFileStatus').textContent = message ? 'Tệp chưa hợp lệ' : 'Đã chọn trên thiết bị · Chưa nộp hồ sơ';
    if (message) {error.textContent=message;return false;}
    const mime = ({pdf:'application/pdf',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp',txt:'text/plain'})[file.name.split('.').pop().toLowerCase()];
    previewUrl=URL.createObjectURL(new Blob([file],{type:mime}));
    link.href=previewUrl; link.hidden=false;
    return true;
  }
  addEventListener('pagehide',()=>{if(previewUrl) URL.revokeObjectURL(previewUrl);});
  function safeView(value) {
    if (typeof value === 'string') return value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    if (Array.isArray(value)) return value.map(safeView);
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key,item]) => [key,safeView(item)]));
    return value;
  }
  async function request(path, options = {}) {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const config = {...options, credentials:'include', headers:{...(token ? {Authorization:`Bearer ${token}`} : {}), ...options.headers}};
    let response = await fetch(api + path, config);
    if (response.status === 401 && token) response = await fetch(api + path, {...config, credentials:'omit'});
    const data = await response.json();
    if (!response.ok) throw Error(typeof data.detail === 'string' ? data.detail : 'Không thể xử lý yêu cầu. Hãy thử lại.');
    return data;
  }
  function jobView(job) {
    return {...job, serverId:job.id, avatar:(job.company || 'D').charAt(0), avatarBg:'#0d9488',
      companyFull:job.company, industry:normalizeIndustryKey(job.industry), industryLabel:job.industry,
      salary:job.salary_min && job.salary_max ? `${job.salary_min/1000000}–${job.salary_max/1000000} triệu` : 'Thỏa thuận',
      salaryDetail:'Theo thông tin trong tin tuyển dụng', postedTime:job.posted_date || 'Mới đăng',
      jobType:'Xem mô tả công việc', requirements:job.skills || [], benefits:[],
      companyAbout:'Thông tin do nhà tuyển dụng đăng.', companyAddress:job.location,
      description:job.description || '', skills:job.skills || []};
  }
  async function load() {
    const version = ++generation;
    state.applications = null;
    try {
      const jobs = await request('/jobs/?limit=1000');
      if (version !== generation) return;
      state.jobs = jobs.filter(job => job.employer_id).map(jobView);
      const requested = Number(new URLSearchParams(location.hash.split('?')[1] || '').get('job'));
      if (state.jobs.some(job => job.id === requested)) currentSelectedJobId = requested;
      renderCandidateJobs();
      if (!isCandidateGuest()) {
        const applications = await request('/jobs/my-applications');
        if (version !== generation) return;
        state.applications = applications.map(item => ({...item, status:({applied:'Đã ứng tuyển',selected:'Đang xem xét',acknowledged:'Đã xác nhận hồ sơ',invited:'Mời phỏng vấn'})[item.status] || item.status}));
        renderCandidateJobs(); updateAppliedCountBadge(); renderAppliedJobsList();
      }
    } catch (error) {
      if (version !== generation) return;
      const list = document.getElementById('candJobsList');
      if (list) {
        const message = document.createElement('p');
        message.setAttribute('role','alert'); message.style.color='#b91c1c';
        message.textContent='Không tải được dữ liệu ứng tuyển: '+error.message;
        list.prepend(message);
      }
    }
  }
  async function submit() {
    if (submitting) return;
    const errorBox = document.getElementById('candApplyError');
    const button = document.getElementById('btnConfirmSubmitApply');
    errorBox.textContent='';
    try {
      if (isCandidateGuest()) throw Error('Hãy đăng nhập tài khoản người tìm việc.');
      const job = state.jobs?.find(item => item.id === applyingJobId);
      if (!job) throw Error('Đây là tin giao diện mẫu. Hãy chọn tin do nhà tuyển dụng đăng để ứng tuyển.');
      const file = document.getElementById('candApplyFile').files[0];
      const text = document.getElementById('candApplyNote').value.trim();
      if (!file && text.replace(/\s/g,'').length < 40) throw Error('Hãy đính kèm CV hoặc nhập nội dung CV có ít nhất 40 ký tự không tính khoảng trắng.');
      if (file && !selectFile()) return;
      submitting=true; button.disabled=true; button.textContent='Đang nộp hồ sơ…';
      document.getElementById('candApplyFile').disabled=true;
      document.getElementById('candApplyRemoveFile').disabled=true;
      if(file) document.getElementById('candApplyFileStatus').textContent='Đang tải CV và nộp hồ sơ…';
      let data;
      if (file) {
        const body = new FormData(); body.append('file',file);
        data=await request(`/jobs/${job.id}/apply-cv`,{method:'POST',body});
      } else {
        data=await request(`/jobs/${job.id}/apply`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cv_snapshot_text:text})});
      }
      closeCandidateApplyModal();
      await load();
      alert(data.extraction_status === 'unreadable' ? 'Đã nộp CV gốc. Hệ thống chưa đọc được nội dung; nhà tuyển dụng có thể mở tệp để kiểm tra.' : 'Đã nộp hồ sơ thành công. Nhà tuyển dụng có thể xem hồ sơ và CV gốc.');
    } catch (error) {
      errorBox.textContent=error.message;
      if(document.getElementById('candApplyFile').files[0]) document.getElementById('candApplyFileStatus').textContent='Chưa nộp thành công · Tệp vẫn được giữ để thử lại';
    }
    finally {
      submitting=false; button.disabled=false; button.textContent='XÁC NHẬN NỘP HỒ SƠ →';
      document.getElementById('candApplyFile').disabled=false;
      document.getElementById('candApplyRemoveFile').disabled=false;
    }
  }
  window.CandidateApplications = Object.assign(state,{load,submit,safeView,selectFile,resetFile});
})();

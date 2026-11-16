/* Shared UI for nginx and React. No build required by the current nginx page. */
(function () {
  const labels = Object.fromEntries(Object.entries(window.RecruitmentStatuses.evidence).map(([key,value])=>[key,value.label]));
  const isDemoEmail = email => /(?:@|\.)demo\.local$/i.test(email || '');
  const engines = { gemini: 'Gemini', groq: 'Groq', keyword: 'Từ khóa' };
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const api = `http://${location.hostname || 'localhost'}:8000/api`;
  let mounted;
  async function request(path, options = {}, kind='json') {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const config = { credentials: 'include', ...options, headers: { ...(options.body instanceof FormData ? {} : {'Content-Type':'application/json'}), ...(token ? {Authorization: `Bearer ${token}`} : {}), ...options.headers } };
    let response = await fetch(api + path, config);
    // A stale cookie must not prevent an otherwise valid existing Bearer session.
    if (response.status === 401 && token) response = await fetch(api + path, {...config, credentials: 'omit'});
    if (!response.ok) {
      let detail; try { detail = (await response.json()).detail; } catch (_) {}
      const error = new Error(typeof detail === 'string' ? detail : 'Không tải được dữ liệu. Thử lại.');
      error.status = response.status;
      throw error;
    }
    return kind==='blob'?response.blob():response.json();
  }
  function mount(root, preferredJob, initialMode = 'evidence') {
    if (!root) return;
    if (!mounted?.disposed && mounted?.root === root && root.querySelector('[data-evidence-shell]')) {
      mounted.reload(preferredJob || mounted.job);
      return mounted.dispose;
    }
    mounted?.dispose();
    const s = { root, jobs: [], applications: [], job: '', selected: null, run: null, active: null, loading: true,
      error: '', detailError: '', detailLoading: false, running: false, saving: false, version: 0, disposed: false,
      mode: initialMode, profileHash: null, review: null, restore: null, quickState: null, errorStatus: null, detailTab:'process',pipelineList:null,pipelineDetail:null,candidateSkills:null,originalCV: null, cvLoading: false, cvError: '', cvNotice:'',cvFull:false };
    mounted = s;
    const live = () => !s.disposed && root.isConnected;
    const button = (text, action, disabled = false) => `<button type="button" class="ev-button" data-action="${action}" ${disabled ? 'disabled' : ''}>${text}</button>`;
    function reviewCandidates() {
      if (!s.review) return s.applications;
      const byId = new Map(s.applications.map(candidate => [candidate.id, candidate]));
      return s.review.ids.map(id => byId.get(id)).filter(Boolean);
    }
    async function openReview(id, ids, profileHash = null) {
      const known = new Set(s.applications.map(candidate => candidate.id));
      if (ids.some(candidateId => !known.has(candidateId))) {
        const version = ++s.version;
        try {
          const applications = await request(`/jobs/${s.job}/applications`);
          if (!live() || version !== s.version) return;
          s.applications = applications;
        } catch (error) {
          if (live() && version === s.version) { s.error = error.message; render(); }
          return;
        }
      }
      if (!s.applications.some(candidate => candidate.id === id)) return;
      const scrollers = [];
      for (let node = root; node; node = node.parentElement) {
        if (node !== document.scrollingElement && (node.scrollTop || node.scrollLeft)) {
          scrollers.push({node, top:node.scrollTop, left:node.scrollLeft});
        }
      }
      s.review = {ids:[...ids], origin:id, x:window.scrollX, y:window.scrollY, scrollers};
      s.selected = id;
      s.profileHash = profileHash;
      if (s.mode === 'quick') s.quickState?.dispose?.();
      detail();
      root.querySelector('.ev-profile h2')?.focus({preventScroll:true});
      root.querySelector('.ev-profile')?.scrollIntoView({block:'start', behavior:'instant'});
    }
    function restoreListPosition() {
      const snapshot = s.restore;
      if (!snapshot) return;
      requestAnimationFrame(() => {
        if (!live() || s.selected || s.restore !== snapshot) return;
        s.restore = null;
        const selector = s.mode === 'quick'
          ? `[data-r-action="evidence"][data-r-id="${snapshot.origin}"]`
          : `[data-pp-person="${snapshot.origin}"]`;
        (root.querySelector(selector) || root.querySelector('#rc-min-pct, [data-pp-search]'))?.focus({preventScroll:true});
        for (const {node, top, left} of snapshot.scrollers) {
          if (node.isConnected) node.scrollTo({top, left, behavior:'instant'});
        }
        window.scrollTo({top:snapshot.y, left:snapshot.x, behavior:'instant'});
      });
    }
    function backToResults() {
      ++s.version;
      clearOriginal();
      s.restore = s.review;
      s.review = null;
      s.selected = null;
      s.run = null;
      s.profileHash = null;
      render();
    }
    function render() {
      if (!live()) return;
      const candidate = s.applications.find(a => a.id === s.selected), data = s.run;
      const navigation = candidate ? reviewCandidates() : [];
      const position = navigation.findIndex(item => item.id === s.selected);
      const rows = data?.evidence || [], row = rows.find(r => r.id === s.active);
      root.innerHTML = `<style>
        .ev-shell{font-family:inherit;color:#0f172a;max-width:1250px;margin:auto;line-height:1.6}.ev-shell h1{font-size:28px;font-weight:900}.ev-shell h2{font-size:19px;font-weight:800}.ev-shell p{margin:8px 0}
        .ev-muted{color:#64748b;font-size:13px}.ev-toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:20px 0}
        .ev-shell select,.ev-shell textarea{padding:10px;border:1px solid #cbd5e1;border-radius:10px;background:#fff;color:#0f172a;font:inherit;max-width:100%}
        .ev-profile-header{display:flex;justify-content:space-between;gap:14px;align-items:flex-start;flex-wrap:wrap}.ev-profile-identity{min-width:0;flex:1 1 220px}.ev-profile-match{--coverage-size:18px;min-width:190px;padding:12px 14px;border:1px solid #b7d9d2;border-radius:12px;background:#f4faf8}.ev-profile-match strong,.ev-profile-match small{display:block}.ev-profile-match strong{font-size:13px;margin-bottom:6px;color:#0d5f57}.ev-profile-match small{margin-top:5px}.ev-profile-skills{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}.ev-profile-skill{background:#f8fafc;color:#475569;border:1px solid #cbd5e1;border-radius:6px;padding:3px 8px;font-size:12px;overflow-wrap:anywhere;max-width:100%}.ev-profile-skill[data-supported=true]{background:#e9f8ef;color:#166534;border-color:#b4dec6}.ev-list-only .ev-app{display:flex;justify-content:space-between;align-items:center;gap:18px}.ev-open{display:none;color:#0d5f57;font-weight:700;font-size:13px;white-space:nowrap}.ev-list-only .ev-open{display:block}.ev-person{display:flex;gap:14px;align-items:center;min-width:0}.ev-person>div{min-width:0}.ev-avatar{display:grid;place-items:center;width:44px;height:44px;flex-shrink:0;border-radius:14px;background:#e6f4f1;color:#0d5f57;font-size:14px;font-weight:800}.ev-page-title{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap}.ev-kicker{text-transform:uppercase;letter-spacing:.1em;color:#0d5f57;font-size:12px;font-weight:800}.ev-hotbar{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px}.ev-cv-modal{position:fixed;inset:0;background:#0f172a99;z-index:100002;display:flex;align-items:center;justify-content:center;padding:20px}.ev-cv-modal>section{background:white;border-radius:20px;padding:24px;width:min(850px,100%);max-height:90vh;overflow:auto}.ev-cv-document{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #e2e8f0;padding:28px;line-height:1.9;font:inherit;color:#0f172a}.ev-detail-tabs{display:flex;gap:8px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #e2e8f0;padding:12px 0;margin:12px 0}.ev-detail-tabs button[aria-pressed=true]{background:#0d5f57;color:white}.ev-detail-tabs [data-action="recruit-candidate"]{margin-left:auto;background:#0d5f57;color:white}.ev-file-view{width:100%;height:65vh;display:block;border:1px solid #e2e8f0;border-radius:10px}.ev-image-view{max-width:100%;max-height:65vh;object-fit:contain;cursor:zoom-in;display:block;margin:auto}.ev-full-view{width:min(1200px,100%)!important;max-height:95vh!important}.ev-full-view .ev-file-view{height:75vh}.ev-full-view .ev-cv-document{max-height:75vh;overflow:auto}.ev-original-inline .ev-cv-document{max-height:65vh;overflow:auto}.ev-detail-nav{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:16px 0}.ev-detail-nav select{flex:1;min-width:140px}
        .ev-card{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:20px;margin-bottom:12px;overflow-wrap:anywhere}.ev-app{display:block;text-align:left;width:100%;cursor:pointer;font:inherit;color:inherit}.ev-app[aria-pressed=true]{border:2px solid #0d5f57}
        .ev-button{padding:10px 16px;border:1px solid #0d5f57;border-radius:999px;background:#f0fdfa;color:#0d5f57;font:inherit;font-weight:700;cursor:pointer}.ev-button:disabled{opacity:.5;cursor:wait}
        .ev-badge{display:inline-block;padding:3px 9px;border-radius:9px;background:#e2e8f0;font-size:12px;font-weight:700}.ev-supported{background:#dcfce7;color:#166534}.ev-needs_review,.ev-unreadable{background:#fef3c7;color:#92400e}
        .ev-warning{padding:12px;border-radius:10px;background:#fff7ed;color:#9a3412;margin:12px 0}.ev-error{color:#b91c1c}
        .ev-table{width:100%;min-width:560px;border-collapse:collapse;font-size:13px}.ev-table th,.ev-table td{text-align:left;vertical-align:top;border-bottom:1px solid #e2e8f0;padding:12px 8px}.ev-table th:first-child{width:20%;min-width:110px}.ev-table th:nth-child(2){width:27%;min-width:145px}.ev-row{cursor:pointer}.ev-row[aria-selected=true]{background:#f0fdfa}.ev-table button{color:inherit;font:inherit;text-align:left;background:none;border:0;cursor:pointer;font-weight:700}
        .ev-cv{white-space:pre-wrap;max-height:420px;overflow:auto;padding:16px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;font:inherit;font-size:13px}.ev-cv mark{background:#fde047;color:#0f172a}.ev-cv::-webkit-scrollbar{width:14px;height:14px}.ev-cv::-webkit-scrollbar-thumb{background:#94a3b8;border:3px solid #f8fafc;border-radius:8px}
        .ev-review{display:grid;gap:10px;margin:18px 0}.ev-review textarea{width:100%;min-height:80px}
        #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-main-content{min-width:0}
        @media(max-width:850px){.ev-card{padding:14px}}
        @media(max-width:650px){.ev-list-only .ev-app{align-items:flex-start;flex-direction:column;gap:10px}.ev-list-only .ev-open{align-self:flex-end}.ev-avatar{width:36px;height:36px}.ev-cv-document{padding:14px}.ev-cv-modal>section{padding:16px}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]){flex-direction:column}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-sidebar{position:relative;width:100%;height:auto}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-sidebar-header{padding:16px}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-sidebar-nav{display:flex;flex-direction:row;overflow:auto;padding:8px;gap:4px}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-nav-item{white-space:nowrap;margin:0}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-sidebar-profile{margin:8px 16px;padding:12px}
          #employerPortalLayout:has(:is(#empTabCandidates,#empTabRecruitment)[style*="display: block"]) .emp-main-content{width:100%;padding:20px 14px}
        }
      </style><div data-evidence-shell class="ev-shell"><div class="ev-page-title"><div><p class="ev-kicker">Không gian nhà tuyển dụng</p><h1>${s.mode==='quick'?'Tuyển dụng nhanh':'Danh sách ứng viên'}</h1></div><span class="ev-badge">${s.mode==='quick'?'Chọn kỹ năng · Đối chiếu · Liên hệ':'Thông tin · Dẫn chứng · CV gốc'}</span></div><p class="ev-muted">${s.mode==='quick'?'Tìm hồ sơ theo những kỹ năng bạn đang cần.':'Xem hồ sơ, cập nhật trạng thái tuyển dụng và kiểm tra lịch sử thao tác.'}</p>
      <div class="ev-hotbar"><strong>${s.mode==='quick'?'Tiêu chí tuyển dụng':'Danh sách ứng viên'}</strong><span class="ev-muted">${s.mode==='quick'?'Bộ lọc luôn mở, chỉ chạy khi bạn bấm Lọc.':s.applications.length+' hồ sơ trong tin đã chọn'}</span></div>
      <div class="ev-toolbar"><label for="ev-job">Tin tuyển dụng</label><select id="ev-job" ${s.loading || s.error ? 'disabled' : ''}>${s.jobs.map(j => `<option value="${j.id}" ${String(j.id) === s.job ? 'selected' : ''}>${esc(j.title)}</option>`).join('') || `<option>${s.loading ? 'Đang tải tin tuyển dụng…' : s.error ? 'Chưa tải được danh sách tin' : 'Chưa có tin tuyển dụng'}</option>`}</select>${button('Tải lại', 'reload')}</div>
      ${s.loading ? '<p role="status">Đang tải dữ liệu…</p>' : ''}
      ${s.error ? `<p role="alert" class="ev-error">Không tải được dữ liệu. Thử lại.</p><p class="ev-muted">${esc(s.error)}</p>` : ''}
      ${s.errorStatus === 401 ? `<div class="ev-warning">Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại để xem hồ sơ của bạn. <a class="ev-button" href="http://${location.hostname}:8081/?view=login">Đăng nhập lại</a><p class="ev-muted">Dữ liệu mẫu nằm trong tài khoản evidence.employer@demo.local.</p></div>` : ''}
      ${!s.loading && !s.error && !s.jobs.length ? '<div class="ev-card">Chưa có tin tuyển dụng.</div>' : ''}
      ${!s.loading && !s.error && s.jobs.length && s.mode === 'quick' && !candidate ? '<div id="ev-quick-panel"></div>' : ''}
      ${!s.loading && !s.error && s.jobs.length && (s.mode !== 'quick' || candidate) ? `${candidate ? `<section class="ev-card ev-profile"><div class="ev-detail-nav">${button(s.mode === 'quick' ? '← Kết quả lọc' : '← Danh sách','back-list')}<select id="ev-candidate-nav" aria-label="Chuyển ứng viên">${navigation.map(a=>`<option value="${a.id}" ${a.id===s.selected?'selected':''}>${esc(a.candidate_name)}</option>`).join('')}</select>${button('← Trước','previous-candidate',position<=0)}${button('Tiếp →','next-candidate',position<0||position>=navigation.length-1)}<span class="ev-muted" data-ev-review-position>${position+1}/${navigation.length} hồ sơ</span></div><div class="ev-profile-header"><div class="ev-profile-identity"><h2 tabindex="-1">${esc(candidate.candidate_name)}</h2>${isDemoEmail(candidate.candidate_email) ? '<span class="ev-badge">Dữ liệu thử — nhân vật hư cấu</span>' : ''}<p class="ev-muted">${esc(candidate.candidate_email)}</p><div class="ev-profile-skills" aria-label="Kỹ năng của ứng viên">${profileSkills()}</div></div><aside class="ev-profile-match" aria-label="Mức đáp ứng kỹ năng"><strong>Mức đáp ứng kỹ năng</strong><div data-ev-profile-coverage aria-live="polite">${profileCoverage()}</div></aside></div>
      <div class="ev-detail-tabs" role="group" aria-label="Nội dung hồ sơ"><button type="button" class="ev-button" data-action="process-view" aria-pressed="${s.detailTab==='process'}">Thông tin</button><button type="button" class="ev-button" data-action="evidence-view" aria-pressed="${s.detailTab==='evidence'}">Dẫn chứng</button><button type="button" class="ev-button" data-action="original-cv" aria-pressed="${s.detailTab==='original'}">CV gốc</button>${button('Tuyển dụng','recruit-candidate',s.detailLoading||s.running||s.saving)}</div>
      ${s.detailTab==='process'?'<div id="ev-process-detail"></div>':s.detailTab==='original'?`<div class="ev-original-inline"><div class="ev-toolbar"><h2>CV gốc</h2><label class="ev-button">${s.cvLoading?'Đang tải…':'Tải lên CV'}<input type="file" data-cv-upload accept=".pdf,.png,.jpg,.jpeg,.webp,.txt" style="display:none" ${s.cvLoading?'disabled':''}></label>${s.originalCV?button('Xem toàn bộ CV','full-cv')+button('Tải CV gốc','download-cv'):''}</div><p class="ev-muted">PDF, PNG, JPG, WEBP hoặc TXT · Tối đa 5 MB</p>${s.cvLoading?'<p role="status">Đang tải CV gốc…</p>':''}${s.cvError?`<p class="ev-error" role="alert">${esc(s.cvError)}</p>`:''}${s.cvNotice?`<p role="status">${esc(s.cvNotice)}</p>`:''}${s.originalCV?`<p class="ev-muted">${esc(s.originalCV.filename)}</p>${cvView(s.originalCV)}`:''}</div>`:`
      ${s.profileHash ? '<p class="ev-warning">Đang xem dẫn chứng theo bộ lọc hiện tại. Kết quả HR sửa sẽ được dùng khi tính lại số mục đạt.</p>' + button('Về Tuyển dụng nhanh', 'quick-tab') : button(s.running ? 'Đang đối chiếu…' : data?.id ? 'Chạy lại' : 'Đối chiếu yêu cầu', 'analyse', s.running || s.detailLoading || s.saving)}
      ${s.detailLoading ? '<p role="status">Đang tải kết quả…</p>' : ''}${s.detailError ? `<p role="alert" class="ev-error">${esc(s.detailError)} ${button('Thử lại', 'detail-retry')}</p>` : ''}
      ${data?.id ? `<p class="ev-muted">Đối chiếu bằng: ${esc(engines[data.provider] || data.provider)} · Lần #${data.id}</p>` : '<p>Chưa đánh giá.</p>'}
      ${data?.error_code === 'LLM_UNAVAILABLE_KEYWORD_FALLBACK' ? '<p class="ev-muted">LLM không khả dụng; kết quả dùng đối chiếu từ khóa.</p>' : ''}
      ${data?.status === 'error' ? `<p class="ev-warning">${data.error_code === 'LLM_UNAVAILABLE_KEYWORD_FALLBACK' ? 'LLM lỗi; các dòng bên dưới chỉ là kết quả đối chiếu từ khóa.' : 'Chưa đánh giá: ' + esc(data.error_code) + '.'} Có thể chạy lại; hồ sơ ứng tuyển vẫn được giữ.</p>` : ''}
      ${data?.status === 'unreadable' ? '<p class="ev-warning">CV rỗng hoặc quá ngắn để đối chiếu. Chưa gọi dịch vụ AI.</p>' : ''}
      ${data?.stale || data?.cv_stale ? '<p class="ev-warning">Kết quả cũ: yêu cầu tin hoặc nội dung CV đã thay đổi. Hãy chạy lại trước khi xác nhận.</p>' : ''}
      ${rows.length ? `<div style="overflow:auto"><table class="ev-table"><thead><tr><th>Yêu cầu</th><th>Nhận định</th><th>Dẫn chứng nguyên văn</th></tr></thead><tbody>${rows.map(r => `<tr class="ev-row" data-row="${r.id}" aria-selected="${r.id === s.active}"><td><button type="button" data-row="${r.id}">${esc(r.requirement_name)}</button></td><td>${window.RecruitmentStatuses.chip('evidence',r.review_result || r.result)}${r.review_result ? '<div class="ev-muted">HR đã kiểm tra</div>' : ''}</td><td>${esc(r.quote ? r.quote.slice(0, 180) + (r.quote.length > 180 ? '…' : '') : 'Không có đoạn trích được xác nhận.')}</td></tr>`).join('')}</tbody></table></div><p class="ev-muted">Chọn một dòng để xem dẫn chứng và kiểm tra nhận định.</p>` : ''}
      ${row ? `<div class="ev-review"><h2>Kiểm tra: ${esc(row.requirement_name)}</h2><p class="ev-muted">Nhận định gốc của bộ đối chiếu: ${esc(labels[row.ai_result_original])}. Sau kiểm tra trích dẫn: ${esc(labels[row.result])}.</p>
      ${row.reviewer_id ? `<p class="ev-muted">Người kiểm tra: ${esc(row.reviewer_name)} (#${row.reviewer_id}) · ${esc(row.reviewed_at)} UTC<br>Lý do: ${esc(row.review_reason || 'Xác nhận, không sửa nhận định.')}</p>` : ''}
      <label>Nhận định của HR <select id="ev-review-result">${Object.entries(labels).map(([value, label]) => `<option value="${value}" ${value === (row.review_result || row.result) ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Lý do (bắt buộc khi sửa)<textarea id="ev-review-reason" maxlength="4000">${esc(row.review_reason || '')}</textarea></label>${button(s.saving ? 'Đang lưu…' : 'Xác nhận / lưu nhận định', 'review', s.saving || s.running || data.stale || data.cv_stale)}</div>` : ''}
      `}</section>` : '<section id="ev-process-list"></section>'}` : ''}${s.cvFull&&s.originalCV?`<div class="ev-cv-modal" role="dialog" aria-modal="true" aria-label="Toàn bộ CV"><section class="ev-full-view"><div class="ev-page-title"><h2>${esc(s.originalCV.filename)}</h2>${button('Đóng','close-full-cv')}</div>${cvView(s.originalCV,true)}</section></div>`:''}</div>`;
      if((s.mode!=='quick'||candidate)&&!s.loading&&!s.error&&s.jobs.length&&window.SkillGapPipeline){
        const list = root.querySelector('#ev-process-list');
        if (list) {
          s.pipelineList = window.SkillGapPipeline.mountList(list, s.job, openReview, s.pipelineList,
            {onReady:restoreListPosition});
        }
        s.pipelineDetail?.dispose?.();s.pipelineDetail=null;
        if(candidate&&s.detailTab==='process'&&s.detailLoading)root.querySelector('#ev-process-detail').innerHTML='<p role="status">Đang mở hồ sơ…</p>';
        if(candidate&&s.detailTab==='process'&&!s.detailLoading)s.pipelineDetail=window.SkillGapPipeline.mountDetail(root.querySelector('#ev-process-detail'),s.selected);
      }
      const quickPanel = root.querySelector('#ev-quick-panel');
      if (quickPanel && window.SkillGapQuickHire) {
        s.quickState = window.SkillGapQuickHire.mount(quickPanel, s.job,
          (id, hash, ids) => openReview(id, ids, hash), s.quickState, {onReady:restoreListPosition});
      }
    }
    function clearOriginal(){if(s.originalCV?.url)URL.revokeObjectURL(s.originalCV.url);s.originalCV=null;s.cvFull=false;}
    function cvView(doc,full=false){return doc.content_type.startsWith('image/')?`<img class="ev-image-view" data-action="${full?'':'full-cv'}" src="${esc(doc.url)}" alt="CV gốc — ${esc(doc.filename)}">`:doc.content_type==='application/pdf'?`<iframe class="ev-file-view" src="${esc(doc.url)}" title="CV PDF gốc"></iframe>`:`<pre class="ev-cv-document" data-action="${full?'':'full-cv'}">${esc(doc.content||'')}</pre>`;}
    async function loadOriginal() {
      const id = s.selected, version = s.version;
      const current = () => live() && s.selected === id && s.version === version;
      s.detailTab = 'original';
      s.cvLoading = true;
      s.cvError = '';
      render();
      try {
        const doc = await request(`/applications/${id}/original-cv`);
        const blob = await request(doc.file_url, {}, 'blob');
        if (doc.content_type.startsWith('text/')) doc.content = await blob.text();
        if (!current()) return;
        clearOriginal();
        doc.url = URL.createObjectURL(blob);
        s.originalCV = doc;
      } catch (error) {
        if (current()) s.cvError = error.message;
      } finally {
        if (current()) { s.cvLoading = false; render(); }
      }
    }
    function profileSkills() {
      if (s.candidateSkills === null) return '<span class="ev-muted">Đang tải kỹ năng…</span>';
      if (s.candidateSkills === false) return '<span class="ev-muted">Không tải được kỹ năng. Mở lại hồ sơ để thử lại.</span>';
      if (!s.candidateSkills.length) return '<span class="ev-muted">Chưa có kỹ năng để đối chiếu</span>';
      return s.candidateSkills.map(skill => {
        const supported = skill.result === 'supported';
        return `<span class="ev-profile-skill" data-supported="${supported}" title="${esc(skill.source === 'keyword' && supported ? 'Có từ khóa trong CV' : labels[skill.result] || 'Chưa đối chiếu')}">${supported ? '✓ ' : ''}${esc(skill.label)}</span>`;
      }).join('');
    }
    function profileCoverage() {
      const status = window.RecruitmentStatuses;
      if (s.profileHash) {
        const scope = 'Theo bộ lọc Tuyển dụng nhanh';
        const run = s.run;
        if (s.detailLoading) return '<span class="ev-muted">Đang tải…</span>';
        if (s.detailError) return '<span class="ev-muted">Không tải được kết quả</span>';
        if (!run?.id) return `<span class="ev-muted">Chưa đánh giá</span><small class="ev-muted">${scope}</small>`;
        const requirements = run.requirements_snapshot || [];
        const supported = new Set((run.evidence || []).filter(row =>
          (row.review_result || row.result) === 'supported').map(row => row.requirement_name));
        const x = run.status === 'done' && !run.stale && !run.cv_stale
          ? requirements.filter(label => supported.has(label)).length : null;
        return status.skillCoverage(x, requirements.length, scope) + `<small class="ev-muted">${scope}</small>`;
      }
      if (s.candidateSkills === null) return '<span class="ev-muted">Đang tải…</span>';
      if (s.candidateSkills === false) return '<span class="ev-muted">Không tải được kết quả</span>';
      const priorities = s.pipelineList?.priorities;
      const scope = priorities?.size ? 'Theo kỹ năng ưu tiên đã áp dụng' : 'Theo kỹ năng của tin tuyển dụng';
      return status.candidateSkillCoverage(s.candidateSkills, priorities) + `<small class="ev-muted">${scope}</small>`;
    }
    async function loadProfileSkills(id, version) {
      let skills;
      try {
        const query = new URLSearchParams();
        for (const skill of s.pipelineList?.priorities || []) query.append('priority_skills', skill);
        const data = await request(`/jobs/${s.job}/pipeline${query.size ? '?' + query : ''}`);
        skills = data.applications.find(row => row.id === id)?.skill_states || [];
      } catch (_) {
        skills = false;
      }
      if (!live() || version !== s.version || s.selected !== id) return;
      s.candidateSkills = skills;
      const box = root.querySelector('.ev-profile-skills');
      if (box) box.innerHTML = profileSkills();
      const coverage = root.querySelector('[data-ev-profile-coverage]');
      if (coverage) coverage.innerHTML = profileCoverage();
    }
    async function detail(tab = s.mode === 'quick' ? 'evidence' : 'process') {
      const version = ++s.version, id = s.selected;
      s.candidateSkills = null;
      s.run = null; s.active = null;s.detailTab=tab; s.cvLoading=false; s.detailError = '';clearOriginal();s.cvError='';s.cvNotice=''; s.detailLoading = true; render();
      loadProfileSkills(id, version);
      try { const data = await request(`/applications/${id}/evidence${s.profileHash ? '?profile_hash=' + encodeURIComponent(s.profileHash) : ''}`); if (!live() || version !== s.version) return; s.run = data; s.active = data.evidence?.[0]?.id ?? null; return data; }
      catch (e) { if (version === s.version) s.detailError = e.message; }
      finally {
        if (version === s.version) {
          s.detailLoading = false;
          if (tab === 'original' && s.detailTab === 'original' && !s.cvLoading && !s.originalCV) loadOriginal();
          else render();
        }
      }
    }
    async function chooseJob(id) {
      s.review = null; s.restore = null;
      s.job = id; s.selected = null; s.applications = []; s.run = null; s.error = ''; s.errorStatus = null; s.loading = true; s.profileHash = null;
      if(s.pipelineList?.job!==String(id)){s.pipelineList?.dispose?.();s.pipelineList=null;}
      if (s.quickState?.job !== String(id)) { s.quickState?.dispose?.(); s.quickState = null; }
      const version = ++s.version; render();
      try { const apps = await request(`/jobs/${id}/applications`); if (!live() || version !== s.version) return; s.applications = apps;s.selected=apps.find(a=>a.id===window.evidencePreferredApplication)?.id??null;s.profileHash=window.evidencePreferredHash||null;window.evidencePreferredApplication=null;window.evidencePreferredHash=null;s.loading=false;render();if(s.selected)await detail(); }
      catch (e) { if (version === s.version) { s.error = e.message; s.errorStatus = e.status; s.loading = false; render(); } }
    }
    async function jobs(preferred) {
      const version = ++s.version; s.loading = true; s.error = ''; s.errorStatus = null; s.jobs = []; s.applications = []; s.selected = null; s.run = null; render();
      try { const data = await request('/jobs/my-jobs'); if (!live() || version !== s.version) return; s.jobs = data.sort((a,b)=>Number(b.title.startsWith('[CV tự tạo]'))-Number(a.title.startsWith('[CV tự tạo]'))||Number(b.industry==='IT')-Number(a.industry==='IT')||b.id-a.id); const id = data.find(j => String(j.id) === String(preferred))?.id || s.jobs[0]?.id; if (id) await chooseJob(String(id)); else { s.loading = false; render(); } }
      catch (e) { if (version === s.version) { s.error = e.message; s.errorStatus = e.status; s.loading = false; render(); } }
    }
    root.onclick = async event => {
      const app = event.target.closest('[data-candidate]'); if (app) { s.selected = Number(app.dataset.candidate); await detail(); return; }
      const selected = event.target.closest('[data-row]'); if (selected) { s.active = Number(selected.dataset.row); render();  return; }
      const action = event.target.closest('[data-action]')?.dataset.action, candidate = s.applications.find(a => a.id === s.selected);
      if(action==='quick-tab'){if(s.mode==='quick'){backToResults();return;}window.evidencePreferredJob=s.job;location.hash='/employer/recruitment';return;}
      if (action === 'evidence-tab') { s.mode = 'evidence'; s.profileHash = null; if (s.selected) await detail(); else render(); return; }
      if(action==='back-list'){backToResults();return;}
      if (action === 'previous-candidate' || action === 'next-candidate') {
        const candidates = reviewCandidates();
        const index = candidates.findIndex(item => item.id === s.selected);
        const next = candidates[index + (action === 'next-candidate' ? 1 : -1)];
        if (next) { s.selected = next.id; await detail(s.detailTab); }
        return;
      }
      if(action==='process-view'){s.detailTab='process';render();return;}
      if(action==='evidence-view'){s.detailTab='evidence';render();return;}
      if(action==='recruit-candidate'&&candidate){window.SkillGapQuickHire.compose(s.job,candidate.id);return;}
      if(action==='full-cv'&&s.originalCV){s.cvFull=true;render();return;}if(action==='close-full-cv'){s.cvFull=false;render();return;}
      if(action==='download-cv'&&s.originalCV){const link=document.createElement('a');link.href=s.originalCV.url;link.download=s.originalCV.filename;link.click();return;}
      if(action==='original-cv'&&candidate){s.detailTab='original';if(s.originalCV){render();return;}await loadOriginal();return;}
      if (action === 'reload') { await jobs(s.job); return; } if (action === 'detail-retry') { await detail(); return; }
      if ((action === 'invite' || action === 'acknowledge') && candidate) { window.evidencePreferredJob=s.job;location.hash='/employer/recruitment';return; }
      if (!['analyse', 'review'].includes(action) || !candidate || s.running || s.saving) return;
      const id = s.selected, version = s.version;
      let path = `/applications/${id}/analyses`, options = { method: 'POST' };
      if (action === 'review') {
        const result = root.querySelector('#ev-review-result').value, reason = root.querySelector('#ev-review-reason').value.trim();
        const row = s.run.evidence.find(r => r.id === s.active);
        if (result !== row.result && !reason) { alert('Bắt buộc ghi lý do khi sửa nhận định.'); return; }
        path = `/evidence/${row.id}/review`; options = { method: 'PATCH', body: JSON.stringify({ review_result: result, review_reason: reason }) };
      }
      s.running = action === 'analyse'; s.saving = action === 'review'; s.detailError = ''; render();
      try { const data = await request(path, options); if (!live() || version !== s.version || id !== s.selected) return; s.run = data; if (action === 'analyse') s.active = data.evidence?.[0]?.id ?? null; loadProfileSkills(id, version); }
      catch (e) { if (version === s.version) s.detailError = e.message; }
      finally { s.running = false; s.saving = false; render(); }
    };
    root.onchange = async event => {if(event.target.matches('[data-cv-upload]')){const file=event.target.files[0],id=s.selected;if(!file)return;if(file.size>5*1024*1024){s.cvError='CV không được vượt quá 5 MB';render();return;}if(!confirm('Tệp mới sẽ thay CV của hồ sơ này. Cần đối chiếu lại khi nội dung thay đổi. Tiếp tục?')){event.target.value='';return;}const body=new FormData();body.append('file',file);s.cvLoading=true;s.cvError='';render();try{const result=await request(`/applications/${id}/original-cv`,{method:'PUT',body});if(s.selected!==id)return;await detail();await loadOriginal();s.cvNotice=result.extraction_status==='unreadable'?'Đã lưu CV gốc. Chưa trích xuất được văn bản đủ để đối chiếu; vui lòng kiểm tra trực tiếp CV.':'Đã lưu CV gốc. Bạn có thể đối chiếu lại nội dung mới.';}catch(e){s.cvError=e.message;}finally{s.cvLoading=false;render();}return;}if(event.target.id==='ev-candidate-nav'){s.selected=Number(event.target.value);detail(s.detailTab);}if(event.target.id==='ev-job')chooseJob(event.target.value);};
    s.chooseJob = chooseJob; s.reload = jobs; s.dispose = () => { s.disposed = true;clearOriginal(); s.version++; s.quickState?.dispose?.();s.pipelineList?.dispose?.();s.pipelineDetail?.dispose?.(); root.onclick = null; root.onchange = null;root.replaceChildren(); };
    jobs(preferredJob); return s.dispose;
  }
  window.SkillGapEvidence = { mount, dispose: () => mounted?.dispose(), applications: () => mounted?.applications || [] };
  if (window.evidenceMountPending) window.renderEmployerCandidatesList();
})();

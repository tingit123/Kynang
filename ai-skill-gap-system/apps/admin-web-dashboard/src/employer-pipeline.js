/* Trial applicant workflow, backed by DB. No automatic hiring decisions. */
(function(){
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const api=`http://${location.hostname||'localhost'}:8000/api`;
 const date=v=>window.RecruitmentStatuses.date(v);
 async function request(path,options={}){
  const token=localStorage.getItem('access_token')||localStorage.getItem('token');
  const config={credentials:'include',...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})}};
  let r=await fetch(api+path,config);if(r.status===401&&token)r=await fetch(api+path,{...config,credentials:'omit'});
  if(!r.ok){const d=await r.json().catch(()=>({}));const e=Error(typeof d.detail==='string'?d.detail:d.detail?.map?.(v=>v.msg).join('; ')||'Không tải được tiến trình.');e.status=r.status;throw e;}return r.json();
 }
 const colors={new:['#f1f5f9','#475569'],screening:['#eff6ff','#1d4ed8'],interviewing:['#f5f3ff','#6d28d9'],offer:['#fff7ed','#c2410c'],hired:['#ecfdf5','#047857'],rejected:['#fff1f2','#be123c']};
 const historicalStageLabels={interview_1:'Phỏng vấn vòng 1',interview_2:'Phỏng vấn vòng 2'};
 const stageLabel=(data,id)=>data.stages.find(s=>s.id===id)?.label||historicalStageLabels[id]||id;
 function badge(data,id){const c=colors[id]||colors.new;return `<span class="pp-badge" style="background:${c[0]};color:${c[1]}">${esc(stageLabel(data,id))}</span>`;}
 function style(){return `<style>
 .pp-root{color:#0f172a;min-width:0}.pp-root button,.pp-root input,.pp-root select,.pp-root textarea{font:inherit;max-width:100%}.pp-root input,.pp-root select,.pp-root textarea{padding:9px 12px;border:1px solid #cbd5e1;border-radius:10px;background:#fff;color:#0f172a;min-width:0}.pp-toolbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:14px 0}.pp-toolbar label{display:flex;align-items:center;gap:8px;font-size:13px}.pp-root h2{font-size:20px;font-weight:850;margin:0}.pp-root h3{font-size:16px;font-weight:800;margin:0}.pp-root p{margin:7px 0}.pp-muted{font-size:12px;color:#64748b}.pp-badge{display:inline-block;font-size:11px;line-height:1.5;font-weight:750;border-radius:7px;padding:4px 8px;white-space:normal}.pp-panel{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:18px;margin-bottom:14px;min-width:0}.pp-stages{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.pp-stage{border:1px solid #e2e8f0;border-radius:12px;background:#fff;padding:10px 12px;text-align:left;cursor:pointer;font-size:12px;min-width:110px;flex:1;color:#334155}.pp-stage strong{display:block;font-size:23px;margin-top:4px}.pp-stage[aria-pressed=true]{border-color:#0d5f57;background:#edf9f6;color:#0d5f57;box-shadow:inset 0 0 0 1px #0d5f57}.pp-toggle{display:flex;gap:5px}.pp-toggle button[aria-pressed=true]{background:#0d5f57;color:white}.pp-list{display:grid;gap:10px}.pp-person{display:flex;align-items:center;gap:14px;justify-content:space-between;width:100%;border:1px solid #e2e8f0;background:#fff;border-radius:14px;padding:16px;cursor:pointer;text-align:left;color:#0f172a}.pp-person:hover,.pp-person.pp-current{border-color:#0d5f57;background:#f2faf8}.pp-person>div{min-width:0;overflow-wrap:anywhere}.pp-person-main{background:none;border:0;padding:0;text-align:left;color:inherit;min-width:0;cursor:pointer;flex:1}.pp-person-main>span{display:block;overflow-wrap:anywhere}.pp-person-main .pp-person-info{display:flex}.pp-skill-list{display:flex;flex-wrap:wrap;gap:5px;align-items:center;flex:1;min-width:0}.pp-skill{font-size:11px;border:1px solid #cbd5e1;border-radius:6px;padding:3px 6px;background:#f8fafc;color:#64748b;overflow-wrap:anywhere}.pp-skill-supported{background:#e9f8ef;border-color:#b4dec6;color:#166534}.pp-root .pp-skill-more{font-size:11px;border:1px solid #0d5f57;border-radius:8px;padding:3px 7px;color:#0d5f57;background:#f0fdfa;cursor:pointer}.pp-column .pp-skill-list,.pp-compact .pp-skill-list{margin-top:10px}.pp-person-name{font-weight:800}.pp-person-info{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:7px}.pp-owner{font-size:12px;color:#475569}.pp-board{display:flex;gap:12px;overflow:auto;max-width:100%;padding:4px 0 16px;align-items:stretch}.pp-board::-webkit-scrollbar{height:12px}.pp-board::-webkit-scrollbar-thumb{background:#94a3b8;border:2px solid #f8fafc;border-radius:8px}.pp-board::-webkit-scrollbar-track{background:#e2e8f0;border-radius:8px}.pp-column{flex:0 0 230px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:14px;padding:12px}.pp-column h3{margin-bottom:12px;font-size:13px}.pp-column .pp-person{padding:12px;margin:8px 0;display:block}.pp-compact .pp-person{padding:12px;display:block}.pp-compact .pp-list{max-height:75vh;overflow:auto;padding:2px}.pp-form{display:grid;grid-template-columns:minmax(0,1fr);gap:12px}.pp-form label{font-size:13px;font-weight:700;display:grid;gap:6px}.pp-form .pp-wide{grid-column:1/-1}.pp-form textarea{width:100%;min-height:72px;resize:vertical;font-weight:400}.pp-note{width:100%;min-height:80px;resize:vertical;margin-top:10px}.pp-error{color:#b91c1c;font-size:13px}.pp-success{color:#047857;font-size:13px}.pp-timeline{list-style:none;padding:0;margin:14px 0 0;border-left:2px solid #dbe9e5}.pp-timeline li{padding:0 0 18px 18px;position:relative;overflow-wrap:anywhere}.pp-timeline li:before{content:'';width:9px;height:9px;background:#0d5f57;border-radius:50%;position:absolute;left:-5px;top:6px}.pp-timeline .pp-reason{white-space:pre-wrap;background:#f8fafc;border-radius:8px;padding:9px 12px;font-size:13px;margin-top:8px}.pp-people-form{border:1px solid #cbd5e1;border-radius:12px;padding:14px;margin:14px 0;background:#f8fafc}.pp-people-form label{display:grid;gap:5px;font-size:13px}.pp-people-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.pp-detail-state{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px}.pp-root .ev-button{font-size:13px;padding:8px 13px}.pp-empty{padding:20px;text-align:center;color:#64748b}.pp-root :focus-visible{outline:2px solid #0d5f57;outline-offset:3px}
 .pp-root .pp-column-title{display:flex;justify-content:space-between;align-items:center;gap:8px;width:100%;padding:8px;border:1px solid transparent;border-radius:8px;background:#e4efee;color:#0d5f57;text-align:left;cursor:pointer}.pp-column-title:hover{border-color:#0d5f57;background:#edf9f6}.pp-board-person>span{display:block;overflow-wrap:anywhere}.pp-board-person .pp-muted{margin-top:4px}
 @media(max-width:700px){.pp-form,.pp-people-grid{grid-template-columns:minmax(0,1fr)}.pp-stage{min-width:95px}.pp-person{align-items:flex-start;flex-direction:column}.pp-toolbar{align-items:stretch}.pp-toolbar>input{width:100%}.pp-toolbar label{flex-wrap:wrap}.pp-panel{padding:14px}}
 .pp-column{cursor:pointer}.pp-column:hover,.pp-column:focus-within{border-color:#0d5f57}
 .pp-card-summary{display:grid;justify-items:end;gap:5px;flex-shrink:0}@media(max-width:700px){.pp-card-summary{justify-items:start}}
 .pp-filters{padding:14px 16px;margin-bottom:16px;background:#fff;border:1px solid #e2e8f0;border-radius:14px}
 .pp-filter-fields{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end}.pp-filter-fields label{display:grid;gap:5px;min-width:0;font-size:13px;font-weight:650}.pp-filter-fields input,.pp-filter-fields select{width:100%;min-height:40px}
 .pp-view-row{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;border-top:1px solid #e2e8f0;padding-top:12px;margin-top:14px}.pp-toggle{flex-wrap:wrap}
 .pp-contact-filters{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding-top:12px;font-size:13px}.pp-root .pp-contact-filters .ev-button{padding:6px 10px}.pp-contact-filters [aria-pressed=true]{background:#0d5f57;color:#fff}
 .pp-coverage-filter{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding-top:10px;border-top:1px solid #e2e8f0;font-size:13px;font-weight:650}.pp-coverage-filter input{width:92px}
 .pp-priority-row{margin-top:12px;padding:12px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;font-size:13px}
 .pp-priority-heading,.pp-priority-footer{display:flex;align-items:center;justify-content:space-between;gap:8px 14px;flex-wrap:wrap}.pp-priority-heading label,.pp-custom-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.pp-priority-heading select,.pp-custom-row input{padding:6px 9px}
 .pp-priority-choices,.pp-priority-selected{display:flex;gap:6px;align-items:center;flex-wrap:wrap;min-width:0}.pp-priority-choices{margin:10px 0}
 .pp-root .pp-priority-chip{border:1px solid #cbd5e1;border-radius:8px;padding:4px 8px;background:#fff;color:#0d5f57;cursor:pointer;font-size:12px;overflow-wrap:anywhere}.pp-priority-chip[aria-pressed=true],.pp-priority-selected .pp-priority-chip{border-color:#8ebcb1;background:#e6f4f1;font-weight:700}
 .pp-priority-footer{border-top:1px solid #e2e8f0;padding-top:10px;margin-top:10px}.pp-priority-footer [data-pp-action=apply-priorities]:enabled{background:#0d5f57;color:#fff}
 #pp-priority-error:empty{display:none}
 @media(max-width:600px){.pp-filter-fields{grid-template-columns:minmax(0,1fr) auto}.pp-filter-fields label:first-child{grid-column:1/-1}.pp-custom-row label{flex-basis:100%}.pp-custom-row input{flex:1;min-width:0}}
 </style>`;}
 const button=(label,action,disabled=false)=>`<button type="button" class="ev-button" data-pp-action="${action}" ${disabled?'disabled':''}>${label}</button>`;
 function mountList(root,job,onSelect,previous,options={}){
  const s=previous?.job===String(job)?previous:{job:String(job),data:null,stage:'',search:'',view:'list',minPct:null,contact:null,priorities:new Set(),priorityDraft:new Set(),priorityIndustry:'',customSkill:'',skillError:'',expandedSkills:new Set(),generation:0};
  s.root=root;s.onSelect=onSelect;s.compact=!!options.compact;s.selected=options.selected;s.loading=true;s.error='';s.disposed=false;
  const live=()=>!s.disposed&&s.root.isConnected;
  function matchingRows() {
   const query = s.search.trim().toLocaleLowerCase();
   return (s.data?.applications || []).filter(candidate => {
    if (s.compact) return true;
    const matchesStage = !s.stage || candidate.stage === s.stage;
    const matchesQuery = !query || (candidate.candidate_name + ' ' + candidate.candidate_email).toLocaleLowerCase().includes(query);
    if (!matchesStage || !matchesQuery) return false;
    if (s.minPct === null) return true;
    const status = window.RecruitmentStatuses;
    const {x, y} = status.candidateSkillCounts(candidate.skill_states || [], s.priorities);
    const percent = status.skillPercent(x, y);
    return percent !== null && percent >= s.minPct;
   });
  }
  function matchesContact(candidate, contact) {
   return !contact || (candidate.contact_states || []).includes(contact);
  }
  function rows(matching = matchingRows()) {
   const filtered = matching.filter(candidate => matchesContact(candidate, s.contact));
   if (!s.priorities.size) return filtered;
   return filtered.map(candidate => {
    const supported = (candidate.skill_states || []).filter(skill => skill.result === 'supported');
    const priorityCount = supported.filter(skill => s.priorities.has(skill.label)).length;
    return { candidate, priorityCount, total: supported.length };
   }).sort((a, b) => b.priorityCount - a.priorityCount || b.total - a.total).map(row => row.candidate);
  }
  function skillTags(candidate) {
   const values = [...(candidate.skill_states || [])].sort((a, b) =>
    Number(s.priorities.has(b.label)) - Number(s.priorities.has(a.label)));
   const expanded = s.expandedSkills.has(candidate.id);
   const limit = s.compact ? 3 : 4;
   const titles = {supported:'Có dẫn chứng trong CV',not_found:'Chưa thấy dẫn chứng',needs_review:'Cần HR kiểm tra',unreadable:'CV chưa đọc được',unassessed:'Chưa đối chiếu'};
   const tags = values.slice(0, expanded ? values.length : limit).map(skill => {
    const supported = skill.result === 'supported';
    const priority = s.priorities.has(skill.label);
    const evidence = skill.source === 'keyword' && supported ? 'Có từ khóa trong CV' : titles[skill.result] || titles.unassessed;
    const title = (priority ? 'Kỹ năng ưu tiên · ' : '') + evidence;
    return `<span class="pp-skill ${supported ? 'pp-skill-supported' : ''}" title="${esc(title)}">${priority ? '★ ' : ''}${supported ? '✓ ' : ''}${esc(skill.label)}</span>`;
   }).join('');
   const more = values.length > limit ? `<button type="button" class="pp-skill-more" data-pp-skills-expand="${candidate.id}" aria-expanded="${expanded}">${expanded ? 'Thu gọn' : `Xem thêm (${values.length - limit})`}</button>` : '';
   return `<div class="pp-skill-list" aria-label="Kỹ năng của ${esc(candidate.candidate_name)}">${tags || '<span class="pp-muted">Chưa có kỹ năng để đối chiếu</span>'}${more}</div>`;
  }
  function card(a){return `<article class="pp-person ${a.id===s.selected?'pp-current':''}" data-pp-card="${a.id}"><button type="button" class="pp-person-main" data-pp-person="${a.id}" aria-pressed="${a.id===s.selected}"><span class="pp-person-name">${esc(a.candidate_name)}</span><span class="pp-muted">${esc(a.candidate_email)}</span><span class="pp-person-info">${badge(s.data,a.stage)}</span>${a.is_demo?'<span class="pp-muted">Dữ liệu thử</span>':''}</button>${skillTags(a)}<div class="pp-card-summary">${window.RecruitmentStatuses.candidateSkillCoverage(a.skill_states || [], s.priorities)}${!s.compact&&(s.view==='list'||s.stage)?'<span class="pp-owner" aria-hidden="true">Mở hồ sơ →</span>':''}</div></article>`;}
  function boardCandidate(candidate) {
   return `<div class="pp-person pp-board-person">
    <span class="pp-person-name">${esc(candidate.candidate_name)}</span>
    <span class="pp-muted">${esc(candidate.candidate_email)}</span>
   </div>`;
  }
  function boardColumn(stage, candidates) {
   return `<section class="pp-column" data-pp-open-stage="${stage.id}">
    <h3><button type="button" class="pp-column-title"
     aria-label="Xem danh sách ${esc(stage.label)} (${candidates.length} hồ sơ)">
     <span>${esc(stage.label)} · ${candidates.length}</span><span aria-hidden="true">→</span>
    </button></h3>
    ${candidates.map(boardCandidate).join('') || '<p class="pp-muted">Chưa có hồ sơ</p>'}
   </section>`;
  }
  function renderRows() {
   const box = s.root.querySelector('[data-pp-list-content]');
   if (!box || !s.data) return;
   const matching = matchingRows();
   const visible = rows(matching);
   for (const button of s.root.querySelectorAll('[data-pp-contact-filter]')) {
    const contact = button.dataset.ppContactFilter || null;
    const count = button.querySelector('[data-pp-contact-count]');
    if (count) count.textContent = '(' + matching.filter(candidate => matchesContact(candidate, contact)).length + ')';
    button.setAttribute('aria-pressed', String(s.contact === contact));
   }
   if (s.view === 'board' && !s.stage) {
    const columns = s.data.stages.map(stage => boardColumn(stage, visible.filter(candidate => candidate.stage === stage.id)));
    box.innerHTML = `<div class="pp-board" tabindex="0" aria-label="Bảng trạng thái tuyển dụng, có thể cuộn ngang">${columns.join('')}</div>`;
   } else {
    box.innerHTML = `<div class="pp-list">${visible.map(card).join('') || '<div class="pp-empty">Không có ứng viên theo điều kiện đang chọn.</div>'}</div>`;
   }
   const count = s.root.querySelector('[data-pp-visible]');
   if (count) count.textContent = `${visible.length}/${s.data.applications.length} hồ sơ`;
  }
  function priorityFilter() {
   const groups = window.SkillGapSkillOptions || {};
   const industry = s.priorityIndustry || (Object.hasOwn(groups, s.data.industry) ? s.data.industry : 'IT');
   const choices = groups[industry] || [];
   const draft = [...s.priorityDraft];
   const hasChanges = draft.length !== s.priorities.size || draft.some(skill => !s.priorities.has(skill));
   return `<section class="pp-priority-row" aria-labelledby="pp-priority-label">
    <div class="pp-priority-heading"><h3 id="pp-priority-label">Ưu tiên hiển thị kỹ năng</h3>
     <label>Kỹ năng theo ngành <select data-pp-priority-industry>${Object.keys(groups).map(group => `<option value="${esc(group)}" ${group === industry ? 'selected' : ''}>${esc(group)}</option>`).join('')}</select></label>
    </div>
    <div class="pp-priority-choices" aria-label="Chọn nhanh kỹ năng">
     ${choices.map(skill => `<button type="button" class="pp-priority-chip" data-pp-priority-choice="${esc(skill)}" aria-pressed="${draft.some(label => sameSkill(label, skill))}">${esc(skill)}</button>`).join('')}
    </div>
    <div class="pp-custom-row"><label for="pp-custom-skill">Bổ sung kỹ năng</label>
     <input id="pp-custom-skill" data-pp-custom-skill maxlength="100" placeholder="Nhập kỹ năng khác…" value="${esc(s.customSkill)}" aria-describedby="pp-priority-error">
     ${button('Thêm kỹ năng', 'add-priority')}
    </div>
    <p id="pp-priority-error" class="pp-error" role="alert">${esc(s.skillError)}</p>
    <div class="pp-priority-footer">
     <div class="pp-priority-selected">
      <strong>Kỹ năng đã chọn</strong>
      ${draft.map(skill => `<button type="button" class="pp-priority-chip" data-pp-remove-priority="${esc(skill)}" aria-label="Bỏ ${esc(skill)}">${esc(skill)} <span aria-hidden="true">×</span></button>`).join('') || '<span class="pp-muted">Chưa chọn kỹ năng</span>'}
     </div>
     ${button(s.loading ? 'Đang tải…' : 'Áp dụng ưu tiên', 'apply-priorities', !hasChanges || s.loading)}
    </div>
    <p class="pp-muted">Ưu tiên hồ sơ có dẫn chứng hoặc từ khóa khớp trong CV. Tối đa 12 kỹ năng.${hasChanges ? ' Có thay đổi chưa áp dụng.' : ''}</p>
    <div class="pp-coverage-filter">
     <label for="pp-min-pct">% đáp ứng tối thiểu</label>
     <input id="pp-min-pct" name="min_pct" type="number" min="0" max="100" step="1" placeholder="Tất cả" value="${s.minPct ?? ''}">
    </div>
   </section>`;
  }
  function sameSkill(first, second) {
   return first.toLocaleLowerCase() === second.toLocaleLowerCase();
  }
  function editPriority(value, toggle) {
   const label = value.trim().replace(/\s+/g, ' ');
   const existing = [...s.priorityDraft].find(skill => sameSkill(skill, label));
   s.skillError = '';
   if (!label) s.skillError = 'Hãy nhập tên kỹ năng.';
   else if (existing && toggle) s.priorityDraft.delete(existing);
   else if (existing) s.skillError = 'Kỹ năng này đã được chọn.';
   else if (s.priorityDraft.size >= 12) s.skillError = 'Chỉ chọn tối đa 12 kỹ năng ưu tiên.';
   else {
    s.priorityDraft.add(label);
    if (!toggle) s.customSkill = '';
   }
   render();
  }
  function contactFilters() {
   const labels = {'':'Tất cả', ...window.RecruitmentStatuses.contact};
   return `<div class="pp-contact-filters" role="group" aria-label="Trạng thái liên hệ">
    <strong>Trạng thái liên hệ</strong>
    ${Object.entries(labels).map(([key, label]) => `<button type="button" class="ev-button"
     data-pp-contact-filter="${key}" aria-pressed="${s.contact === (key || null)}">
     ${esc(label)}${key ? ' <span data-pp-contact-count></span>' : ''}
    </button>`).join('')}
   </div>`;
  }
  function filters() {
   return `<div class="pp-filters">
    <div class="pp-filter-fields">
     <label>Tìm ứng viên<input data-pp-search type="search" placeholder="Tên hoặc email…" value="${esc(s.search)}"></label>
     ${button('Bỏ lọc', 'reset')}
    </div>
    <div class="pp-view-row">
     <div class="pp-toggle" role="group" aria-label="Chế độ xem">
      <button type="button" class="ev-button" data-pp-view="list" aria-pressed="${s.view === 'list'}">Danh sách</button>
      <button type="button" class="ev-button" data-pp-view="board" aria-pressed="${s.view === 'board'}">Bảng tiến trình</button>
     </div>
     <span class="pp-muted" data-pp-visible aria-live="polite"></span>
    </div>
    ${priorityFilter()}
    ${contactFilters()}
   </div>`;
  }
  function render() {
   if (!live()) return;
   s.root.innerHTML = style() + `<div class="pp-root ${s.compact ? 'pp-compact' : ''}">
    <div class="pp-detail-state"><h2>Danh sách ứng viên</h2></div>
    ${s.loading && !s.data ? '<p role="status">Đang tải thông tin…</p>' : ''}
    ${s.error ? `<p class="pp-error" role="alert">${esc(s.error)} ${button('Tải lại','reload')}</p>` : ''}
    ${s.data && !s.compact ? filters() : ''}
    ${s.data ? '<div data-pp-list-content></div>' : ''}
   </div>`;
   renderRows();
  }
  async function refresh(priorities = s.priorities) {
   const requested = new Set(priorities);
   const generation = ++s.generation;
   s.loading = true;
   s.error = '';
   render();
   try {
    const query = new URLSearchParams();
    for (const skill of requested) query.append('priority_skills', skill);
    const data = await request(`/jobs/${s.job}/pipeline${query.size ? '?' + query : ''}`);
    if (generation !== s.generation || !live()) return;
    s.data = data;
    s.priorities = requested;
   } catch (error) {
    if (generation === s.generation) s.error = error.message;
   } finally {
    if (generation === s.generation) {
     s.loading = false;
     render();
     options.onReady?.();
    }
   }
  }
  root.onclick=e=>{
   const contact = e.target.closest('[data-pp-contact-filter]');
   if (contact) {
    s.contact = contact.dataset.ppContactFilter || null;
    renderRows();
    return;
   }
   const column = e.target.closest('[data-pp-open-stage]');
   if (column) {
    s.stage = column.dataset.ppOpenStage;
    render();
    s.root.querySelector('[data-pp-stage][aria-pressed="true"]')?.focus();
    return;
   }
   const choice = e.target.closest('[data-pp-priority-choice]');
   if (choice) {
    editPriority(choice.dataset.ppPriorityChoice, true);
    [...s.root.querySelectorAll('[data-pp-priority-choice]')].find(el => el.dataset.ppPriorityChoice === choice.dataset.ppPriorityChoice)?.focus();
    return;
   }
   const remove = e.target.closest('[data-pp-remove-priority]');
   if (remove) {
    s.priorityDraft.delete(remove.dataset.ppRemovePriority);
    s.skillError = '';
    render();
    s.root.querySelector('[data-pp-custom-skill]')?.focus();
    return;
   }
   const priorityAction = e.target.closest('[data-pp-action]')?.dataset.ppAction;
   if (priorityAction === 'add-priority') {
    editPriority(s.customSkill, false);
    s.root.querySelector('[data-pp-custom-skill]')?.focus();
    return;
   }
   if (priorityAction === 'apply-priorities') {
    refresh(s.priorityDraft);
    return;
   }
   const more=e.target.closest('[data-pp-skills-expand]');if(more){const id=Number(more.dataset.ppSkillsExpand);s.expandedSkills.has(id)?s.expandedSkills.delete(id):s.expandedSkills.add(id);renderRows();return;}const person=e.target.closest('[data-pp-person]'),card=e.target.closest('[data-pp-card]');if(person||card){s.onSelect(Number(person?.dataset.ppPerson||card.dataset.ppCard), rows().map(candidate => candidate.id));return;}const stage=e.target.closest('[data-pp-stage]');if(stage){s.stage=s.stage===stage.dataset.ppStage?'':stage.dataset.ppStage;render();return;}const view=e.target.closest('[data-pp-view]');if(view){s.view=view.dataset.ppView;s.stage='';render();s.root.querySelector('[data-pp-view][aria-pressed="true"]')?.focus();return;}const action=e.target.closest('[data-pp-action]')?.dataset.ppAction;if(action==='reset'){s.stage='';s.search='';s.minPct=null;s.contact=null;s.priorityDraft.clear();s.customSkill='';s.skillError='';refresh(s.priorityDraft);s.root.querySelector('[data-pp-search]')?.focus();}if(action==='reload')refresh();};
  root.oninput = event => {
   const target = event.target;
   if (target.id === 'pp-min-pct') {
    target.setAttribute('aria-invalid', String(!target.validity.valid));
    if (!target.validity.valid) return;
    s.minPct = target.value === '' ? null : target.valueAsNumber;
    renderRows();
    return;
   }
   if (target.matches('[data-pp-search]')) {
    s.search = target.value;
    renderRows();
   }
   if (target.matches('[data-pp-custom-skill]')) {
    s.customSkill = target.value;
    s.skillError = '';
    s.root.querySelector('#pp-priority-error').textContent = '';
   }
  };
  root.onchange = event => {
   const target = event.target;
   if (target.matches('[data-pp-priority-industry]')) {
    s.priorityIndustry = target.value;
    render();
    s.root.querySelector('[data-pp-priority-industry]').focus();
   }
  };
  root.onkeydown = event => {
   if (event.key === 'Enter' && event.target.matches('[data-pp-custom-skill]')) {
    event.preventDefault();
    s.root.querySelector('[data-pp-action="add-priority"]').click();
   }
  };
  s.refresh=refresh;s.dispose=()=>{s.disposed=true;s.generation++;};refresh();return s;
 }
 function mountDetail(root,id,onChanged){
  const s={data:null,loading:true,busy:false,error:'',notice:'',stage:'',reason:'',note:'',disposed:false};
  const live=()=>!s.disposed&&root.isConnected;
  function eventText(e){if(e.details.interview){const item=e.details.interview;const states={scheduled:'Đã lên lịch',completed:'Đã diễn ra',no_show:'Ứng viên vắng',cancelled:'Đã hủy'};const previous=item.before;return (e.event_type==='interview_created'?'Tạo lịch phỏng vấn: ':'Cập nhật lịch phỏng vấn: ')+(previous?date(previous.starts_at)+' → ':'')+date(item.starts_at)+' · '+(states[item.status]||item.status);}if(e.event_type==='note')return 'Đã thêm ghi chú nội bộ';const changes=[];if(e.details.stage)changes.push(`${stageLabel(s.data,e.details.stage.from)} → ${stageLabel(s.data,e.details.stage.to)}`);if(e.details.assignee)changes.push(`Phụ trách: ${e.details.assignee.from} → ${e.details.assignee.to}`);return (e.event_type==='demo_setup'?'Khởi tạo dữ liệu thử: ':'')+changes.join(' · ');}
  function accept(data){s.data=data;s.stage=data.stage;}
  function render(){if(!live())return;const d=s.data;root.innerHTML=style()+`<div class="pp-root">${s.loading?'<p role="status">Đang tải thông tin…</p>':''}${s.error?`<p class="pp-error" role="alert">${esc(s.error)} ${button('Tải lại thông tin','reload',s.busy)}</p>`:''}${s.notice?`<p class="pp-success" role="status">${esc(s.notice)}</p>`:''}${d?`<section class="pp-panel"><div class="pp-detail-state"><h2>Thông tin tuyển dụng</h2>${badge(d,d.stage)}</div><form data-pp-process-form><div class="pp-form"><label>Trạng thái tuyển dụng<select data-pp-field="stage" ${s.busy?'disabled':''}>${d.stages.map(v=>`<option value="${v.id}" ${s.stage===v.id?'selected':''}>${esc(v.label)}</option>`).join('')}</select></label><label class="pp-wide">Lý do cập nhật<textarea data-pp-field="reason" maxlength="2000" placeholder="Ví dụ: đã xem CV, chuyển sang phỏng vấn…" ${s.busy?'disabled':''}>${esc(s.reason)}</textarea></label></div><div class="pp-toolbar"><button type="submit" class="ev-button" ${s.busy?'disabled':''}>${s.busy?'Đang lưu…':'Lưu thông tin'}</button></div></form><p class="pp-muted">Cập nhật nội bộ, không gửi thông báo cho ứng viên. Có thể đổi lại trạng thái khi ghi rõ lý do.</p></section><section class="pp-panel"><h3>Ghi chú nội bộ</h3><form data-pp-note-form><textarea class="pp-note" data-pp-field="note" maxlength="2000" placeholder="Ghi nhận việc cần làm hoặc nội dung trao đổi nội bộ…" ${s.busy?'disabled':''}>${esc(s.note)}</textarea><div class="pp-toolbar"><button type="submit" class="ev-button" ${s.busy?'disabled':''}>Thêm ghi chú</button></div></form></section><section class="pp-panel"><div class="pp-detail-state"><h3>Lịch sử thao tác</h3><span class="pp-muted">${d.event_count} thao tác</span></div>${d.event_count>200?'<p class="pp-muted">Đang hiển thị 200 thao tác gần nhất.</p>':''}<ol class="pp-timeline"><li><strong>Đã nhận hồ sơ</strong><p class="pp-muted">${esc(date(d.applied_at))}</p></li>${d.events.map(e=>`<li><strong>${esc(eventText(e))}</strong><p class="pp-muted">${esc(e.actor_name)} · ${esc(date(e.created_at))}</p><div class="pp-reason">${esc(e.reason)}</div></li>`).join('')}</ol></section>`:''}</div>`;}
  async function load(){s.loading=true;s.error='';render();try{const d=await request(`/applications/${id}/process`);if(live())accept(d);}catch(e){s.error=e.message;}finally{s.loading=false;render();}}
  root.oninput=root.onchange=e=>{if(e.target.dataset.ppField)s[e.target.dataset.ppField]=e.target.value;};
  root.onclick=e=>{const action=e.target.closest('[data-pp-action]')?.dataset.ppAction;if(s.busy)return;if(action==='reload')load();};
  root.onsubmit=async e=>{e.preventDefault();if(s.busy||!s.data)return;const form=e.target;s.busy=true;s.error='';s.notice='';render();try{
   if(form.matches('[data-pp-process-form]')){if(s.reason.trim().length<5)throw Error('Hãy ghi lý do có ít nhất 5 ký tự.');const d=await request(`/applications/${id}/process`,{method:'PATCH',body:JSON.stringify({expected_version:s.data.version,stage:s.stage,reason:s.reason.trim()})});accept(d);s.reason='';s.notice='Đã lưu thông tin và lịch sử thao tác.';onChanged?.();}
   if(form.matches('[data-pp-note-form]')){if(!s.note.trim())throw Error('Hãy nhập ghi chú.');const d=await request(`/applications/${id}/process/notes`,{method:'POST',body:JSON.stringify({note:s.note.trim()})});const edited=s.stage!==s.data.stage||!!s.reason.trim();if(edited){s.data.events=d.events;s.data.event_count=d.event_count;}else accept(d);s.note='';s.notice='Đã thêm ghi chú vào lịch sử.';}
  }catch(e){s.error=e.message;}finally{s.busy=false;render();}};
  render();load();return {dispose(){s.disposed=true;}};
 }
 window.SkillGapPipeline={mountList,mountDetail};
})();

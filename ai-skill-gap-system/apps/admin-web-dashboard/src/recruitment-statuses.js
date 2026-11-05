/* Single shared label/color/icon source for employer and worker delivery UIs. */
(function () {
  const application = {
    applied: {label:'Mới nộp',icon:'○',bg:'#e2e8f0',fg:'#334155'},
    acknowledged: {label:'Đã xác nhận hồ sơ',icon:'✓',bg:'#dbeafe',fg:'#1e40af'},
    invited: {label:'Đã mời phỏng vấn',icon:'↗',bg:'#ede9fe',fg:'#5b21b6'},
    selected: {label:'Đã chọn (nội bộ)',icon:'◆',bg:'#e4e4e7',fg:'#3f3f46'}
  };
  const delivery = {
    queued: {label:'Chờ gửi',icon:'◷',bg:'#e2e8f0',fg:'#334155'},
    sending: {label:'Đang gửi',icon:'↻',bg:'#e0f2fe',fg:'#075985'},
    sent: {label:'Đã gửi',icon:'✓',bg:'#dcfce7',fg:'#166534'},
    read: {label:'Đã đọc',icon:'👁',bg:'#ccfbf1',fg:'#115e59'},
    failed: {label:'Thất bại',icon:'!',bg:'#fee2e2',fg:'#991b1b'},
    unknown: {label:'Chưa xác định',icon:'?',bg:'#ffedd5',fg:'#9a3412'},
    missing_contact: {label:'Chưa gửi - thiếu liên hệ',icon:'⚠',bg:'#fef9c3',fg:'#854d0e'},
    none: {label:'Chưa có lần gửi',icon:'—',bg:'#f1f5f9',fg:'#475569'}
  };
  const batch = {processing:'Đang xử lý',completed:'Đã xử lý xong',completed_with_errors:'Còn mục cần xử lý'};
  const evidence = {
    supported:{label:'Có dẫn chứng trong CV',icon:'✓',bg:'#dcfce7',fg:'#166534'},
    not_found:{label:'Chưa thấy dẫn chứng',icon:'—',bg:'#f1f5f9',fg:'#475569'},
    needs_review:{label:'Cần người kiểm tra',icon:'!',bg:'#fef3c7',fg:'#92400e'},
    unreadable:{label:'Chưa đọc được',icon:'?',bg:'#fef3c7',fg:'#92400e'}
  };
  const actions = {acknowledge:'Xác nhận hồ sơ',invite:'Mời phỏng vấn'};
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const chip=(kind,state,channel)=>{
    const entry=(kind==='application'?application:kind==='evidence'?evidence:delivery)[state]||{label:String(state),icon:'○',bg:'#e2e8f0',fg:'#334155'};
    const tip=kind==='delivery'&&channel==='email'&&state==='sent'?'Máy chủ thư đã nhận yêu cầu; chưa chắc thư đã đến hộp thư người nhận.':entry.label;
    return `<span class="recruitment-chip" title="${escape(tip)}" style="display:inline-flex;align-items:center;gap:5px;padding:4px 9px;border-radius:999px;font-size:12px;font-weight:700;background:${entry.bg};color:${entry.fg}"><span ${state==='sending'?'class="delivery-spin"':''}>${entry.icon}</span>${escape(entry.label)}</span>`;
  };
  const date=value=>value?new Date(/(?:Z|[+-]\d\d:\d\d)$/.test(value)?value:value+'Z').toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'}):'';
  window.RecruitmentStatuses={application,delivery,evidence,batch,actions,chip,date};
})();

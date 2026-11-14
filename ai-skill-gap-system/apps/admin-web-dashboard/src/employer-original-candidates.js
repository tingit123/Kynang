/* Read-only original mock list, recovered from Kynang-Loc.zip for UI review. */
(function () {
  const candidates = [
    {id:1,name:'Trần Thị Bích Ngọc',email:'ngoc.tran@email.com',date:'15/10',title:'Sinh viên CNTT năm 4 · Đại học Cần Thơ',skills:['Python','SQL','FastAPI','Git','Docker']},
    {id:2,name:'Nguyễn Văn An',email:'an.nguyen@email.com',date:'14/10',title:'Sinh viên CNTT năm 4 · Đại học Cần Thơ',skills:['Python','SQL','Git','REST API']},
    {id:3,name:'Lê Minh Quân',email:'quan.le@email.com',date:'14/10',title:'Kỹ sư phần mềm mới tốt nghiệp · Cần Thơ',skills:['Python','Git','Linux']},
    {id:4,name:'Phạm Gia Hân',email:'han.pham@email.com',date:'13/10',title:'Sinh viên năm 3 · ĐH FPT Cần Thơ',skills:['Git','HTML/CSS']}
  ];
  function html(selectedId) {
    const current=candidates.find(c=>c.id===selectedId)||candidates[1];
    return `<style>
      .original-candidates{color:#0f172a;max-width:1150px;margin:auto;line-height:1.6}
      .original-candidates h1{font-size:30px;font-weight:900}.original-candidates h2{font-size:23px;font-weight:800}
      .original-notice{margin:18px 0;padding:14px 18px;border:1px solid #99f6e4;background:#f0fdfa;border-radius:14px;color:#115e59;font-size:13px}
      .original-nav{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.original-nav button{padding:10px 18px;border-radius:999px;border:1px solid #0d5f57;background:white;color:#0d5f57;font:inherit;font-weight:700;cursor:pointer}
      .original-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:28px;align-items:start;margin:24px 0}
      .original-card{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:18px 20px;overflow-wrap:anywhere}.original-card+ .original-card{margin-top:12px}
      button.original-card{width:100%;text-align:left;color:inherit;font:inherit;cursor:pointer}.original-card[aria-pressed=true]{border:2px solid #0d5f57;background:#f0fdfa}
      .original-muted{color:#64748b;font-size:13px}.original-label{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:8px;background:#e2e8f0;color:#334155;margin-left:6px}
      .original-skills{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.original-skills span{padding:5px 12px;background:#f0fdfa;color:#115e59;border-radius:999px;font-size:12px;font-weight:700}
      #employerPortalLayout:has(.original-candidates) .emp-main-content{min-width:0}
      @media(max-width:850px){.original-grid{grid-template-columns:minmax(0,1fr)}}
      @media(max-width:650px){#employerPortalLayout:has(.original-candidates){flex-direction:column}#employerPortalLayout:has(.original-candidates) .emp-sidebar{width:100%;height:auto;position:relative}#employerPortalLayout:has(.original-candidates) .emp-sidebar-nav{flex-direction:row;overflow:auto;padding:8px}#employerPortalLayout:has(.original-candidates) .emp-nav-item{white-space:nowrap}#employerPortalLayout:has(.original-candidates) .emp-main-content{padding:20px 14px;width:100%}}
    </style><div class="original-candidates"><h1>Quản lý ứng viên</h1>
      <p class="original-muted">Xem lại danh sách ứng viên của giao diện ban đầu.</p>
      <div class="original-nav"><button type="button" data-action="original-tab" aria-pressed="true">Danh sách gốc (mẫu)</button><button type="button" data-action="evidence-tab">Hồ sơ và dẫn chứng</button><button type="button" data-action="quick-tab">Lọc hồ sơ và gửi</button></div>
      <div class="original-notice"><strong>Dữ liệu mẫu từ giao diện gốc.</strong> Danh sách này dùng để xem lại bố cục và thông tin mẫu, chưa xác minh năng lực thực tế. Hồ sơ lưu trên hệ thống nằm ở tab “Hồ sơ và dẫn chứng”.</div>
      <p><strong>Python Backend Developer</strong> <span class="original-label">4 hồ sơ mẫu</span></p>
      <div class="original-grid"><section><h2 style="font-size:17px;margin-bottom:14px">Ứng viên</h2>
        ${candidates.map(c=>`<button type="button" class="original-card" data-original-candidate="${c.id}" aria-pressed="${current.id===c.id}"><strong>${c.name}</strong><span class="original-label">Hồ sơ mẫu</span><div class="original-muted">${c.email}</div><div class="original-muted">Ngày trong bản mẫu: ${c.date}</div></button>`).join('')}
      </section><section class="original-card" aria-label="Chi tiết ứng viên mẫu"><p style="font-size:11px;font-weight:800;color:#0d5f57">THÔNG TIN BẢN MẪU GỐC</p><h2>${current.name}</h2><p class="original-muted">${current.title}</p><p class="original-muted">${current.email}</p><hr style="border:0;border-top:1px solid #e2e8f0;margin:22px 0"><h3 style="font-size:14px;font-weight:800">Kỹ năng ghi trong bản mẫu</h3><div class="original-skills">${current.skills.map(skill=>`<span>${skill}</span>`).join('')}</div><p class="original-muted" style="margin-top:20px">Thông tin kỹ năng được giữ từ bản giao diện cũ; chưa có dẫn chứng CV trong bản xem lại này.</p></section></div>
    </div>`;
  }
  window.SkillGapOriginalCandidates={html};
})();

(function(){
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const api=`http://${location.hostname||'localhost'}:8000/api`;
 async function request(path,options={}){
  const token=localStorage.getItem('access_token')||localStorage.getItem('token');
  const config={credentials:'include',...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`} : {})}};
  let response=await fetch(api+path,config);if(response.status===401&&token)response=await fetch(api+path,{...config,credentials:'omit'});
  if(!response.ok)throw Error(response.status===401?'Hãy đăng nhập để xem thông báo.':'Không tải được thông báo. Thử lại.');return response.json();
 }
 function setBadge(count){document.querySelectorAll('[data-worker-unread]').forEach(e=>{e.textContent=String(count);e.hidden=count===0;});}
 async function refreshBadge(){try{const d=await request('/me/notifications');setBadge(d.unread_count);}catch(_){document.querySelectorAll('[data-worker-unread]').forEach(e=>e.hidden=true);}}
 function mount(root){
  let data=null,error='',loading=true,opened=null,disposed=false;
  function render(){if(disposed||!root.isConnected)return;root.innerHTML=`<section style="max-width:900px;margin:auto;background:#fff;color:#0f172a;border:1px solid #e2e8f0;border-radius:18px;padding:24px"><h1 style="font-size:26px;font-weight:900">Thông báo</h1><p>${data?data.unread_count+' chưa đọc':''}</p><button type="button" style="padding:9px 16px;border:1px solid #0d5f57;border-radius:999px;background:#f0fdfa;color:#0d5f57;font:inherit;font-weight:700;cursor:pointer" data-worker-reload>Tải lại</button>${loading?'<p role="status">Đang tải thông báo…</p>':''}${error?`<p role="alert" style="color:#b91c1c">${esc(error)}</p>`:''}${data&&!data.notifications.length?'<p>Chưa có thông báo.</p>':''}${data?data.notifications.map(n=>`<article style="border:1px solid ${n.read_at?'#e2e8f0':'#93c5fd'};background:${n.read_at?'#fff':'#eff6ff'};border-radius:12px;padding:16px;margin:12px 0"><button type="button" data-worker-open="${n.id}" style="background:none;border:0;color:#0f172a;text-align:left;font:inherit;cursor:pointer"><strong>${esc(n.title)}</strong></button><div>${window.RecruitmentStatuses.chip('delivery',n.read_at?'read':'sent','in_app')} <span style="font-size:12px;color:#64748b">${esc(window.RecruitmentStatuses.date(n.created_at))}</span></div>${n.simulated?'<p>Chế độ giả lập (chỉ để thử giao diện)</p>':''}${opened===n.id?`<p style="white-space:pre-wrap;margin-top:12px">${esc(n.body)}</p>`:'<p style="font-size:13px;color:#64748b">Bấm tiêu đề để mở và đánh dấu đã đọc.</p>'}</article>`).join(''):''}</section>`;}
  async function load(){loading=true;error='';render();try{data=await request('/me/notifications');setBadge(data.unread_count);}catch(e){data=null;error=e.message;}finally{loading=false;render();}}
  root.onclick=async e=>{if(e.target.closest('[data-worker-reload]')){await load();return;}const b=e.target.closest('[data-worker-open]');if(b){const id=Number(b.dataset.workerOpen);try{await request('/me/notifications/'+id+'/read',{method:'POST'});opened=id;await load();}catch(e){error=e.message;render();}}};
  load();return()=>{disposed=true;root.onclick=null;};
 }
 function syncHeader(){const main=document.getElementById('main'),nav=document.getElementById('publicNavbar');if(main&&nav)main.style.setProperty('padding-top',(nav.getBoundingClientRect().height+24)+'px','important');}
 function mountPage(main){document.querySelectorAll('#main .page').forEach(e=>e.classList.remove('active'));let root=document.getElementById('page-notifications');if(!root){root=document.createElement('div');root.id='page-notifications';root.className='page';main.appendChild(root);}root.classList.add('active');syncHeader();return mount(root);}
 window.SkillGapWorkerNotifications={mount,mountPage,refreshBadge};
 window.addEventListener('DOMContentLoaded',()=>{setTimeout(refreshBadge,1200);});
 window.addEventListener('focus',refreshBadge);
 window.addEventListener('resize',()=>{if(location.hash==='#/notifications')syncHeader();});
})();

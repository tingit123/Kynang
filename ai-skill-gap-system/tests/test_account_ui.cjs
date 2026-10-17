// Exercise the actual account-management script without a browser or live API.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {value:'', textContent:'', innerHTML:'', classList:{add(){},remove(){}}, reset(){}});
  return elements.get(id);
}
const requests = [];
const accounts = [
  {id:1, full_name:'Admin', email:'admin@example.com', role:'admin', is_active:true},
  {id:2, full_name:'<img src=x onerror=alert(1)>', email:'worker@example.com', role:'candidate', is_active:true, company_name:'Company'}
];
const context = vm.createContext({
  console, API_BASE:'http://test', currentUser:{id:1,role:'admin'},
  document:{getElementById:element, createElement:()=>({setAttribute(){},style:{},remove(){}}),body:{appendChild(){}}},
  getAuthHeaders:()=>({'Authorization':'Bearer test','Content-Type':'application/json'}),
  localStorage:{setItem(){}}, updateUserUI(){}, confirm:()=>true, setTimeout(){},
  fetch:async (url, options) => {
    requests.push({url,options});
    return {ok:true,json:async()=>options.method ? {id:2,...JSON.parse(options.body || '{}')} : accounts};
  }
});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../apps/admin-web-dashboard/account-management.js'),'utf8'),context);
(async () => {
  element('adminRoleFilter').value = 'all';
  element('adminStatusFilter').value = 'all';
  await context.renderAdmin();
  assert.equal(element('accountCount-candidate').textContent,1);
  assert.ok(element('adminUsersBody').innerHTML.includes('&lt;img'));
  assert.ok(!element('adminUsersBody').innerHTML.includes('<img'));
  assert.equal(requests[0].options.headers.Authorization,'Bearer test');
  element('adminUserSearch').value = 'worker';
  context.filterAdminUsers();
  assert.equal(element('accountCountBadge').textContent,'1 tài khoản');
  context.openEditUserModal(2);
  assert.equal(element('accountFormEmail').value,'worker@example.com');
  assert.equal(element('accountFormPassword').required,false);
  await context.toggleUserStatus(2);
  const mutation = requests.find(r => r.options.method === 'PUT');
  assert.equal(JSON.parse(mutation.options.body).is_active,false);
  context.currentUser = {id:0,role:'guest',is_guest:true};
  const count = requests.length;
  await context.renderAdmin();
  assert.equal(requests.length,count);
  console.log('Account UI: PASS (load, filters, escaping, edit, lock, auth headers, guest guard)');
})().catch(error => { console.error(error); process.exitCode=1; });

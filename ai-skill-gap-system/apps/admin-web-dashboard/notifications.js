let notificationPageItems = [];
let notificationPageTotal = 0;
let notificationBellTrigger = null;
let notificationPageLoading = false;

function notificationSeenKey() { return `skillgap_notifications_seen_${currentUser?.id || 'guest'}`; }
function notificationLastSeen() { try { return Number(localStorage.getItem(notificationSeenKey())) || 0; } catch { return 0; } }
function notificationMarkSeen(items) {
  const latest = Math.max(notificationLastSeen(), ...items.map(n => n.id));
  try { localStorage.setItem(notificationSeenKey(), String(latest)); } catch {}
  document.querySelectorAll('[data-notification-dot]').forEach(dot => dot.hidden = true);
  document.querySelectorAll('[data-notification-bell]').forEach(button => button.setAttribute('aria-label','Xem thông báo'));
}

function notificationCards(items) {
  return items.map(item => {
    const date = new Date(item.created_at);
    const displayDate = date.toLocaleString('vi-VN', {timeZone:'Asia/Ho_Chi_Minh',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'});
    return `<article class="notification-item"><time datetime="${flowEscape(item.created_at)}">${flowEscape(displayDate)}</time><h3>${flowEscape(item.title)}</h3><p>${flowEscape(item.content)}</p></article>`;
  }).join('');
}

async function refreshNotificationBell() {
  try {
    const data = await flowRequest('notifications/?limit=1');
    const hasNew = data.items.some(item => item.id > notificationLastSeen());
    document.querySelectorAll('[data-notification-dot]').forEach(dot => dot.hidden = !hasNew);
    document.querySelectorAll('[data-notification-bell]').forEach(button => button.setAttribute('aria-label',hasNew ? 'Xem thông báo, có thông báo mới' : 'Xem thông báo'));
  } catch { /* Keep the bell usable; opening it exposes errors and a retry. */ }
}

function closeNotificationPopover(restoreFocus = false) {
  document.getElementById('notificationPopover').hidden = true;
  document.querySelectorAll('[data-notification-bell]').forEach(button => button.setAttribute('aria-expanded','false'));
  if (restoreFocus) notificationBellTrigger?.focus();
}

async function toggleNotificationPopover(event) {
  event.stopPropagation();
  const popover = document.getElementById('notificationPopover');
  if (!popover.hidden) { closeNotificationPopover(true); return; }
  notificationBellTrigger = event.currentTarget;
  popover.hidden = false;
  notificationBellTrigger.setAttribute('aria-expanded','true');
  popover.querySelector('button').focus();
  await loadNotificationPopover();
}

async function loadNotificationPopover() {
  const list = document.getElementById('notificationPopoverList');
  list.innerHTML = '<p class="notification-empty" role="status">Đang tải thông báo...</p>';
  try {
    const data = await flowRequest('notifications/?limit=10');
    list.innerHTML = notificationCards(data.items) || '<p class="notification-empty">Chưa có thông báo nào.<br>Thông báo từ Admin sẽ xuất hiện tại đây.</p>';
    if (!document.getElementById('notificationPopover').hidden) notificationMarkSeen(data.items);
  } catch (error) {
    list.innerHTML = `<div class="notification-empty"><p>${flowEscape(error.message)}</p><button class="action-btn" onclick="loadNotificationPopover()">Thử lại</button></div>`;
  }
}

function openNotificationsPage() {
  closeNotificationPopover();
  const role = currentUser?.role;
  navigate(['admin','employer','provider'].includes(role) ? `/${role}/notifications` : '/notifications');
}

function notificationSyncRole() {
  const compose = document.getElementById('notificationCompose');
  if (compose) {
    const admin = currentUser?.role === 'admin' && !currentUser.is_guest && !!(localStorage.getItem('access_token') || localStorage.getItem('token'));
    compose.hidden = !admin;
    document.getElementById('notificationLayout').classList.toggle('viewer', !admin);
  }
  refreshNotificationBell();
}

async function renderNotificationsPage() {
  closeNotificationPopover();
  notificationSyncRole();
  notificationPageItems = [];
  notificationPageTotal = 0;
  notificationPageLoading = false;
  document.getElementById('notificationsFeed').innerHTML = '<p class="notification-empty" role="status">Đang tải thông báo...</p>';
  document.getElementById('notificationsMore').hidden = true;
  await loadNotificationsPage();
}

async function loadNotificationsPage() {
  if (notificationPageLoading) return;
  notificationPageLoading = true;
  const more = document.getElementById('notificationsMore'); more.disabled = true;
  const errorBox = document.getElementById('notificationListError'); errorBox.textContent = '';
  try {
    const data = await flowRequest(`notifications/?limit=20&offset=${notificationPageItems.length}`);
    notificationPageItems.push(...data.items.filter(item => !notificationPageItems.some(existing => existing.id === item.id)));
    notificationPageTotal = data.total;
    document.getElementById('notificationsFeed').innerHTML = notificationCards(notificationPageItems) || '<p class="notification-empty">Chưa có thông báo nào được đăng.</p>';
    document.getElementById('notificationTotal').textContent = `${notificationPageTotal} thông báo`;
    more.hidden = notificationPageItems.length >= notificationPageTotal;
    more.textContent = 'Xem thêm thông báo';
    notificationMarkSeen(notificationPageItems);
  } catch (error) {
    if (!notificationPageItems.length) document.getElementById('notificationsFeed').innerHTML = '';
    errorBox.textContent = error.message;
    more.hidden = false; more.textContent = 'Thử tải lại';
  } finally { notificationPageLoading = false; more.disabled = false; }
}

async function publishNotification(event) {
  event.preventDefault();
  if (!flowAllowed(['admin'])) return;
  const title = document.getElementById('notificationTitle').value.trim();
  const content = document.getElementById('notificationContent').value.trim();
  const errorBox = document.getElementById('notificationFormError'); errorBox.textContent = '';
  if (!title || !content) { errorBox.textContent = 'Vui lòng nhập tiêu đề và nội dung thông báo.'; return; }
  const button = document.getElementById('publishNotificationButton'); button.disabled = true; button.textContent = 'Đang đăng...';
  try {
    await flowRequest('notifications/',{method:'POST',body:JSON.stringify({title,content})});
    document.getElementById('notificationForm').reset();
    await renderNotificationsPage();
    showToast('Đã đăng thông báo đến người dùng.');
  } catch (error) { errorBox.textContent = error.message; }
  finally { button.disabled = false; button.textContent = 'Đăng thông báo'; }
}

document.addEventListener('click', event => {
  if (!event.target.closest('#notificationPopover, [data-notification-bell]')) closeNotificationPopover();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !document.getElementById('notificationPopover').hidden) closeNotificationPopover(true);
});
window.addEventListener('DOMContentLoaded', refreshNotificationBell);
window.addEventListener('focus', refreshNotificationBell);

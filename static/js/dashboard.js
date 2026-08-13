const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const renderRows = (items, formatter) => items.length ? items.map(formatter).join('') : '<p class="empty">No records yet.</p>';
async function loadDashboard() {
  const response = await fetch('/api/dashboard/summary', {credentials: 'same-origin'});
  if (!response.ok) { window.location.assign('/login'); return; }
  const data = await response.json();
  document.querySelector('#total-events').textContent = data.total_events;
  document.querySelector('#open-alerts').textContent = data.open_alerts;
  document.querySelector('#critical-events').textContent = data.critical_events;
  document.querySelector('#risk-breakdown').innerHTML = Object.entries(data.risk_breakdown)
    .map(([level, count]) => `<span class="badge ${level}">${escapeHtml(level)}: ${count}</span>`).join('');
  document.querySelector('#recent-events').innerHTML = renderRows(data.recent_events,
    event => `<div class="row"><div><strong>${escapeHtml(event.event_type)}</strong><small>${escapeHtml(event.created_at)}</small></div><span class="badge ${escapeHtml(event.severity)}">${event.risk_score}/100 · ${escapeHtml(event.severity)}</span></div>`);
  document.querySelector('#recent-alerts').innerHTML = renderRows(data.recent_open_alerts,
    alert => `<div class="row"><div><strong>${escapeHtml(alert.event_type)}</strong><small>Alert #${alert.id}</small></div><span class="badge ${escapeHtml(alert.severity)}">${alert.status}</span></div>`);
}
document.querySelector('#logout').addEventListener('click', async () => {
  const tokenResponse = await fetch('/api/csrf-token', {credentials: 'same-origin'});
  const {csrf_token: csrfToken} = await tokenResponse.json();
  await fetch('/auth/logout', {method: 'POST', headers: {'X-CSRFToken': csrfToken}, credentials: 'same-origin'});
  window.location.assign('/login');
});
loadDashboard();
setInterval(loadDashboard, 30000);

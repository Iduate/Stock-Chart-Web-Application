// Global Auth UI helper
// - Reads user from localStorage and updates header on all pages
// - Provides a logout flow that clears storage and optionally notifies backend

(function(){
  const STATE = {
    user: null,
    accessToken: null,
    refreshToken: null,
    cookieMode: false // frontend hint; backend may also set HttpOnly cookies
  };

  function readLocalAuth() {
    try {
      const u = localStorage.getItem('user');
      STATE.user = u ? JSON.parse(u) : null;
    } catch {}
    STATE.accessToken = localStorage.getItem('access_token') || localStorage.getItem('access');
    STATE.refreshToken = localStorage.getItem('refresh_token') || localStorage.getItem('refresh');
  }

  function getCSRFToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function createUserChip() {
    const user = STATE.user || {};
    const name = user.username || user.first_name || user.email || 'User';
    const initials = (name || '?').toString().trim().split(/\s+/).map(s => s[0]).slice(0,2).join('').toUpperCase();
    const chip = document.createElement('div');
    chip.className = 'user-chip';
    chip.style.display = 'flex';
    chip.style.alignItems = 'center';
    chip.style.gap = '10px';

    const avatar = document.createElement('span');
    avatar.className = 'avatar';
    avatar.style.width = '32px';
    avatar.style.height = '32px';
    avatar.style.borderRadius = '50%';
    avatar.style.background = '#0A84FF';
    avatar.style.display = 'inline-flex';
    avatar.style.alignItems = 'center';
    avatar.style.justifyContent = 'center';
    avatar.style.fontWeight = '700';
    avatar.style.color = 'white';
    avatar.textContent = initials || 'U';

    const label = document.createElement('span');
    label.className = 'user-name';
    label.textContent = name;

    const logoutBtn = document.createElement('button');
    logoutBtn.className = 'ghost-btn';
    logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> 로그아웃';
    logoutBtn.addEventListener('click', logout);

    chip.appendChild(avatar);
    chip.appendChild(label);
    chip.appendChild(logoutBtn);
    return chip;
  }

  function replaceHeaderActionsPrediction() {
    const actions = document.querySelector('.prediction-header .header-actions');
    if (!actions) return false;
    actions.innerHTML = '';
    actions.appendChild(createUserChip());
    return true;
  }

  function injectIntoTopActions() {
    const actions = document.querySelector('.dashboard-top-bar .top-actions');
    if (!actions) return false;
    // Avoid duplicating
    if (actions.querySelector('.user-chip')) return true;
    const sep = document.createElement('div');
    sep.style.width = '1px';
    sep.style.height = '28px';
    sep.style.background = 'rgba(255,255,255,0.1)';
    sep.style.margin = '0 8px';
    actions.appendChild(sep);
    actions.appendChild(createUserChip());
    return true;
  }

  async function notifyBackendLogout() {
    // Prefer JWT logout endpoint
    const headers = { 'Content-Type': 'application/json' };
    if (STATE.accessToken) headers['Authorization'] = 'Bearer ' + STATE.accessToken;
    const csrf = getCSRFToken();
    if (csrf) headers['X-CSRFToken'] = csrf;

    try {
      const res1 = await fetch('/api/auth/social/logout/', { method: 'POST', headers, body: JSON.stringify({}) });
      if (res1.ok) return; // done
    } catch {}
    // Fallback generic logout
    try {
      await fetch('/api/auth/logout/', { method: 'POST', headers, body: JSON.stringify({}) });
    } catch {}
  }

  async function logout(e) {
    if (e && e.preventDefault) e.preventDefault();
    try { await notifyBackendLogout(); } catch {}
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('user');
    } catch {}
    // Best effort: also clear potential non-HttpOnly cookies set by older flows
    try {
      document.cookie = 'access=; Max-Age=0; path=/';
      document.cookie = 'refresh=; Max-Age=0; path=/';
      document.cookie = 'sc_access=; Max-Age=0; path=/';
      document.cookie = 'sc_refresh=; Max-Age=0; path=/';
    } catch {}
    window.location.reload();
  }

  function render() {
    readLocalAuth();
    if (!STATE.user) return; // not logged in
    // Try specific page header first
    if (replaceHeaderActionsPrediction()) return;
    // Else general top bar injection
    injectIntoTopActions();
  }

  // Expose minimal API
  window.AppAuth = window.AppAuth || {};
  window.AppAuth.logout = logout;
  window.AppAuth.readLocalAuth = readLocalAuth;

  document.addEventListener('DOMContentLoaded', render);
})();

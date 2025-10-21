// Partner portal frontend logic
(function(){
  const API_ROOT = '/api/affiliates';
  const state = {
    token: null,
    csrf: null,
    partner: null,
    lastDashboard: null,
    cookieAuth: false,
    loadingPartner: false,
  };
  const modalState = { overlay: null };
  const LOGIN_BUTTON_HTML = '<i class="fas fa-sign-in-alt"></i> 로그인';

  const els = {};
  const SECTION_IDS = ['authNotice', 'applicationSection', 'pendingSection', 'dashboardSection'];

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  async function init(){
    cacheElements();
    bindStaticHandlers();
    readAuthState();
    try {
      await probeAuth();
    } catch (_) {}
    if (!state.token && !state.cookieAuth){
      showSection('authNotice');
      return;
    }
    loadPartnerState();
  }

  function flashSection(id){
    const target = document.getElementById(id);
    if (!target) return;
    target.classList.remove('flash-highlight');
    void target.offsetWidth;
    target.classList.add('flash-highlight');
    setTimeout(() => {
      target.classList.remove('flash-highlight');
    }, 900);
  }

  function cacheElements(){
    SECTION_IDS.forEach(id => {
      els[id] = document.getElementById(id);
    });
    els.applicationForm = document.getElementById('partnerApplicationForm');
    els.applicationFeedback = document.getElementById('applicationFeedback');
    els.dashboardFeedback = document.getElementById('dashboardFeedback');
    els.partnerStatusBadge = document.getElementById('partnerStatusBadge');
    els.summaryPartnerCode = document.getElementById('summaryPartnerCode');
    els.summaryClicks = document.getElementById('summaryClicks');
    els.summaryConversions = document.getElementById('summaryConversions');
    els.summaryPending = document.getElementById('summaryPending');
    els.copyPartnerCode = document.getElementById('copyPartnerCode');
    els.requestPayout = document.getElementById('requestPayout');
    els.refreshDashboard = document.getElementById('refreshDashboard');
    els.toggleLinkForm = document.getElementById('toggleLinkForm');
    els.newLinkForm = document.getElementById('newLinkForm');
    els.linksTableBody = document.querySelector('#linksTable tbody');
    els.commissionTableBody = document.querySelector('#commissionTable tbody');
    els.performanceTableBody = document.querySelector('#performanceTable tbody');
    els.materialsGrid = document.getElementById('materialsGrid');
    els.openApplication = document.getElementById('openApplication');
    els.openDashboard = document.getElementById('openDashboard');
    els.openPortalTop = document.getElementById('openPortalTop');
    els.statReferrals = document.getElementById('statReferrals');
    els.statMonthlyCommission = document.getElementById('statMonthlyCommission');
    els.statTotalCommission = document.getElementById('statTotalCommission');
    els.statConversionRate = document.getElementById('statConversionRate');
    els.quickCopyLink = document.getElementById('quickCopyLink');
    els.quickMaterials = document.getElementById('quickMaterials');
    els.quickCommissions = document.getElementById('quickCommissions');
  }

  function bindStaticHandlers(){
    if (els.applicationForm){
      els.applicationForm.addEventListener('submit', onSubmitApplication);
    }
    if (els.copyPartnerCode){
      els.copyPartnerCode.addEventListener('click', copyPartnerCode);
    }
    if (els.requestPayout){
      els.requestPayout.addEventListener('click', onRequestPayout);
    }
    if (els.refreshDashboard){
      els.refreshDashboard.addEventListener('click', () => loadDashboard(true));
    }
    if (els.toggleLinkForm){
      els.toggleLinkForm.addEventListener('click', toggleLinkForm);
    }
    if (els.newLinkForm){
      els.newLinkForm.addEventListener('submit', onCreateLink);
    }
    if (els.openApplication){
      els.openApplication.addEventListener('click', onHeroApplication);
    }
    if (els.openDashboard){
      els.openDashboard.addEventListener('click', onHeroDashboard);
    }
    if (els.openPortalTop){
      els.openPortalTop.addEventListener('click', onHeroDashboard);
    }
    if (els.quickCopyLink){
      els.quickCopyLink.addEventListener('click', copyDefaultLink);
    }
    if (els.quickMaterials){
      els.quickMaterials.addEventListener('click', () => goToDashboardPanel('materialPanel'));
    }
    if (els.quickCommissions){
      els.quickCommissions.addEventListener('click', () => goToDashboardPanel('commissionPanel'));
    }
  }

  function readAuthState(){
    try {
  state.token = localStorage.getItem('access_token') || localStorage.getItem('access') ||
        localStorage.getItem('sc_access') || localStorage.getItem('sc_access_token') ||
        localStorage.getItem('token');
      state.csrf = getCSRFToken();
      // Detect possible cookie-based session (HttpOnly JWT/sessionid)
      const hasSession = /(?:^|; )sessionid=/.test(document.cookie) ||
                         /(?:^|; )sc_session=/.test(document.cookie) ||
                         /(?:^|; )access=/.test(document.cookie) ||
                         /(?:^|; )sc_access=/.test(document.cookie);
      if (!state.token && hasSession) {
        state.cookieAuth = true;
      }
    } catch (err) {
      state.token = null;
    }
  }

  function getCSRFToken(){
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
  }

  async function probeAuth(){
    // Quickly determine if the user is authenticated via token or session
    const headers = {};
    if (state.token) headers['Authorization'] = 'Bearer ' + state.token;
    const csrf = state.csrf || getCSRFToken();
    if (csrf) headers['X-CSRFToken'] = csrf;
    try {
      const res = await fetch('/api/auth/verify/', {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({}),
      });
      if (res.ok){
        // If verify passed without a token, we are in cookie mode
        if (!state.token) state.cookieAuth = true;
        return true;
      }
      // If verify failed and we only had a token, clear it
      if (state.token && res.status === 401){
        try {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
          localStorage.removeItem('sc_access');
          localStorage.removeItem('sc_access_token');
          localStorage.removeItem('token');
        } catch {}
        state.token = null;
        state.cookieAuth = false;
      }
      return false;
    } catch (e){
      return false;
    }
  }

  function showSection(id){
    SECTION_IDS.forEach(sectionId => {
      if (!els[sectionId]) return;
      els[sectionId].style.display = sectionId === id ? 'block' : 'none';
    });
  }

  function setFeedback(el, message, tone){
    if (!el) return;
    el.textContent = message || '';
    if (!message){
      el.style.color = '';
      return;
    }
    if (tone === 'error'){
      el.style.color = '#ff6767';
    } else if (tone === 'info'){
      el.style.color = '#0A84FF';
    } else {
      el.style.color = '#00ffa3';
    }
  }

  function promptLogin(message, feedbackEl){
    showSection('authNotice');
    scrollToSection('authNotice');
    if (feedbackEl && message){
      setFeedback(feedbackEl, message, 'error');
    }
    openLoginModal();
    if (message){
      const overlay = modalState.overlay || document.getElementById('partnerLoginModal');
      const status = overlay?.querySelector('.partner-login-status');
      if (status){
        status.textContent = message;
        status.classList.remove('success');
        status.classList.add('error');
      }
      window.alert(message);
    }
  }

  async function loadPartnerState(){
    if (state.loadingPartner) return;
    state.loadingPartner = true;
    try {
      const partners = await apiGet('/partners/');
      const list = Array.isArray(partners) ? partners : partners?.results;
      const partner = Array.isArray(list) && list.length ? list[0] : null;
      state.partner = partner;
      if (!partner){
        setQuickActionsEnabled(false);
        showSection('applicationSection');
        return;
      }
      updateStatusBadge(partner.status);
      setQuickActionsEnabled(partner.status === 'active');
      if (partner.status === 'pending'){
        showSection('pendingSection');
      } else if (partner.status === 'suspended' || partner.status === 'terminated'){
        showSection('pendingSection');
        setPendingCopy(partner.status);
      } else {
        showSection('dashboardSection');
        loadDashboard();
      }
    } catch (err){
      if (err.status === 401){
        // If we thought we had a cookie session, retry once without Authorization header
        if (state.cookieAuth && state.token){
          const prev = state.token; state.token = null; // force cookie-mode
          try {
            const partners2 = await apiGet('/partners/');
            const list2 = Array.isArray(partners2) ? partners2 : partners2?.results;
            const partner2 = Array.isArray(list2) && list2.length ? list2[0] : null;
            state.partner = partner2;
            if (partner2){
              updateStatusBadge(partner2.status);
              setQuickActionsEnabled(partner2.status === 'active');
              if (partner2.status === 'pending') showSection('pendingSection');
              else if (partner2.status === 'suspended' || partner2.status === 'terminated') { showSection('pendingSection'); setPendingCopy(partner2.status); }
              else { showSection('dashboardSection'); loadDashboard(); }
              return;
            }
          } catch (_) { /* fallthrough */ }
          state.token = prev; // restore
        }
        showSection('authNotice');
        clearState();
        setQuickActionsEnabled(false);
      } else {
        showSection('applicationSection');
        setQuickActionsEnabled(false);
        setFeedback(els.applicationFeedback, '파트너 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.', 'error');
      }
    }
    finally {
      state.loadingPartner = false;
    }
  }

  function updateStatusBadge(status){
    if (!els.partnerStatusBadge) return;
    const labelMap = {
      pending: 'PENDING',
      active: 'ACTIVE',
      suspended: 'SUSPENDED',
      terminated: 'TERMINATED',
    };
    els.partnerStatusBadge.textContent = labelMap[status] || status?.toUpperCase() || '';
    els.partnerStatusBadge.classList.remove('success', 'warning');
    if (status === 'active'){
      els.partnerStatusBadge.classList.add('success');
    } else if (status === 'pending'){
      els.partnerStatusBadge.classList.add('warning');
    }
  }

  function onHeroApplication(){
    if (!state.token && !state.cookieAuth){
      promptLogin('로그인 후 파트너 신청이 가능합니다.', els.applicationFeedback);
      return;
    }
    if (!state.partner && !state.loadingPartner){
      setFeedback(els.applicationFeedback, '상태 확인 중입니다...', 'info');
      loadPartnerState();
      return;
    }
    if (state.partner){
      if (state.partner.status === 'active'){
        scrollToSection('dashboardSection');
      } else {
        scrollToSection('pendingSection');
      }
    } else {
      scrollToSection('applicationSection');
    }
  }

  function onHeroDashboard(){
    if (!state.token && !state.cookieAuth){
      promptLogin('로그인 후 파트너 포털을 이용할 수 있습니다.', els.dashboardFeedback);
      return;
    }
    if (!state.partner && !state.loadingPartner){
      setFeedback(els.dashboardFeedback, '상태 확인 중입니다...', 'info');
      loadPartnerState();
      return;
    }
    if (state.partner && state.partner.status === 'active'){
      scrollToSection('dashboardSection');
    } else if (state.partner) {
      scrollToSection('pendingSection');
    } else {
      scrollToSection('applicationSection');
    }
  }

  function setPendingCopy(status){
    if (!els.pendingSection) return;
    const copy = els.pendingSection.querySelector('.info-banner div p');
    if (!copy) return;
    if (status === 'suspended'){
      copy.textContent = '계정이 일시중지되었습니다. 고객 성공팀과 연결하여 재활성화를 진행하세요.';
    } else if (status === 'terminated'){
      copy.textContent = '파트너 계약이 종료되었습니다. 추가 안내가 필요하면 관리자에게 문의하세요.';
    }
  }

  function clearState(){
    state.partner = null;
    state.lastDashboard = null;
  }

  async function onSubmitApplication(evt){
    evt.preventDefault();
    if (!state.token){
      promptLogin('로그인 후 신청서를 제출할 수 있습니다.', els.applicationFeedback);
      return;
    }
    const form = evt.currentTarget;
    const submitButton = document.getElementById('submitApplication');
    const payload = buildApplicationPayload(form);
    setFeedback(els.applicationFeedback, '제출 중입니다...', 'info');
    if (submitButton) submitButton.disabled = true;
    try {
      await apiPost('/partners/apply/', payload);
      setFeedback(els.applicationFeedback, '신청이 완료되었습니다. 승인까지 최대 1영업일이 소요됩니다.', 'success');
      await loadPartnerState();
    } catch (err){
      setFeedback(els.applicationFeedback, extractErrorMessage(err, '신청 처리 중 문제가 발생했습니다.'), 'error');
    } finally {
      if (submitButton) submitButton.disabled = false;
    }
  }

  function buildApplicationPayload(form){
    const company = form.querySelector('#partnerCompany')?.value.trim();
    const phone = form.querySelector('#partnerPhone')?.value.trim();
    const biz = form.querySelector('#partnerBizReg')?.value.trim();
    const website = form.querySelector('#partnerWebsite')?.value.trim();
    const instagram = form.querySelector('#partnerInstagram')?.value.trim();
    const youtube = form.querySelector('#partnerYoutube')?.value.trim();
    const blog = form.querySelector('#partnerBlog')?.value.trim();
    const bank = form.querySelector('#partnerBank')?.value.trim();
    const account = form.querySelector('#partnerAccount')?.value.trim();
    const holder = form.querySelector('#partnerAccountHolder')?.value.trim();
    const notes = form.querySelector('#partnerNotes')?.value.trim();

    const social_media = {};
    if (instagram) social_media.instagram = instagram;
    if (youtube) social_media.youtube = youtube;
    if (blog) social_media.blog = blog;
    if (notes) social_media.notes = notes;

    const bank_info = {};
    if (bank) bank_info.bank = bank;
    if (account) bank_info.account = account;
    if (holder) bank_info.holder = holder;

    return {
      company_name: company,
      phone_number: phone,
      business_registration: biz,
      website: website,
      social_media,
      bank_info,
    };
  }

  async function loadDashboard(force){
    if (!state.partner) return;
    if (state.partner.status !== 'active') return;
    if (!force && state.loadingDashboard) return;
    state.loadingDashboard = true;
    setFeedback(els.dashboardFeedback, '대시보드를 불러오는 중입니다...', 'info');
    try {
      const [dashboard, links, commissions, performance, materials] = await Promise.all([
        apiGet('/partners/dashboard/'),
        apiGet('/links/'),
        apiGet('/commissions/'),
        apiGet('/partners/performance/'),
        apiGet('/materials/'),
      ]);
      state.lastDashboard = dashboard;
      renderDashboardSummary(dashboard);
      renderLinks(links);
      renderCommissions(commissions);
      renderPerformance(performance);
      renderMaterials(materials);
      setFeedback(els.dashboardFeedback, '', 'success');
    } catch (err){
      setFeedback(els.dashboardFeedback, extractErrorMessage(err, '대시보드 데이터를 불러오지 못했습니다.'), 'error');
    } finally {
      state.loadingDashboard = false;
    }
  }

  function renderDashboardSummary(data){
    if (!data) return;
    const info = data.partner_info || {};
    const stats = data.recent_stats || {};
    if (els.summaryPartnerCode) els.summaryPartnerCode.textContent = info.partner_code || '-';
    if (els.summaryClicks) els.summaryClicks.textContent = formatNumber(stats.clicks_30days);
    if (els.summaryConversions) els.summaryConversions.textContent = formatNumber(stats.conversions_30days);
    if (els.summaryPending) els.summaryPending.textContent = formatCurrency(stats.pending_commission || 0, info.currency || 'KRW');
    if (els.statReferrals) els.statReferrals.textContent = `${formatNumber(info.total_referrals)}명`;
    if (els.statMonthlyCommission) els.statMonthlyCommission.textContent = formatCurrency(stats.this_month_commission || 0, info.currency || 'KRW');
    if (els.statTotalCommission) els.statTotalCommission.textContent = formatCurrency(info.total_commission_earned || 0, info.currency || 'KRW');
    if (els.statConversionRate){
      const rate = stats.conversion_rate != null ? Number(stats.conversion_rate) : null;
      els.statConversionRate.textContent = rate != null && Number.isFinite(rate) ? `${rate.toFixed(2)}%` : '-';
    }
  }

  function renderLinks(data){
    if (!els.linksTableBody) return;
    const list = normalizeList(data);
    els.linksTableBody.innerHTML = '';
    if (!list.length){
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 5;
      cell.textContent = '생성된 추천 링크가 없습니다.';
      row.appendChild(cell);
      els.linksTableBody.appendChild(row);
      return;
    }
    list.forEach(item => {
      const row = document.createElement('tr');
      const nameCell = document.createElement('td');
      nameCell.textContent = item.name;
      const urlCell = document.createElement('td');
      const link = document.createElement('button');
      link.className = 'ghost-btn small';
      link.textContent = '링크 복사';
      link.addEventListener('click', () => copyToClipboard(item.full_url || item.target_url));
      urlCell.appendChild(link);
      const clickCell = document.createElement('td');
      clickCell.textContent = formatNumber(item.click_count);
      const conversionCell = document.createElement('td');
      conversionCell.textContent = formatNumber(item.conversion_count);
      const actionsCell = document.createElement('td');
      const openBtn = document.createElement('a');
      openBtn.href = item.full_url || item.target_url || '#';
      openBtn.target = '_blank';
      openBtn.rel = 'noopener';
      openBtn.className = 'ghost-btn small';
      openBtn.textContent = '열기';
      actionsCell.appendChild(openBtn);
      row.appendChild(nameCell);
      row.appendChild(urlCell);
      row.appendChild(clickCell);
      row.appendChild(conversionCell);
      row.appendChild(actionsCell);
      els.linksTableBody.appendChild(row);
    });
  }

  function renderCommissions(data){
    if (!els.commissionTableBody) return;
    const list = normalizeList(data);
    els.commissionTableBody.innerHTML = '';
    if (!list.length){
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 4;
      cell.textContent = '수수료 내역이 아직 없습니다.';
      row.appendChild(cell);
      els.commissionTableBody.appendChild(row);
      return;
    }
    list.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${formatDate(item.created_at)}</td>
        <td>${translateTransactionType(item.transaction_type)}</td>
        <td>${formatCurrency(item.amount, item.currency)}</td>
        <td>${translateStatus(item.status)}</td>
      `;
      els.commissionTableBody.appendChild(row);
    });
  }

  function renderPerformance(data){
    if (!els.performanceTableBody) return;
    const list = normalizeList(data);
    els.performanceTableBody.innerHTML = '';
    if (!list.length){
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 5;
      cell.textContent = '성과 데이터가 아직 없습니다.';
      row.appendChild(cell);
      els.performanceTableBody.appendChild(row);
      return;
    }
    list.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${item.year}.${String(item.month).padStart(2, '0')}</td>
        <td>${formatNumber(item.total_clicks)}</td>
        <td>${formatNumber(item.conversions)}</td>
        <td>${formatCurrency(item.revenue_generated, 'KRW')}</td>
        <td>${formatCurrency(item.commission_earned, 'KRW')}</td>
      `;
      els.performanceTableBody.appendChild(row);
    });
  }

  function renderMaterials(data){
    if (!els.materialsGrid) return;
    const list = normalizeList(data);
    els.materialsGrid.innerHTML = '';
    if (!list.length){
      const empty = document.createElement('p');
      empty.className = 'form-helper';
      empty.textContent = '등록된 홍보 자료가 없습니다. 담당자에게 요청해주세요.';
      els.materialsGrid.appendChild(empty);
      return;
    }
    list.forEach(item => {
      const card = document.createElement('div');
      card.className = 'material-card';
      const title = document.createElement('h4');
      title.textContent = item.name;
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = `${translateMaterialType(item.material_type)} · 다운로드 ${formatNumber(item.download_count)}`;
      card.appendChild(title);
      card.appendChild(meta);
      if (item.description){
        const desc = document.createElement('p');
        desc.className = 'form-helper';
        desc.textContent = item.description;
        card.appendChild(desc);
      }
      const actions = document.createElement('div');
      actions.className = 'material-actions';
      const downloadBtn = document.createElement('button');
      downloadBtn.className = 'primary-btn';
      downloadBtn.type = 'button';
      downloadBtn.textContent = '다운로드';
      downloadBtn.addEventListener('click', () => downloadMaterial(item));
      actions.appendChild(downloadBtn);
      if (item.file_url){
        const viewBtn = document.createElement('a');
        viewBtn.className = 'ghost-btn';
        viewBtn.href = item.file_url;
        viewBtn.target = '_blank';
        viewBtn.rel = 'noopener';
        viewBtn.textContent = '미리보기';
        actions.appendChild(viewBtn);
      }
      card.appendChild(actions);
      els.materialsGrid.appendChild(card);
    });
  }

  async function downloadMaterial(item){
    try {
      const response = await apiPost(`/materials/${item.id}/download/`, {});
      const url = response?.download_url || item.file_url;
      if (url) window.open(url, '_blank', 'noopener');
      loadDashboard(true);
    } catch (err){
      setFeedback(els.dashboardFeedback, '자료 다운로드에 실패했습니다.', 'error');
    }
  }

  function toggleLinkForm(){
    if (!els.newLinkForm) return;
    const isHidden = els.newLinkForm.style.display === 'none' || !els.newLinkForm.style.display;
    els.newLinkForm.style.display = isHidden ? 'flex' : 'none';
  }

  async function onCreateLink(evt){
    evt.preventDefault();
    if (!state.token) return;
    const form = evt.currentTarget;
    const payload = {
      name: form.querySelector('#newLinkName')?.value.trim(),
      target_url: form.querySelector('#newLinkTarget')?.value.trim(),
      utm_source: form.querySelector('#newLinkUTMSource')?.value.trim(),
      utm_medium: form.querySelector('#newLinkUTMMedium')?.value.trim(),
      utm_campaign: form.querySelector('#newLinkUTMCampaign')?.value.trim(),
    };
    try {
      await apiPost('/links/', payload);
      form.reset();
      toggleLinkForm();
      loadDashboard(true);
    } catch (err){
      setFeedback(els.dashboardFeedback, extractErrorMessage(err, '추천 링크 생성에 실패했습니다.'), 'error');
    }
  }

  async function onRequestPayout(){
    if (!ensureActivePartner()) return;
    if (!confirm('미지급 수수료에 대해 지급 요청을 진행할까요?')) return;
    try {
      const res = await apiPost('/commissions/request-payout/', {});
      const amount = res?.amount ? formatCurrency(res.amount, res.currency || 'KRW') : '';
      setFeedback(els.dashboardFeedback, `지급 요청이 접수되었습니다. ${amount}`, 'success');
      loadDashboard(true);
    } catch (err){
      setFeedback(els.dashboardFeedback, extractErrorMessage(err, '지급 요청에 실패했습니다.'), 'error');
    }
  }

  function copyPartnerCode(){
    const code = els.summaryPartnerCode?.textContent;
    if (!code) return;
    copyToClipboard(code);
  }

  function copyDefaultLink(){
    if (!ensureActivePartner()) return;
    if (!state.lastDashboard){
      setFeedback(els.dashboardFeedback, '대시보드를 불러오는 중입니다. 잠시 후 다시 시도해주세요.', 'info');
      loadDashboard(true);
      return;
    }
    const link = state.lastDashboard?.partner_info?.referral_link;
    if (link){
      copyToClipboard(link);
    } else {
      setFeedback(els.dashboardFeedback, '추천 링크를 찾을 수 없습니다. 링크를 먼저 생성해주세요.', 'error');
    }
  }

  function goToDashboardPanel(panelId){
    if (!ensureActivePartner()) return;
    scrollToSection(panelId);
  }

  function copyToClipboard(text){
    if (!text) return;
    if (navigator.clipboard){
      navigator.clipboard.writeText(text).then(() => {
        setFeedback(els.dashboardFeedback, '클립보드에 복사했습니다.', 'success');
      }).catch(() => fallbackCopy(text));
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text){
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setFeedback(els.dashboardFeedback, '클립보드에 복사했습니다.', 'success');
    } catch (err){
      setFeedback(els.dashboardFeedback, '복사에 실패했습니다.', 'error');
    }
  }

  function scrollToSection(id){
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    flashSection(id);
  }

  function normalizeList(data){
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.results)) return data.results;
    return [];
  }

  function translateTransactionType(code){
    const map = {
      earned: '수수료 발생',
      paid: '수수료 지급',
      adjustment: '조정',
      refund: '환불',
    };
    return map[code] || code;
  }

  function translateStatus(code){
    const map = {
      pending: '대기중',
      completed: '완료',
      failed: '실패',
      cancelled: '취소',
    };
    return map[code] || code;
  }

  function translateMaterialType(code){
    const map = {
      banner: '배너',
      text: '텍스트',
      video: '비디오',
      landing_page: '랜딩 페이지',
      email_template: '이메일 템플릿',
    };
    return map[code] || code;
  }

  function formatNumber(value){
    const num = Number(value || 0);
    return Number.isFinite(num) ? num.toLocaleString('ko-KR') : '0';
  }

  function formatCurrency(value, currency){
    const amount = Number(value || 0);
    const code = currency || 'KRW';
    if (!Number.isFinite(amount)) return '-';
    try {
      return amount.toLocaleString('ko-KR', { style: 'currency', currency: code });
    } catch (err){
      return `${amount.toLocaleString('ko-KR')} ${code}`;
    }
  }

  function formatDate(value){
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
  }

  function extractErrorMessage(err, fallback){
    if (!err) return fallback;
    const detail = err.detail || err.message || err.error;
    if (!detail) return fallback;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map(String).join(', ');
    if (typeof detail === 'object'){
      try {
        return Object.values(detail).map(val => Array.isArray(val) ? val.join(', ') : String(val)).join(' ');
      } catch (e){
        return JSON.stringify(detail);
      }
    }
    return String(detail);
  }

  function ensureLoginModal(){
    if (modalState.overlay) return modalState.overlay;
    const overlay = document.createElement('div');
    overlay.id = 'partnerLoginModal';
    overlay.className = 'partner-login-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = `
      <div class="partner-login-modal" role="dialog" aria-modal="true" aria-labelledby="partnerLoginTitle">
        <button type="button" class="partner-login-close" data-close>&times;</button>
        <h2 id="partnerLoginTitle">로그인이 필요합니다</h2>
        <p>파트너 포털은 회원 전용 서비스입니다. 계정으로 로그인해 주세요.</p>
        <form class="partner-login-form">
          <label for="partnerLoginEmail">이메일</label>
          <input type="email" id="partnerLoginEmail" name="email" required placeholder="you@example.com">
          <label for="partnerLoginPassword">비밀번호</label>
          <input type="password" id="partnerLoginPassword" name="password" required placeholder="비밀번호">
          <div class="partner-login-status" role="alert" aria-live="polite"></div>
          <button type="submit" class="primary-btn">${LOGIN_BUTTON_HTML}</button>
        </form>
      </div>
    `;
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closeLoginModal();
    });
    const closeBtn = overlay.querySelector('[data-close]');
    if (closeBtn){
      closeBtn.addEventListener('click', closeLoginModal);
    }
    const form = overlay.querySelector('form');
    if (form){
      form.addEventListener('submit', onLoginSubmit);
    }
    document.body.appendChild(overlay);
    modalState.overlay = overlay;
    return overlay;
  }

  function openLoginModal(){
    const overlay = ensureLoginModal();
    if (!overlay) return;
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('partner-modal-open');
    const emailInput = overlay.querySelector('#partnerLoginEmail');
    if (emailInput){
      setTimeout(() => emailInput.focus(), 60);
    }
  }

  function closeLoginModal(){
    const overlay = modalState.overlay || document.getElementById('partnerLoginModal');
    if (!overlay) return;
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('partner-modal-open');
    const status = overlay.querySelector('.partner-login-status');
    if (status){
      status.textContent = '';
      status.classList.remove('error', 'success');
    }
    const submit = overlay.querySelector('button[type="submit"]');
    if (submit){
      submit.disabled = false;
      submit.innerHTML = LOGIN_BUTTON_HTML;
    }
    const form = overlay.querySelector('form');
    if (form){
      form.reset();
    }
  }

  async function onLoginSubmit(event){
    event.preventDefault();
    const overlay = modalState.overlay || document.getElementById('partnerLoginModal');
    if (!overlay) return;
    const emailInput = overlay.querySelector('#partnerLoginEmail');
    const passwordInput = overlay.querySelector('#partnerLoginPassword');
    const statusEl = overlay.querySelector('.partner-login-status');
    const submitBtn = overlay.querySelector('button[type="submit"]');
    const email = emailInput?.value.trim();
    const password = passwordInput?.value || '';
    if (!email || !password){
      if (statusEl){
        statusEl.textContent = '이메일과 비밀번호를 모두 입력해주세요.';
        statusEl.classList.remove('success');
        statusEl.classList.add('error');
      }
      return;
    }
    if (submitBtn){
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 확인 중';
    }
    if (statusEl){
      statusEl.textContent = '';
      statusEl.classList.remove('error', 'success');
    }
    try {
      const csrf = state.csrf || getCSRFToken();
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrf ? { 'X-CSRFToken': csrf } : {}),
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok){
        const message = extractErrorMessage(data, '로그인에 실패했습니다.');
        throw new Error(message);
      }
      if (data.access_token) localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
      if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
      if (statusEl){
        statusEl.textContent = '로그인되었습니다. 잠시 후 새로고침됩니다.';
        statusEl.classList.remove('error');
        statusEl.classList.add('success');
      }
      setTimeout(() => {
        closeLoginModal();
        window.location.reload();
      }, 700);
    } catch (err){
      if (statusEl){
        statusEl.textContent = err.message || '로그인에 실패했습니다.';
        statusEl.classList.remove('success');
        statusEl.classList.add('error');
      }
      if (submitBtn){
        submitBtn.disabled = false;
        submitBtn.innerHTML = LOGIN_BUTTON_HTML;
      }
    }
  }

  async function apiGet(path){
    return request(path, { method: 'GET' });
  }

  async function apiPost(path, data){
    return request(path, {
      method: 'POST',
      body: data ? JSON.stringify(data) : '{}',
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async function request(path, options){
    // Allow cookie-auth flows where HttpOnly cookies carry the session
    if (!state.token && !state.cookieAuth) throw { status: 401 };
    const opts = options || {};
    const headers = Object.assign({}, opts.headers || {},
      state.token ? { Authorization: 'Bearer ' + state.token } : {}
    );
    if (state.csrf && !headers['X-CSRFToken']){
      headers['X-CSRFToken'] = state.csrf;
    }
    const response = await fetch(`${API_ROOT}${path}`, {
      ...opts,
      headers,
      credentials: 'include',
    });
    if (response.status === 204) return {};
    const text = await response.text();
    let payload = {};
    try {
      payload = text ? JSON.parse(text) : {};
    } catch (err){
      payload = { detail: text };
    }
    if (!response.ok){
      const error = payload;
      error.status = response.status;
      throw error;
    }
    return payload;
  }

  function ensureActivePartner(){
    if (!state.token){
      promptLogin('로그인 후 이용할 수 있는 기능입니다.', els.dashboardFeedback);
      return false;
    }
    if (!state.partner){
      setFeedback(els.dashboardFeedback, '먼저 파트너 신청을 완료해주세요.', 'error');
      return false;
    }
    if (state.partner.status !== 'active'){
      setFeedback(els.dashboardFeedback, '승인 완료 후 이용할 수 있는 기능입니다.', 'error');
      return false;
    }
    return true;
  }

  function setQuickActionsEnabled(enabled){
    const buttons = [els.quickCopyLink, els.quickMaterials, els.quickCommissions];
    buttons.forEach(btn => {
      if (!btn) return;
      btn.disabled = !enabled;
      btn.classList.toggle('disabled', !enabled);
    });
  }
})();

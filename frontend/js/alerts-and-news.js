(function(){
  function qs(sel){return document.querySelector(sel);}
  function qsa(sel){return Array.from(document.querySelectorAll(sel));}
  function toast(msg){
    try{console.log('[UI]', msg);}catch(e){}
    alert(msg);
  }

  async function createPriceAlert(symbol, price, market) {
    // Fallback: demo stores in localStorage if API not available
    try {
      const res = await fetch('/api/market-data/alerts/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, market, alert_type: 'price_up', trigger_price: price })
      });
      if (res.ok) return true;
    } catch (e) {}
    const list = JSON.parse(localStorage.getItem('price_alerts')||'[]');
    list.push({ symbol, market, price, ts: Date.now() });
    localStorage.setItem('price_alerts', JSON.stringify(list));
    return true;
  }

  function wirePriceAlertButtons(){
    const btn = qs('#setAlertBtn') || qs('#setAlertBtnTop');
    if (!btn) return;
    btn.addEventListener('click', async ()=>{
      const symbol = (qs('.chart-symbol')?.textContent || 'BTC/USD').split(/[\s·]/)[0].replace('/', '');
      const priceStr = prompt('알림을 받을 목표 가격을 입력하세요 (예: 45000)');
      if (!priceStr) return;
      const price = parseFloat(priceStr.replace(/,/g,''));
      if (!isFinite(price)) return alert('유효한 숫자를 입력해주세요.');
      await createPriceAlert(symbol, price, 'crypto');
      toast('가격 알림이 설정되었습니다.');
    });
  }

  async function fetchLatestNews(limit=5){
    const res = await fetch('/api/market-data/news/?limit='+limit);
    if (!res.ok) throw new Error('뉴스를 불러오지 못했습니다');
    return (await res.json()).news || [];
  }

  function renderNews(list){
    const ul = qs('.news-list');
    if (!ul) return;
    ul.innerHTML = '';
    list.forEach(item=>{
      const li = document.createElement('li');
      li.className = 'news-item';
      li.innerHTML = `<span class="news-title">${item.headline || item.title || '뉴스'}</span>
                      <span class="news-meta">${item.source || ''}</span>`;
      ul.appendChild(li);
    });
  }

  function wireNewsButtons(){
    qsa('.board-action').forEach(btn=>{
      const text = btn.textContent.trim();
      if (text.includes('새로고침')){
        btn.addEventListener('click', async ()=>{
          try{ const news = await fetchLatestNews(5); renderNews(news); toast('최신 뉴스로 새로고침했습니다.'); }
          catch(e){ alert('뉴스를 불러오지 못했습니다.'); }
        });
      } else if (text.includes('전체 보기')){
        btn.addEventListener('click', async ()=>{
          try{ const news = await fetchLatestNews(12); renderNews(news); }
          catch(e){ alert('전체 뉴스를 불러오지 못했습니다.'); }
        });
      }
    });
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    wirePriceAlertButtons();
    wireNewsButtons();
  });
})();

// Simple SNS sharing utility with graceful fallbacks
(function () {
  const currentUrl = window.location.href;
  const pageTitle = document.title || 'Stock Chart';
  const pageDesc = (document.querySelector('meta[name="description"]') || {}).content || '';

  function openPopup(url) {
    const w = 560, h = 640;
    const y = window.top.outerHeight / 2 + window.top.screenY - (h / 2);
    const x = window.top.outerWidth / 2 + window.top.screenX - (w / 2);
    window.open(url, '_blank', `toolbar=0,status=0,width=${w},height=${h},top=${y},left=${x}`);
  }

  function copyToClipboard(text) {
    try {
      navigator.clipboard.writeText(text);
      alert('링크가 복사되었습니다. 원하는 SNS에 붙여넣기 하세요.');
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
      alert('링크가 복사되었습니다.');
    }
  }

  async function webShare() {
    if (navigator.share) {
      try {
        await navigator.share({ title: pageTitle, text: pageDesc, url: currentUrl });
        return true;
      } catch (e) { /* user cancelled */ }
    }
    return false;
  }

  function kakaoShare() {
      try {
        // Kakao SDK optional
        if (window.Kakao && typeof window.Kakao.isInitialized === 'function') {
          if (!window.Kakao.isInitialized()) {
            const key = document.querySelector('meta[name="kakao-app-key"]')?.content || '';
            if (key) {
              window.Kakao.init(key);
            }
          }
          if (window.Kakao.isInitialized() && window.Kakao.Share) {
            window.Kakao.Share.sendDefault({
              objectType: 'feed',
              content: {
                title: pageTitle,
                description: pageDesc || '주식 차트 예측 플랫폼',
                imageUrl: document.querySelector('meta[property="og:image"]')?.content || '',
                link: { mobileWebUrl: currentUrl, webUrl: currentUrl }
              },
              buttons: [{
                title: '바로 보기',
                link: { mobileWebUrl: currentUrl, webUrl: currentUrl }
              }]
            });
            return true;
          }
        }
      } catch (e) {}
      return false;
  }

  function twitterShare() {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(pageTitle)}&url=${encodeURIComponent(currentUrl)}`;
    openPopup(url);
  }

  function facebookShare() {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
    openPopup(url);
  }

  function linkedinShare() {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(currentUrl)}`;
    openPopup(url);
  }

  function setupShareButtons() {
    document.querySelectorAll('[data-share]')?.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const type = btn.getAttribute('data-share');
        if (type === 'web') {
          const done = await webShare();
          if (!done) copyToClipboard(currentUrl);
        } else if (type === 'kakao') {
          const done = kakaoShare();
          if (!done) copyToClipboard(currentUrl);
        } else if (type === 'twitter') twitterShare();
        else if (type === 'facebook') facebookShare();
        else if (type === 'linkedin') linkedinShare();
        else copyToClipboard(currentUrl);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', setupShareButtons);

  // Expose minimal API
  window.SNSShare = { webShare, kakaoShare, twitterShare, facebookShare, linkedinShare, copyToClipboard };
})();

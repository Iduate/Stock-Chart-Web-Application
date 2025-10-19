(function(){
  async function createPaypalOrder(planId, currency) {
    const payload = { plan_id: planId, currency: currency || 'USD' };
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch('/api/payments/payments/create-paypal-order/', {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to create PayPal order');
    return res.json();
  }

  async function capturePaypal(orderId) {
    const res = await fetch('/api/payments/payments/capture-paypal-payment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId })
    });
    if (!res.ok) throw new Error('Failed to capture PayPal payment');
    return res.json();
  }

  async function startPaypalFlow(planId, currency) {
    const { approval_url } = await createPaypalOrder(planId, currency);
    if (approval_url) {
      window.location.href = approval_url;
    } else {
      alert('결제 링크 생성에 실패했습니다.');
    }
  }

  function wireSubscriptionButtons() {
    document.querySelectorAll('[data-paypal]')?.forEach(btn => {
      btn.addEventListener('click', () => {
        const directId = btn.getAttribute('data-plan-id');
        const planName = btn.getAttribute('data-plan-name');
        const currency = btn.getAttribute('data-currency') || 'USD';
        (async () => {
          try {
            let planId = directId;
            if (!planId && planName) {
              const res = await fetch('/api/payments/plans/');
              if (!res.ok) throw new Error('요금제 조회 실패');
              const list = await res.json();
              const match = (list?.results || list).find(p => p.name === planName);
              planId = match?.id;
            }
            if (!planId) throw new Error('요금제 ID를 찾을 수 없습니다.');
            await startPaypalFlow(planId, currency);
          } catch (err) {
            console.error(err);
            alert('PayPal 결제 시작 중 오류가 발생했습니다.');
          }
        })();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', wireSubscriptionButtons);
  window.PaymentsAPI = { startPaypalFlow, createPaypalOrder, capturePaypal };
})();

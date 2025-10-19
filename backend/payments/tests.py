from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from affiliates.models import AffiliatePartner, CommissionTransaction, ReferralClick, ReferralLink
from payments.models import Payment, PaymentMethod, PaymentPlan
from users.models import Subscription


class PayPalOrderFlowTests(APITestCase):
    """구독 결제(PayPal) 흐름을 검증하는 통합 테스트."""

    def setUp(self):
        self.plan = PaymentPlan.objects.create(
            name="프로",
            plan_type="premium",
            price_krw=Decimal("39900"),
            price_usd=Decimal("39.90"),
            duration_days=30,
            features=["무제한 예측", "실시간 데이터"],
        )

        self.partner_user = get_user_model().objects.create_user(
            username="affiliate",
            email="affiliate@example.com",
            password="pass1234",
            referral_code="AFFILIATE1",
        )
        self.partner = AffiliatePartner.objects.create(
            user=self.partner_user,
            phone_number="010-5555-5555",
            status="active",
            commission_rate=Decimal("15.00"),
        )
        self.link = ReferralLink.objects.create(
            partner=self.partner,
            name="랜딩 페이지",
            target_url="/",
        )

    @patch("payments.views.create_paypal_order")
    def test_create_paypal_order_persists_payment_and_referral_context(self, mock_create_order):
        """주문 생성 시 결제 레코드와 추천 정보가 모두 저장되는지 확인."""
        mock_create_order.return_value = {
            "id": "ORDER123",
            "status": "CREATED",
            "approval_url": "https://paypal.test/approve",
        }

        session = self.client.session
        session["referral_partner"] = self.partner.id
        session["referral_link"] = self.link.id
        session.save()

        response = self.client.post(
            reverse("payment-create-paypal-order"),
            {"plan_id": self.plan.id, "currency": "USD"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment = Payment.objects.get(external_payment_id="ORDER123")
        self.assertEqual(payment.plan, self.plan)
        self.assertEqual(payment.currency, "USD")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.payment_url, "https://paypal.test/approve")
        self.assertEqual(payment.callback_data.get("referral_partner_id"), self.partner.id)
        self.assertEqual(payment.callback_data.get("referral_link_id"), self.link.id)
        self.assertEqual(payment.callback_data.get("referral_session"), session.session_key)

    @patch("payments.views.capture_paypal_order")
    def test_capture_paypal_payment_completes_subscription_and_commission(self, mock_capture):
        """PayPal 결제 완료 시 구독 활성화와 수수료 적립이 정상 동작하는지 검증."""
        mock_capture.return_value = {"status": "COMPLETED"}

        subscriber = get_user_model().objects.create_user(
            username="subscriber",
            email="subscriber@example.com",
            password="pass1234",
            referral_code="SUBSCRIBER1",
        )
        payment_method = PaymentMethod.objects.create(
            name="PayPal",
            provider="paypal",
            is_active=True,
        )

        session = self.client.session
        session["referral_partner"] = self.partner.id
        session["referral_link"] = self.link.id
        session.save()

        ReferralClick.objects.create(
            link=self.link,
            ip_address="127.0.0.1",
            user_agent="pytest",
            session_id=session.session_key,
        )

        payment = Payment.objects.create(
            user=subscriber,
            plan=self.plan,
            payment_method=payment_method,
            amount=Decimal("39.90"),
            currency="USD",
            status="pending",
            transaction_id="txn-123",
            external_payment_id="ORDER456",
            callback_data={
                "referral_partner_id": self.partner.id,
                "referral_link_id": self.link.id,
                "referral_session": session.session_key,
            },
        )

        response = self.client.post(
            reverse("payment-capture-paypal-payment"),
            {"order_id": "ORDER456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "completed")
        self.assertIsNotNone(payment.completed_at)
        mock_capture.assert_called_once_with("ORDER456")

        subscriber.refresh_from_db()
        self.assertEqual(subscriber.user_type, "paid")
        self.assertEqual(subscriber.subscription_status, "active")
        self.assertIsNotNone(subscriber.subscription_expiry)

        self.assertTrue(
            Subscription.objects.filter(user=subscriber, payment_id=str(payment.id)).exists()
        )

        commission = CommissionTransaction.objects.get(partner=self.partner, reference_payment_id=str(payment.id))
        expected_commission = self.partner.calculate_commission(payment.amount).quantize(Decimal("0.01"))
        self.assertEqual(commission.amount, expected_commission)

        self.link.refresh_from_db()
        self.assertEqual(self.link.conversion_count, 1)

        click = ReferralClick.objects.get(link=self.link)
        self.assertTrue(click.converted)
        self.assertIsNotNone(click.converted_at)

        self.partner.refresh_from_db()
        self.assertGreaterEqual(self.partner.total_commission_earned, expected_commission)
        self.assertGreaterEqual(self.partner.total_conversions, 1)


from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from affiliates.models import AffiliatePartner, CommissionTransaction, ReferralClick, ReferralLink


class AffiliatePartnerAPITests(APITestCase):
    """API-level tests covering the 핵심 홍보파트너 플로우."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="partner_user",
            email="partner@example.com",
            password="testpass123",
            referral_code="REFPARTNER",
        )

    def test_apply_for_partnership_creates_partner(self):
        """신청 API가 신규 홍보파트너를 생성하고 파트너 코드가 발급되는지 확인."""
        self.client.force_authenticate(self.user)
        payload = {
            "company_name": "테스트 회사",
            "business_registration": "123-45-67890",
            "phone_number": "010-1234-5678",
            "website": "https://example.com",
            "social_media": {"instagram": "@stock"},
            "bank_info": {"bank": "KBank", "account": "123456"},
        }

        response = self.client.post(
            reverse("affiliate-partners-apply-for-partnership"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        partner = AffiliatePartner.objects.get(user=self.user)
        self.assertTrue(partner.partner_code)
        self.assertEqual(partner.status, "pending")
        self.assertEqual(partner.phone_number, payload["phone_number"])

    def test_dashboard_returns_recent_stats(self):
        """대시보드 엔드포인트가 최근 지표와 대기 중 수수료를 반환하는지 검증."""
        partner = AffiliatePartner.objects.create(
            user=self.user,
            phone_number="010-9999-9999",
            status="active",
            total_commission_earned=Decimal("120000"),
            total_commission_paid=Decimal("20000"),
        )
        link = ReferralLink.objects.create(
            partner=partner,
            name="테스트 링크",
            target_url="/",
        )
        ReferralClick.objects.create(
            link=link,
            ip_address="127.0.0.1",
            user_agent="pytest",
            session_id="sess123",
            clicked_at=timezone.now(),
        )
        CommissionTransaction.objects.create(
            partner=partner,
            transaction_type="earned",
            amount=Decimal("5000"),
            currency="KRW",
            description="이번 달 테스트",
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("affiliate-partners-dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("partner_info", data)
        self.assertIn("recent_stats", data)
        self.assertEqual(data["partner_info"]["partner_code"], partner.partner_code)
        self.assertGreaterEqual(data["recent_stats"]["clicks_30days"], 1)
        self.assertEqual(
            Decimal(str(data["recent_stats"]["pending_commission"])),
            partner.total_commission_earned - partner.total_commission_paid,
        )

    def test_request_payout_creates_pending_transaction(self):
        """지급 요청 시 최소 지급액 이상이면 거래가 생성되는지 확인."""
        partner = AffiliatePartner.objects.create(
            user=self.user,
            phone_number="010-8888-8888",
            status="active",
            total_commission_earned=Decimal("150000"),
            total_commission_paid=Decimal("20000"),
            minimum_payout=Decimal("50000"),
        )

        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("commission-transactions-request-payout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pending_amount = partner.total_commission_earned - partner.total_commission_paid
        self.assertEqual(
            Decimal(str(response.data["amount"])),
            pending_amount,
        )
        transaction = CommissionTransaction.objects.get(partner=partner, transaction_type="paid")
        self.assertEqual(transaction.status, "pending")
        self.assertEqual(transaction.amount, pending_amount)

    def test_referral_tracking_records_click_and_session(self):
        """추천 추적 뷰가 클릭 기록과 세션 값을 저장하는지 확인."""
        partner = AffiliatePartner.objects.create(
            user=self.user,
            phone_number="010-7777-7777",
            status="active",
        )
        link = ReferralLink.objects.create(
            partner=partner,
            name="카카오 공유",
            target_url="/welcome/",
        )

        session = self.client.session
        session.save()

        response = self.client.get(
            reverse("referral-tracking"),
            {
                "ref": partner.partner_code,
                "link_id": str(link.link_id),
                "target": "/welcome/",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, "/welcome/")

        link.refresh_from_db()
        self.assertEqual(link.click_count, 1)
        self.assertEqual(ReferralClick.objects.filter(link=link).count(), 1)

        session = self.client.session
        self.assertEqual(session.get("referral_partner"), partner.id)
        self.assertEqual(session.get("referral_link"), link.id)
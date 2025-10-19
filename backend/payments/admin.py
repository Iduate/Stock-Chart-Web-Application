from django.contrib import admin
from .models import (
	PaymentMethod,
	PaymentPlan,
	Payment,
	Coupon,
	CouponUsage,
	Referral,
	CommissionPayment,
	InternationalPayment,
	ExchangeRate,
	PaymentWebhook,
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
	list_display = ("name", "provider", "is_active")
	list_filter = ("provider", "is_active")
	search_fields = ("name", "provider")


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
	list_display = ("name", "plan_type", "price_krw", "price_usd", "duration_days", "is_active")
	list_filter = ("plan_type", "is_active")
	search_fields = ("name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ("user", "plan", "payment_method", "amount", "currency", "status", "created_at")
	list_filter = ("status", "currency", "payment_method")
	search_fields = ("transaction_id", "external_payment_id")
	readonly_fields = ("callback_data",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "coupon_type", "discount_value", "is_active", "valid_from", "valid_until")
	list_filter = ("coupon_type", "is_active")
	search_fields = ("code", "name")


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
	list_display = ("user", "coupon", "payment", "discount_amount", "used_at")
	list_filter = ("coupon",)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
	list_display = ("referrer", "referred", "commission_rate", "total_commission", "is_active", "created_at")
	list_filter = ("is_active",)
	search_fields = ("referrer__username", "referred__username")


@admin.register(CommissionPayment)
class CommissionPaymentAdmin(admin.ModelAdmin):
	list_display = ("referral", "payment", "commission_amount", "status", "paid_at")
	list_filter = ("status",)


@admin.register(InternationalPayment)
class InternationalPaymentAdmin(admin.ModelAdmin):
	list_display = ("user", "provider", "amount_converted", "currency_converted", "status", "created_at")
	list_filter = ("provider", "status", "currency_converted")
	search_fields = ("payment_id", "merchant_uid")


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
	list_display = ("from_currency", "to_currency", "rate", "source", "is_active", "updated_at")
	list_filter = ("from_currency", "to_currency", "is_active")


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
	list_display = ("provider", "event_type", "payment_id", "processed", "created_at")
	list_filter = ("provider", "processed")
	search_fields = ("payment_id", "event_type")

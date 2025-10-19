from django.db import migrations


def seed_payments(apps, schema_editor):
    PaymentMethod = apps.get_model('payments', 'PaymentMethod')
    PaymentPlan = apps.get_model('payments', 'PaymentPlan')

    # Ensure PayPal payment method exists
    PaymentMethod.objects.get_or_create(
        provider='paypal',
        defaults={
            'name': 'PayPal',
            'is_active': True,
            'icon_url': 'https://www.paypalobjects.com/webstatic/icon/pp258.png',
            'description': 'Pay with PayPal',
        }
    )

    # Ensure a couple of plans exist for testing
    plans = [
        {
            'name': '베이직',
            'plan_type': 'basic',
            'price_krw': 19900,
            'price_usd': 9.99,
            'duration_days': 30,
            'features': ['고급 차트', '예측 무제한', '실시간 데이터'],
            'is_active': True,
        },
        {
            'name': '프로',
            'plan_type': 'pro',
            'price_krw': 39900,
            'price_usd': 19.99,
            'duration_days': 30,
            'features': ['베이직 포함', '고급 모델', '포트폴리오 분석', '알림'],
            'is_active': True,
        },
    ]

    for p in plans:
        PaymentPlan.objects.get_or_create(
            name=p['name'],
            defaults=p,
        )


def unseed_payments(apps, schema_editor):
    # Leave seeded data in place on reverse migration
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0002_paymentwebhook_alter_paymentmethod_provider_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_payments, unseed_payments),
    ]

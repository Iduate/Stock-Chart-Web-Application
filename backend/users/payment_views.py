from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .visit_tracker import VisitTracker
from payments.models import PaymentPlan


def subscription_page(request):
    """
    Subscription page that shows available plans and prompts for payment
    """
    tracker = VisitTracker(request)
    payment_required = tracker.needs_payment_prompt()
    
    # Get available payment plans
    plans = PaymentPlan.objects.filter(is_active=True).order_by('price_krw')
    
    context = {
        'payment_required': payment_required,
        'visit_count': tracker.get_visit_count() if not request.user.is_authenticated else request.user.free_access_count,
        'plans': plans,
    }
    
    return render(request, 'subscription.html', context)


@login_required
@require_POST
def reset_free_visits(request):
    """
    For testing: Reset the free visits counter
    """
    if request.user.is_staff:
        request.user.free_access_count = 0
        request.user.save()
        
        tracker = VisitTracker(request)
        tracker.reset_visits()
        
        return JsonResponse({'status': 'success', 'message': 'Free visits counter reset'})
    
    return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

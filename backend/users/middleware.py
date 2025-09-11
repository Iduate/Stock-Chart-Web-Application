from .visit_tracker import VisitTracker
from django.shortcuts import redirect


class VisitTrackerMiddleware:
    """
    Middleware to track user visits to premium content and enforce access limits
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Define paths that require premium subscription (advanced features only)
        premium_paths = [
            '/api/charts/public_predictions/',
            '/api/charts/rankings/',
            '/api/market_data/',
            '/prediction/',
            '/ranking/',
        ]
        
        # Basic chart viewing should be free for logged-in users
        basic_chart_paths = ['/charts/', '/charts.html']
        
        # Skip tracking for static files, admin pages, authentication pages
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or 
            request.path.startswith('/api/auth/') or
            request.path == '/' or
            request.path == '/home/' or
            request.path == '/login/' or
            request.path == '/signup/'):
            return self.get_response(request)
        
        # Initialize visit tracker
        tracker = VisitTracker(request)
        
        # Check if the current path is premium content
        is_premium_content = any(request.path.startswith(path) for path in premium_paths)
        is_basic_charts = any(request.path.startswith(path) for path in basic_chart_paths)
        
        # Handle basic chart access (free for logged-in users)
        if is_basic_charts:
            # Debug: Print authentication status
            print(f"DEBUG: Chart access - User: {request.user}, Authenticated: {request.user.is_authenticated}")
            
            # TEMPORARY FIX: Allow chart access for everyone to test the charts
            print(f"DEBUG: TEMPORARY - Allowing chart access for all users to test functionality")
            return self.get_response(request)
            
            # Allow access if user is logged in, otherwise limit anonymous users
            if request.user.is_authenticated:
                print(f"DEBUG: Allowing chart access for logged-in user: {request.user.username}")
                # Logged-in users get free access to basic charts
                return self.get_response(request)
            else:
                print(f"DEBUG: Anonymous user accessing charts, checking limits")
                # Anonymous users still have limits
                if not tracker.can_access_premium():
                    print(f"DEBUG: Anonymous user limit reached, redirecting to subscription")
                    return redirect('subscription')
        
        # Only track and limit access for premium content
        if is_premium_content:
            # Check if user can access premium content
            if not tracker.can_access_premium():
                # If this is an API request, return appropriate response
                if request.path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({
                        'error': 'Free access limit reached',
                        'payment_required': True
                    }, status=402)  # 402 Payment Required
                else:
                    # For normal page requests, redirect to subscription page
                    return redirect('subscription')
            
            # Increment visit count for anonymous users or free users
            if tracker.is_anonymous():
                tracker.increment_visit()
            elif request.user.user_type == 'free':
                request.user.increment_free_access()
        
        # Continue with the request
        response = self.get_response(request)
        return response

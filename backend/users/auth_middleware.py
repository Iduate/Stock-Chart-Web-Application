from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json

User = get_user_model()

class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Simple token authentication middleware
    Checks for Bearer tokens in Authorization header
    Excludes admin URLs to allow Django's built-in authentication
    """
    
    def process_request(self, request):
        # Skip token authentication for admin URLs to allow Django's session auth
        if request.path.startswith('/admin/') or request.path.startswith('/static/admin/'):
            return None
        
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Check if token exists in session (simplified approach)
            # In production, you'd use a proper token store like Redis
            try:
                # Try to find a session with this token
                from django.contrib.sessions.models import Session
                for session in Session.objects.all():
                    session_data = session.get_decoded()
                    if session_data.get('auth_token') == token:
                        user_id = session_data.get('user_id')
                        if user_id:
                            try:
                                user = User.objects.get(id=user_id)
                                request.user = user
                                return None
                            except User.DoesNotExist:
                                pass
            except Exception:
                pass
        
        # Otherwise leave request.user as assigned by SessionAuthentication
        # (do not force AnonymousUser which would override logged-in sessions)
        return None

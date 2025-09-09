"""
Google OAuth utilities for the users app
"""
import requests
from django.conf import settings
from .models import User, UserProfile

def verify_google_token(token):
    """
    Verify a Google ID token and return user info
    
    Args:
        token (str): The Google ID token to verify
        
    Returns:
        dict: User information from Google or None if verification failed
    """
    try:
        # Verify the token with Google
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={'id_token': token}
        )
        
        if response.status_code != 200:
            return None
            
        user_info = response.json()
        
        # Check if token is issued for our app
        if user_info.get('aud') != settings.GOOGLE_CLIENT_ID:
            return None
            
        return user_info
    except Exception as e:
        print(f"Error verifying Google token: {e}")
        return None
        
def get_or_create_google_user(user_info):
    """
    Get or create a user based on Google profile information
    
    Args:
        user_info (dict): User information from Google
        
    Returns:
        User: The created or existing user
        bool: Whether the user was created or not
    """
    email = user_info.get('email')
    if not email:
        return None, False
        
    try:
        # Try to find an existing user
        user = User.objects.get(email=email)
        created = False
    except User.DoesNotExist:
        # Create a new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None,  # We don't need a password for OAuth users
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            auth_provider='google',
        )
        
        # Create a profile for the user
        UserProfile.objects.create(
            user=user,
            avatar_url=user_info.get('picture', '')
        )
        
        # Generate a referral code
        user.referral_code = f"REF{user.id:06d}"
        user.save()
        
        created = True
        
    return user, created

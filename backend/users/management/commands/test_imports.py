# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test import of oauth_utils and other modules'

    def handle(self, *args, **options):
        try:
            # Test imports
            from users.models import User, UserProfile, Subscription
            self.stdout.write(self.style.SUCCESS('✓ Successfully imported User models'))
            
            from users.serializers import UserSerializer, UserProfileSerializer, SubscriptionSerializer
            self.stdout.write(self.style.SUCCESS('✓ Successfully imported User serializers'))
            
            from users.oauth_utils import verify_google_token, get_or_create_google_user
            self.stdout.write(self.style.SUCCESS('✓ Successfully imported oauth_utils functions'))

            from users.views import GoogleOAuthView
            self.stdout.write(self.style.SUCCESS('✓ Successfully imported GoogleOAuthView'))
            
            self.stdout.write(self.style.SUCCESS('All imports are working correctly!'))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Import error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

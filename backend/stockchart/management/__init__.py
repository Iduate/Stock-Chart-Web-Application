"""
Django management command to test database connectivity
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.core.exceptions import ImproperlyConfigured
import os


class Command(BaseCommand):
    help = 'Test database connectivity'

    def handle(self, *args, **options):
        self.stdout.write("Testing database connectivity...")
        
        # Print environment info
        self.stdout.write(f"DATABASE_URL is set: {'YES' if os.environ.get('DATABASE_URL') else 'NO'}")
        self.stdout.write(f"RENDER environment: {os.environ.get('RENDER', 'Not set')}")
        
        try:
            # Get default database connection
            connection = connections['default']
            
            # Print database settings (without sensitive info)
            db_settings = connection.settings_dict
            self.stdout.write(f"Database ENGINE: {db_settings.get('ENGINE')}")
            self.stdout.write(f"Database NAME: {db_settings.get('NAME')}")
            self.stdout.write(f"Database HOST: {db_settings.get('HOST')}")
            self.stdout.write(f"Database PORT: {db_settings.get('PORT')}")
            self.stdout.write(f"Database USER: {db_settings.get('USER')}")
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result:
                self.stdout.write(
                    self.style.SUCCESS("✅ Database connection successful!")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Database connection failed - no result")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Database connection failed: {str(e)}")
            )
            
            # Print more detailed error info
            import traceback
            self.stdout.write("Full error traceback:")
            self.stdout.write(traceback.format_exc())
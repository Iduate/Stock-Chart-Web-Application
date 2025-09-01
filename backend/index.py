import os
import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockchart.free_deployment_settings')

# Setup Django
import django
django.setup()

# Import the WSGI application from wsgi.py
from stockchart.wsgi import application

# This is what Vercel looks for
app = application

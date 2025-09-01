import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockchart.free_deployment_settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

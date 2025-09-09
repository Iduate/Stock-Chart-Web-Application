# Setup Guide for Stock Chart Web Application

This guide will help you set up the development environment and fix the common issues that might occur during installation.

## Prerequisites

Make sure you have the following installed:

- Python 3.9 or higher
- pip (Python package manager)
- PostgreSQL database

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/Iduate/Stock-Chart-Web-Application.git
cd Stock-Chart-Web-Application
```

### 2. Set up a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the backend directory with the following contents:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_NAME=stockchart_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 5. Set up the database

```bash
# Create the database
createdb stockchart_db

# Apply migrations
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

## Troubleshooting Common Issues

### ImportError: "django.xxx" could not be resolved

This error typically occurs when the VS Code Python interpreter is not properly configured. To fix:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Select the Python interpreter from your virtual environment

### ImportError: "No module named 'xxx'"

If you're getting errors about missing modules:

```bash
pip install django-ipware
pip install django-oauth-toolkit
pip install psycopg2-binary
```

### Database connection errors

If you're having trouble connecting to PostgreSQL:

1. Check that PostgreSQL is running
2. Verify the credentials in your `.env` file
3. Try creating the database manually:
   ```
   psql -U postgres -c "CREATE DATABASE stockchart_db"
   ```

### Issues with middleware

If there are issues with the custom middleware:

1. Make sure your `MIDDLEWARE` setting in `settings.py` has the correct order
2. Check that `django.contrib.sessions.middleware.SessionMiddleware` is loaded before the custom middleware

### Django command not found

If you're getting "django-admin: command not found":

```bash
pip install django
```

## Next Steps

After successful installation:

1. Access the admin panel at http://127.0.0.1:8000/admin/ using your superuser credentials
2. Create test data using the admin interface
3. Visit the homepage at http://127.0.0.1:8000/ to see your application

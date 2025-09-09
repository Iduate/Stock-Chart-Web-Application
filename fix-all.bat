@echo off
echo =====================================================
echo Stock Chart Web Application - Fix All Script
echo =====================================================

echo Installing required Python packages...
pip install -r requirements.txt

echo Creating directories if they don't exist...
mkdir -p backend\charts\management\commands 2>nul
mkdir -p frontend\css 2>nul

echo Checking for .env file...
if not exist backend\.env (
    echo Creating .env file...
    echo SECRET_KEY=django-insecure-stockchart-app-development-key-2025 > backend\.env
    echo DEBUG=True >> backend\.env
    echo DATABASE_NAME=stockchart_db >> backend\.env
    echo DATABASE_USER=postgres >> backend\.env
    echo DATABASE_PASSWORD=postgres >> backend\.env
    echo DATABASE_HOST=localhost >> backend\.env
    echo DATABASE_PORT=5432 >> backend\.env
) else (
    echo .env file already exists.
)

echo Running Django migrations...
cd backend
python manage.py makemigrations
python manage.py migrate

echo Creating a superuser (if needed)...
echo To create a superuser, answer the following prompts:
python manage.py createsuperuser --username admin --email admin@example.com

echo Starting the Django development server...
python manage.py runserver

echo =====================================================
echo Script completed!
echo =====================================================

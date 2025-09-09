@echo off
echo ====================================================================
echo     Stock Chart Web Application - Package Installation Helper
echo ====================================================================
echo.

echo This script will install all required packages and handle common errors.
echo.

echo 1. Making sure pip is up to date...
python -m pip install --upgrade pip

echo.
echo 2. Installing wheel and setuptools (prevents build errors)...
pip install --upgrade setuptools wheel

echo.
echo 3. Installing all packages from requirements.txt...
pip install -r requirements.txt

echo.
echo 4. Checking for problematic packages and installing them separately if needed...

echo.
echo    Checking Pillow...
pip uninstall -y Pillow
pip install Pillow>=9.5.0,<10.0.0

echo.
echo    Checking psycopg2-binary...
pip install psycopg2-binary>=2.9.9,<3.0.0

echo.
echo    Checking django-ipware...
pip install django-ipware>=5.0.0,<6.0.0

echo.
echo ====================================================================
echo     Installation completed!
echo ====================================================================
echo.
echo If you still have issues:
echo  1. Try running: python -m pip install --upgrade --force-reinstall -r requirements.txt
echo  2. Check the Python version (Django 4.2.7 requires Python 3.8+)
echo  3. Make sure your virtual environment is activated
echo.
echo Press any key to continue...
pause > nul

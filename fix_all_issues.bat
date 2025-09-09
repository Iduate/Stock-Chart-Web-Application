@echo off
echo ================================================================
echo  Stock Chart Web Application - Complete Environment Fix Script
echo ================================================================
echo.

echo Step 1: Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Virtual environment created and activated.
)

echo.
echo Step 2: Updating pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 3: Installing all required packages...
pip install -r requirements.txt
pip install -r backend\requirements.txt

echo.
echo Step 4: Installing specific packages that might have issues...
pip install python-decouple
pip install dj-database-url
pip install Pillow
pip install django-ipware
pip install pylint pylint-django
pip install black

echo.
echo Step 5: Setting up VS Code configuration...
if not exist .vscode mkdir .vscode
copy /y .vscode\settings.json .vscode\settings.json.backup 2>nul
echo {
echo     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
echo     "python.analysis.extraPaths": [
echo         "${workspaceFolder}",
echo         "${workspaceFolder}/backend"
echo     ],
echo     "python.linting.enabled": true,
echo     "python.linting.pylintEnabled": true,
echo     "python.linting.pylintArgs": [
echo         "--disable=C0111",
echo         "--load-plugins=pylint_django",
echo         "--django-settings-module=stockchart.settings"
echo     ]
echo } > .vscode\settings.json

echo.
echo Step 6: Testing package imports...
python -c "try: import django; print(f'Django is installed: {django.__version__}'); except: print('Django import failed')"
python -c "try: from decouple import config; print('python-decouple is installed'); except: print('decouple import failed')"
python -c "try: import dj_database_url; print('dj-database-url is installed'); except: print('dj_database_url import failed')"
python -c "try: from PIL import Image; print('Pillow is installed'); except: print('PIL import failed')"

echo.
echo ================================================================
echo  Fix Complete!
echo ================================================================
echo.
echo If you still see import errors in VS Code:
echo  1. Restart VS Code completely
echo  2. Press Ctrl+Shift+P
echo  3. Type "Python: Select Interpreter"
echo  4. Select the Python interpreter from your .venv folder
echo.
echo Ready to run Django server:
echo  cd backend
echo  python manage.py runserver
echo.
pause

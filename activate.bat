@echo off
echo Activating virtual environment...

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
    echo.
    echo Python version:
    python --version
    echo.
    echo Installed packages:
    pip list
) else (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Virtual environment created and activated.
    echo.
    echo Installing required packages...
    pip install -r requirements.txt
)

echo.
echo You can now run Django commands, e.g.:
echo cd backend
echo python manage.py runserver

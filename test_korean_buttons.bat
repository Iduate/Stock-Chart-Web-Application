@echo off
echo Checking Korean translations for chart buttons...

cd frontend
echo.
echo Testing Korean translations...

echo 1. Verifying HTML files have Korean translations
findstr /C:"특성" home.html >nul
if %errorlevel% equ 0 (
  echo [OK] home.html contains Korean translations
) else (
  echo [ERROR] home.html is missing Korean translations
)

findstr /C:"특성" charts.html >nul
if %errorlevel% equ 0 (
  echo [OK] charts.html contains Korean translations
) else (
  echo [ERROR] charts.html is missing Korean translations
)

echo.
echo 2. Verifying JavaScript translation support
findstr /C:"translations" js\chart-controls.js >nul
if %errorlevel% equ 0 (
  echo [OK] Translation system found in chart-controls.js
) else (
  echo [ERROR] Translation system not found in chart-controls.js
)

echo.
echo 3. Starting test server...
cd ..
echo You can now check the buttons at http://localhost:8000/frontend/charts.html or http://localhost:8000/frontend/home.html
echo To test language switching, use ?lang=ko or ?lang=en at the end of the URL
echo.
echo Press Ctrl+C to stop the server when done.
python -m http.server 8000

echo Done.

@echo off
echo Checking for broken images and icons...

cd frontend
echo.
echo Testing image and icon fixes...

echo 1. Verifying Font Awesome is loaded properly
findstr /C:"font-awesome" home.html >nul
if %errorlevel% equ 0 (
  echo [OK] Font Awesome is included in home.html
) else (
  echo [ERROR] Font Awesome is missing in home.html
)

echo.
echo 2. Verifying SVG avatars
findstr /C:"data:image/svg+xml" home.html >nul
if %errorlevel% equ 0 (
  echo [OK] SVG avatars found in home.html
) else (
  echo [ERROR] SVG avatars not found in home.html
)

echo.
echo 3. Verifying stock symbols styling
findstr /C:"stock-symbol-container" home.html >nul
if %errorlevel% equ 0 (
  echo [OK] Stock symbol containers found in home.html
) else (
  echo [ERROR] Stock symbol containers not found in home.html
)

echo.
echo 4. Starting test server...
cd ..
echo You can now check the fixed images at http://localhost:8000/frontend/home.html
echo.
echo Press Ctrl+C to stop the server when done.
python -m http.server 8000

echo Done.

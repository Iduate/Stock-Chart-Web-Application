@echo off
echo Checking and fixing chart button issues...

cd frontend
echo Verifying JavaScript files...
if not exist js\chart-controls.js (
  echo Error: chart-controls.js not found
  exit /b 1
)

echo Verifying CSS files...
if not exist css\chart-controls.css (
  echo Error: chart-controls.css not found
  exit /b 1
)

echo Verifying HTML references...
findstr /c:"chart-controls.js" home.html >nul
if errorlevel 1 (
  echo Warning: chart-controls.js not found in home.html
  echo Adding reference...
  echo ^<script src="js/chart-controls.js"^>^</script^> >> home.html
)

findstr /c:"chart-controls.js" charts.html >nul
if errorlevel 1 (
  echo Warning: chart-controls.js not found in charts.html
  echo Adding reference...
  echo ^<script src="js/chart-controls.js"^>^</script^> >> charts.html
)

echo Running server to test changes...
cd ..
echo You can now check the buttons at http://localhost:8000/frontend/charts.html or http://localhost:8000/frontend/home.html
echo.
echo Press Ctrl+C to stop the server when done.
python -m http.server 8000

echo Done.

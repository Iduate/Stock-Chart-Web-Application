@echo off
echo ============================================================
echo  Stock Chart Web Application - Package Installation Script
echo ============================================================
echo.

echo Installing all required packages from the backend requirements.txt file...
echo.

cd backend
pip install -r requirements.txt

echo.
echo ============================================================
echo  Package installation completed!
echo ============================================================
echo.
echo If you still see import errors in your IDE:
echo  1. Restart your IDE or the Python Language Server
echo  2. Make sure your virtual environment is activated
echo  3. If using VS Code, select the correct Python interpreter
echo     (Ctrl+Shift+P then "Python: Select Interpreter")
echo.
echo Press any key to exit...
pause > nul

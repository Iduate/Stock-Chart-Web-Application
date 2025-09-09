@echo off
echo ===============================================================
echo  VS Code Python Development Environment Setup
echo ===============================================================
echo.

echo Installing Python linting and formatting tools...
pip install pylint pylint-django black

echo.
echo Installing Python development tools...
pip install ipython pytest pytest-django

echo.
echo Setting up VS Code Python settings...

REM Check if .vscode directory exists, create if not
if not exist .vscode mkdir .vscode

echo.
echo ===============================================================
echo  Setup complete!
echo ===============================================================
echo.
echo Please restart VS Code for the changes to take effect.
echo.
echo To fix remaining import errors in VS Code:
echo  1. Press Ctrl+Shift+P
echo  2. Type "Python: Select Interpreter"
echo  3. Select the Python interpreter from your .venv folder
echo.
pause

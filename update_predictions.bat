@echo off
echo Running prediction update task...

REM Navigate to the project directory
cd c:\Users\DAVID IDUATE\Desktop\UPDATED STOCK\Stock-Chart-Web-Application\backend

REM Run the update_predictions command
python manage.py update_predictions

echo Task completed.
pause

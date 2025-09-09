# Troubleshooting Guide for Stock Chart Web Application

This guide provides solutions to common issues encountered when setting up the Stock Chart Web Application.

## Current Issues and Fixes

### 1. Missing Dependencies

The most common issue is missing Python packages. Run:

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Django
- Django REST framework
- django-ipware (for IP detection)
- django-oauth-toolkit
- python-decouple
- psycopg2-binary (for PostgreSQL)

### 2. Import Errors in Python Files

These errors appear because some modules couldn't be imported. They will be resolved once the proper packages are installed.

### 3. File Structure Issues

The script `fix-all.bat` creates any missing directories needed for the project.

## Step-by-Step Fix

1. **Run the fix-all batch file**:
   ```
   fix-all.bat
   ```

2. **Manually fix remaining import issues**:
   
   If you still see import errors after running the fix script, check the following files:
   
   - `backend/users/visit_tracker.py`:
     - Make sure `ipware` is installed
   
   - `backend/charts/signals.py`:
     - Make sure the `Avg` import from `django.db.models` is present
   
   - `backend/users/middleware.py`:
     - Ensure the redirects are working properly

3. **Database Issues**:

   If you encounter database connection problems:
   
   - Check PostgreSQL is installed and running
   - Create the database manually if needed:
     ```
     createdb stockchart_db
     ```
   - Update the `.env` file with your database credentials

4. **Running the Application**:

   After fixing the issues:
   
   ```bash
   cd backend
   python manage.py runserver
   ```

## Testing the Fixes

1. **Check Import Errors**: 
   - If VS Code still shows import errors but the application runs, this is often just an IDE issue
   - Try restarting VS Code or its Python extension

2. **Test Visit Tracking**:
   - Open a private/incognito browser window
   - Visit premium content pages (e.g., /charts.html)
   - After 3 visits, you should be redirected to the subscription page

3. **Test User Authentication**:
   - Create a user account and test the login functionality
   - Verify that free users are limited to 3 visits

4. **Test Prediction System**:
   - Create a prediction and check if it's published on the chart board
   - Run the update_predictions command to test the accuracy calculation

## Need More Help?

If you continue to experience issues:

1. Check the Django logs for specific error messages
2. Run with debug mode enabled
3. Verify all environment variables are correctly set
4. Make sure PostgreSQL is properly configured

# Package Installation Guide

## Fixed Issues

I've updated the package requirements to use more flexible version ranges to avoid build issues. The main fixes are:

1. Changed Pillow from version 10.0.1 (which has build issues) to a range of `9.5.0 to 9.x`
2. Added flexible version ranges for all packages to prevent compatibility problems
3. Created helpful scripts to automate the installation process
4. Added additional dependencies that were missing

## How to Install the Packages

### Option 1: Using the Installation Helper Script

Run one of the helper scripts:

```bash
# On Windows
install_packages_fix.bat

# On any OS with Python
python install_packages.py
```

### Option 2: Manual Installation

Install these packages manually:

```bash
# Essential packages
pip install Django>=4.2.7,<4.3.0 djangorestframework>=3.14.0,<3.15.0 python-decouple>=3.8,<4.0

# Dependencies for image processing
pip install Pillow>=9.5.0,<10.0.0

# Database connector
pip install psycopg2-binary>=2.9.9,<3.0.0

# Authentication and API
pip install django-oauth-toolkit>=2.3.0,<2.4.0 djangorestframework-simplejwt>=5.3.0,<6.0.0

# Other required packages
pip install django-ipware>=5.0.0,<6.0.0 django-filter>=23.3,<24.0
```

## Fixing IDE Import Errors

If you still see import errors in your IDE after installing all packages:

1. Restart your IDE or the Python Language Server
2. Make sure your virtual environment is activated
3. If using VS Code, select the correct Python interpreter:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment

## Testing Your Installation

Run the following commands to verify your installation:

```python
# Verify Django installation
python -c "import django; print(f'Django version: {django.__version__}')"

# Verify DRF installation
python -c "import rest_framework; print(f'Django REST framework version: {rest_framework.__version__}')"

# Verify Pillow installation
python -c "import PIL; print(f'Pillow version: {PIL.__version__}')"
```

## Still Having Issues?

If you're still experiencing problems, try these steps:

1. Completely uninstall problematic packages and reinstall:
   ```
   pip uninstall -y Pillow
   pip install Pillow>=9.5.0,<10.0.0
   ```

2. Force reinstall all packages:
   ```
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

3. Check your Python version (Django 4.2.7 requires Python 3.8+):
   ```
   python --version
   ```

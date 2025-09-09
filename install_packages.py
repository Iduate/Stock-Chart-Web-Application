"""
Package Installation Helper for Stock Chart Web Application
This script checks for all required dependencies and installs them
with appropriate error handling.
"""

import subprocess
import sys
import os
from pathlib import Path

# Define required packages with version ranges
REQUIRED_PACKAGES = [
    "Django>=4.2.7,<4.3.0",
    "djangorestframework>=3.14.0,<3.15.0",
    "python-decouple>=3.8,<4.0",
    "django-cors-headers>=4.3.0,<4.4.0",
    "requests>=2.31.0,<2.32.0",
    "whitenoise>=6.5.0,<6.7.0", 
    "gunicorn>=21.2.0,<22.0.0",
    "dj-database-url>=2.1.0,<2.2.0",
    "Pillow>=9.5.0,<10.0.0",
    "psycopg2-binary>=2.9.9,<3.0.0",
    "django-oauth-toolkit>=2.3.0,<2.4.0",
    "django-ipware>=5.0.0,<6.0.0",
    "django-filter>=23.3,<24.0",
    "djangorestframework-simplejwt>=5.3.0,<6.0.0",
    "python-dateutil>=2.8.2,<3.0.0",
    "pytz>=2023.3",
    "six>=1.16.0,<2.0.0",
    "sqlparse>=0.4.4,<0.5.0",
    "tzdata>=2023.3"
]

# Define packages that might need special handling
PROBLEMATIC_PACKAGES = [
    "Pillow",
    "psycopg2-binary"
]

def run_command(command):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            command, 
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return None

def update_pip():
    """Ensure pip is up to date"""
    print("Updating pip to latest version...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

def install_build_tools():
    """Install tools needed for building packages"""
    print("Installing build tools...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])

def install_packages():
    """Install all required packages"""
    print("\n=== Installing all required packages ===\n")
    
    for package in REQUIRED_PACKAGES:
        pkg_name = package.split('>=')[0].split('==')[0]
        print(f"Installing {pkg_name}...")
        
        # Try to install the package
        result = run_command([sys.executable, "-m", "pip", "install", package])
        
        # If it's a problematic package and failed, try force reinstall
        if pkg_name in PROBLEMATIC_PACKAGES and "error" in str(result).lower():
            print(f"Trying force reinstall of {pkg_name}...")
            run_command([sys.executable, "-m", "pip", "uninstall", "-y", pkg_name])
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", package])

def check_installations():
    """Check if all packages are installed correctly"""
    print("\n=== Checking installed packages ===\n")
    
    for package in REQUIRED_PACKAGES:
        pkg_name = package.split('>=')[0].split('==')[0]
        try:
            # Try to import the package (simplified for common packages)
            if pkg_name.lower() == "django":
                import django
                print(f"✅ Django {django.__version__} installed")
            elif pkg_name.lower() == "pillow":
                try:
                    import PIL
                    print(f"✅ Pillow {PIL.__version__} installed")
                except (ImportError, AttributeError):
                    from PIL import Image
                    print(f"✅ Pillow (PIL) is installed")
            elif pkg_name.lower() == "djangorestframework":
                import rest_framework
                print(f"✅ DRF {rest_framework.__version__} installed")
            else:
                # Just check if it's installed via pip
                result = run_command([sys.executable, "-m", "pip", "show", pkg_name])
                if result:
                    print(f"✅ {pkg_name} installed")
                else:
                    print(f"❌ {pkg_name} not found")
        except ImportError:
            print(f"❌ {pkg_name} not properly installed")

def main():
    """Main function to run the installation process"""
    print("=" * 70)
    print("Stock Chart Web Application - Package Installation Helper")
    print("=" * 70)
    print("\nThis script will install all required packages for the project.\n")
    
    # Change to the backend directory if not already there
    backend_path = Path(__file__).parent / "backend"
    if backend_path.exists():
        os.chdir(backend_path)
        print(f"Working directory changed to: {os.getcwd()}")
    
    # Update pip and install build tools
    update_pip()
    install_build_tools()
    
    # Install all packages
    install_packages()
    
    # Check installations
    check_installations()
    
    print("\n" + "=" * 70)
    print("Package installation process completed!")
    print("=" * 70)
    print("\nIf you still see import errors in your IDE:")
    print("1. Restart your IDE or the Python Language Server")
    print("2. Make sure your virtual environment is activated")
    print("3. If using VS Code, select the correct Python interpreter")
    print("   (Ctrl+Shift+P then 'Python: Select Interpreter')")

if __name__ == "__main__":
    main()

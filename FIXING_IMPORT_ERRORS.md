# Fixing Import Errors in VS Code

If you're seeing import errors in VS Code (like "Import x could not be resolved"), here's how to fix them:

## Quick Fix: Run the Fix Script

The fastest way to fix all import errors is to run the provided batch file:

```
fix_all_issues.bat
```

This will:
1. Activate or create a virtual environment
2. Install all required packages
3. Set up VS Code settings
4. Test package imports

## Manual Fix Steps

If you prefer to fix issues manually or the script doesn't work:

### 1. Activate Your Virtual Environment

```
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Install Required Packages

```
pip install python-decouple dj-database-url Pillow django-ipware
```

### 3. Set Up VS Code Python Interpreter

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter"
3. Choose the Python interpreter from your `.venv` folder

### 4. Fix VS Code Settings

Create or edit `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.analysis.extraPaths": [
        "${workspaceFolder}",
        "${workspaceFolder}/backend"
    ],
    "python.linting.enabled": true
}
```

### 5. Restart VS Code

Close and reopen VS Code completely to make sure all changes take effect.

## Common Import Issues and Fixes

### Import "decouple" could not be resolved

```
pip install python-decouple
```

### Import "dj_database_url" could not be resolved

```
pip install dj-database-url
```

### Import "PIL" could not be resolved

```
pip install Pillow
```

### Import "django" could not be resolved

```
pip install Django
```

## For Pylance (VS Code Python Language Server)

If you're using Pylance (VS Code's Python language server) and still see import errors:

1. Create a file named `pyrightconfig.json` in your project root:

```json
{
    "include": [
        "backend"
    ],
    "extraPaths": [
        "${workspaceFolder}",
        "${workspaceFolder}/backend"
    ],
    "venvPath": ".",
    "venv": ".venv"
}
```

2. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")

## Note on Code Running vs. Import Errors

Sometimes VS Code will show import errors even though the code runs fine. This is because:

1. The IDE's Python Language Server runs separately from your code execution
2. It might not be using the same Python environment as your terminal

If your code runs successfully but VS Code shows errors, you can often ignore them or try the fixes above to make the IDE "see" your packages correctly.

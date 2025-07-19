# run_or_server.ps1
# This script sets up a Python virtual environment, installs dependencies, and runs the application.
# It is designed to be run in a Windows PowerShell environment.
# It assumes Python is installed and available in the system PATH.
# It also assumes that the requirements file is named 'requirements_or.txt' and is located in the same directory as this script.
# It creates a virtual environment named '.venv_or' if it does not already exist.


# Set paths
$venv = ".venv_or"
$requirements = "requirements_or.txt"

# Check for Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Please install Python and ensure it is accessible."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
}

# Activate the virtual environment
$activateScript = Join-Path $venv "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..."
    . $activateScript
} else {
    Write-Error "Activation script not found in $venv. Virtual environment may be corrupted."
    exit 1
}

# Install requirements
if (Test-Path $requirements) {
    Write-Host "Installing dependencies from $requirements..."
    pip install -r $requirements
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies from $requirements."
        exit 1
    }
} else {
    Write-Error "Requirements file not found: $requirements"
    exit 1
}

# Run the application
Write-Host "Starting application: python -m backend.dev_flask_opt.main"
python -m backend.dev_flask_opt.main
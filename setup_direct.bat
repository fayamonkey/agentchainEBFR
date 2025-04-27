@echo off
echo Welcome to Dirk's Agent Laboratory Research Lab Setup...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo and make sure it is added to your PATH.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version > nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed!
    echo Please install pip and try again.
    pause
    exit /b 1
)

REM Prompt for API key
set /p API_KEY="Please enter your OpenAI API key: "

REM Create Python virtual environment in a path without spaces
set VENV_PATH=%USERPROFILE%\agentlab_venv

REM Create virtual environment only if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating Python virtual environment in %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment!
        echo Please make sure you have write permissions in this directory.
        pause
        exit /b 1
    )
) else (
    echo Using existing virtual environment at %VENV_PATH%...
)

call "%VENV_PATH%\Scripts\activate.bat"

REM Install requirements
echo Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install required packages!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

REM Create config file with API key
echo Creating configuration...
echo { > config.json
echo   "api_key": "%API_KEY%" >> config.json
echo } >> config.json

REM Create desktop shortcuts using PowerShell
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Agent Laboratory Manager.lnk'); $Shortcut.TargetPath = '%~dp0run_research_manager.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Agent Laboratory Research Manager'; $Shortcut.Save()"

REM Create batch file with correct virtual environment path
echo Creating launch script...
echo @echo off > run_research_manager.bat
echo call "%VENV_PATH%\Scripts\activate.bat" >> run_research_manager.bat
echo python research_manager.py >> run_research_manager.bat
echo pause >> run_research_manager.bat

echo.
echo Setup completed successfully!
echo.
echo A shortcut has been created on your desktop:
echo - "Agent Laboratory Manager" for the GUI interface
echo.
echo Note: This setup was performed with Python %PYTHON_VERSION%
echo If you encounter any compatibility issues, please try using setup.bat
echo which will install with the recommended Python 3.10
echo.
echo For support, contact: dirk.wonhoefer@ai-engineering.ai
echo.
pause 
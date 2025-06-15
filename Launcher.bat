@echo off
setlocal enabledelayedexpansion

:: Set the title of the console window
title SHL Image Converter Launcher

:: Change to the script's directory
cd /d "%~dp0"

echo ===== SHL Image Converter Launcher =====
echo.

:: ===== STEP 1: Python Detection =====
echo [1/3] Detecting Python...

:: Define variables for Python paths
set "LOCAL_PYTHON=python\windows\python.exe"
set "PYTHON_CMD="

:: Check if local Python exists
if exist "%LOCAL_PYTHON%" (
    echo Python found in local directory.
    set "PYTHON_CMD=%LOCAL_PYTHON%"
    goto :PYTHON_FOUND
)

:: Check for system Python
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python found in system PATH.
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

:: Check for py launcher
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python found via py launcher.
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

:: Python not found, offer download options
echo Python is not installed on your device.
echo.
echo Please select an option:
echo [1] Download portable Python (will be extracted to the application folder)
echo [2] Download official Python installer (will install Python system-wide)
echo.

:PYTHON_CHOICE
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    goto :DOWNLOAD_PORTABLE
) else if "%choice%"=="2" (
    goto :DOWNLOAD_INSTALLER
) else (
    echo Invalid choice. Please enter 1 or 2.
    goto :PYTHON_CHOICE
)

:DOWNLOAD_PORTABLE
echo.
echo Downloading portable Python...

:: Create python directory if it doesn't exist
if not exist "python\windows" mkdir "python\windows"

:: Download Python portable using built-in bitsadmin
bitsadmin /transfer "PythonPortableDownload" https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip "%CD%\python_portable.zip" >nul

if %ERRORLEVEL% NEQ 0 (
    echo Failed to download portable Python. Please check your internet connection.
    goto :END
)

echo Extracting portable Python...
:: Extract using built-in expand command
powershell -Command "Expand-Archive -Path python_portable.zip -DestinationPath python\windows -Force" >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Failed to extract portable Python. Using alternative method...
    
    :: Try alternative extraction method if PowerShell fails
    call :ExtractZip "%CD%\python_portable.zip" "%CD%\python\windows"
    
    if !ERRORLEVEL! NEQ 0 (
        echo Failed to extract Python using all available methods.
        goto :END
    )
)

:: Clean up
del python_portable.zip >nul 2>&1

:: Install pip for portable Python
echo Setting up pip for portable Python...
curl -o python\windows\get-pip.py https://bootstrap.pypa.io/get-pip.py >nul 2>&1
"%CD%\python\windows\python.exe" python\windows\get-pip.py >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Failed to set up pip. Continuing anyway...
)

set "PYTHON_CMD=%CD%\python\windows\python.exe"
goto :PYTHON_FOUND

:DOWNLOAD_INSTALLER
echo.
echo Downloading official Python installer...

:: Download Python installer using built-in bitsadmin
bitsadmin /transfer "PythonInstallerDownload" https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe "%CD%\python_installer.exe" >nul

if %ERRORLEVEL% NEQ 0 (
    echo Failed to download Python installer. Please check your internet connection.
    goto :END
)

echo Running Python installer...
echo Please complete the installation process. Be sure to check "Add Python to PATH".
echo.
echo The launcher will continue automatically after installation.

:: Run the Python installer
start /wait python_installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_test=0

:: Clean up
del python_installer.exe >nul 2>&1

:: Check if Python was installed successfully
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
) else (
    echo Python installation failed or was cancelled.
    goto :END
)

:PYTHON_FOUND
echo Python successfully detected: !PYTHON_CMD!
echo.

:: ===== STEP 2: Install Dependencies =====
echo [2/3] Installing dependencies...

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Creating requirements.txt file...
    echo pyside6>=6.0.0 > requirements.txt
    echo pillow>=9.0.0 >> requirements.txt
    echo qtawesome>=1.0.0 >> requirements.txt
)

:: Install required packages silently
%PYTHON_CMD% -m pip install -r requirements.txt --upgrade >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Error details:
    %PYTHON_CMD% -m pip install -r requirements.txt
    goto :END
)

echo Dependencies installed successfully.
echo.

:: ===== STEP 3: Run Main Program =====
echo [3/3] Starting SHL Image Converter...
echo.

:: Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found in the current directory.
    goto :END
)

:: Run the main program
%PYTHON_CMD% main.py

if %ERRORLEVEL% NEQ 0 (
    echo Program exited with an error code: %ERRORLEVEL%
) else (
    echo Program completed successfully.
)

goto :END

:: ===== Helper function to extract ZIP files without PowerShell =====
:ExtractZip
setlocal
set "zipfile=%~1"
set "destination=%~2"

:: Using VBScript to extract ZIP file
set "vbscript=%temp%\_.vbs"
echo Set fso = CreateObject("Scripting.FileSystemObject") > "%vbscript%"
echo If NOT fso.FolderExists("%destination%") Then >> "%vbscript%"
echo    fso.CreateFolder("%destination%") >> "%vbscript%"
echo End If >> "%vbscript%"
echo set objShell = CreateObject("Shell.Application") >> "%vbscript%"
echo set FilesInZip=objShell.NameSpace("%zipfile%").items >> "%vbscript%"
echo objShell.NameSpace("%destination%").CopyHere(FilesInZip) >> "%vbscript%"
echo Set fso = Nothing >> "%vbscript%"
echo Set objShell = Nothing >> "%vbscript%"
cscript //nologo "%vbscript%" > nul
del "%vbscript%" > nul
endlocal
exit /b

:END
echo.
echo ===== Process Complete =====
pause
exit /b

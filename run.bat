@echo off
REM Eco Data Reader Launcher Script
REM This script runs the application using a portable Python installation

SETLOCAL

REM Check if portable Python exists
IF EXIST "python\python.exe" (
    echo Using portable Python installation...
    set PYTHON_EXE=python\python.exe
) ELSE (
    echo Portable Python not found. Checking for system Python...
    where python >nul 2>nul
    IF %ERRORLEVEL% EQU 0 (
        echo Using system Python installation...
        set PYTHON_EXE=python
    ) ELSE (
        echo ERROR: Python not found!
        echo.
        echo Please either:
        echo   1. Install Python and add it to your PATH, OR
        echo   2. Extract a portable Python to the 'python' folder in this directory
        echo.
        echo You can download Python embeddable package from:
        echo https://www.python.org/downloads/windows/
        echo.
        pause
        exit /b 1
    )
)

REM Check if config.ini exists
IF NOT EXIST "config.ini" (
    echo ERROR: config.ini not found!
    echo.
    echo Please create a config.ini file and set the ECO_SERVER_PATH.
    echo See config.ini.example or README for more information.
    echo.
    pause
    exit /b 1
)

REM Run the application
echo Running Eco Data Reader...
echo.
"%PYTHON_EXE%" main.py
echo.
echo Application finished.
pause

ENDLOCAL

@echo off
cd /d "%~dp0"
"GPX_SHP_Converter.exe"
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    echo.
    echo GPX to SHP Converter stopped with an error.
    echo Error code: %EXIT_CODE%
    echo.
    echo Please take a screenshot of this window when reporting the problem.
    pause
)

exit /b %EXIT_CODE%

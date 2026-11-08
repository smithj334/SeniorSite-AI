@echo off
echo.
echo ========================================
echo    SeniorSite AI - Startup Script
echo ========================================
echo.

REM Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Ollama does not appear to be running!
    echo.
    echo Please open another terminal and run:
    echo    ollama run llama3.1
    echo.
    echo The Chat Analysis feature requires Ollama.
    echo Other features will still work without it.
    echo.
    pause
)

echo.
echo Starting SeniorSite AI...
echo.
echo The application will open in your web browser.
echo Press Ctrl+C in this window to stop the server.
echo.

streamlit run app.py

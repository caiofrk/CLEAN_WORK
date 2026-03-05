@echo off
echo ==============================================
echo Starting Marketplace Python Scraper Backend...
echo ==============================================

cd "%~dp0\scraper_backend"
call venv\Scripts\activate.bat
python main.py

echo.
echo ==============================================
echo Scraping completed or stopped.
echo ==============================================
pause

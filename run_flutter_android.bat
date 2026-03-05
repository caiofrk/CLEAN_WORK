@echo off
echo ==============================================
echo Launching Android Emulator and Flutter App...
echo ==============================================

cd "%~dp0\marketplace_app"

echo Starting Emulator (Pixel 7 Pro)...
start "Launch Emulator" /B flutter emulators --launch Pixel_7_Pro

echo Waiting for emulator to boot up...
timeout /t 10 /nobreak

echo Building and Running the Flutter app...
flutter run

echo.
echo ==============================================
echo Application closed.
echo ==============================================
pause

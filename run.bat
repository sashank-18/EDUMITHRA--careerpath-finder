@echo off
echo ========================================================
echo          STARTING EDUMITHRA LEARNING PLATFORM
echo ========================================================
echo.

:: Launch the FastAPI Backend
echo [1/2] Launching backend server on http://localhost:8000 ...
start /B "" cmd /c "cd backend && python main.py"

:: Launch the Python HTTP Frontend
echo [2/2] Launching frontend server on http://localhost:3000 ...
start /B "" cmd /c "cd frontend && python -m http.server 3000"

echo.
echo ========================================================
echo  All systems starting up! 
echo  - Backend API:  http://localhost:8000
echo  - Frontend Web: http://localhost:3000
echo ========================================================
echo.
echo Waiting for servers to start...
timeout /t 3 /nobreak > NUL
echo Opening browser...
start http://localhost:3000

@echo off
echo ========================================
echo   Load Balancer Demo Startup
echo ========================================
echo.
echo Starting RL Agent Load Balancer...
echo.
echo Keep this window open during demo!
echo.
echo Dashboard will open automatically...
echo.
timeout /t 2 /nobreak >nul
start dashboard.html
python local_rl_loadbalancer.py

@echo off
echo ========================================
echo   Installing Demo Dependencies
echo ========================================
echo.
echo This will install all required packages...
echo.
pip install flask flask-cors requests python-dotenv
echo.
echo Installing TensorFlow (this may take a few minutes)...
pip install tensorflow tf-agents
echo.
echo Installing other dependencies...
pip install numpy prometheus_client flask-limiter
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run: python local_rl_loadbalancer.py
echo.
pause

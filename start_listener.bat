@echo off
REM MemoryX 后台监听服务启动脚本
REM 自动监听会话变化，调用 MemoryX

echo Starting MemoryX Listener...
echo.

cd /d "%~dp0..\..\.."
python -m memoryx.listener

pause

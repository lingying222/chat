@echo off
cd /d %~dp0
set PY="C:\Users\lingying\AppData\Local\Programs\Python\Python311\python.exe"
echo 启动本地删除服务（127.0.0.1:8765），关闭本窗口即停止服务...
%PY% delete_server.py
pause

@echo off
chcp 65001 >nul
cd /d %~dp0
"C:\Users\lingying\AppData\Local\Programs\Python\Python311\python.exe" build_manifest.py --watch
pause

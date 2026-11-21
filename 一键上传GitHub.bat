@echo off
cd /d %~dp0
set PY="C:\Users\lingying\AppData\Local\Programs\Python\Python311\python.exe"

echo [1/4] 重新生成目录清单...
%PY% build_manifest.py
if errorlevel 1 echo 警告：清单生成失败，仍继续上传。

echo [2/4] 暂存改动...
git add -A

git diff --cached --quiet
if errorlevel 1 (
  echo [3/4] 提交改动...
  git commit -m "update: 同步聊天记录归档 %date% %time%"
) else (
  echo [3/4] 没有需要提交的新改动。
)

echo [4/4] 推送到 GitHub...
git push origin main
if errorlevel 1 (
  echo.
  echo 推送失败：请确认代理已开启（127.0.0.1:7897）后重新双击本脚本。
  pause
  exit /b 1
)

echo.
echo 上传完成！线上地址：https://lingying222.github.io/chat/
pause

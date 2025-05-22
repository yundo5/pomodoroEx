@echo off
chcp 65001 >nul 2>nul

REM 1. 파이썬 설치 여부 확인
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 파이썬이 설치되어 있지 않습니다.
    echo python-3.12.3-amd64.exe를 실행하여 파이썬을 먼저 설치하세요.
    start python-3.12.3-amd64.exe
    pause
    exit /b
)

REM 2. 패키지 설치
pip install -r requirements.txt

REM 3. 서버 실행 (새 창에서)
start cmd /k ""C:\Users\axfgz\AppData\Local\Programs\Python\Python312\python.exe" app.py"

REM 4. 기본 웹브라우저로 자동 접속
timeout /t 3
start http://127.0.0.1:5000

pause

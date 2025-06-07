@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo [INFO] Python 설치 여부를 확인 중입니다...
set "PYTHON_PATH="

for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto check_version
)

echo [WARN] Python이 설치되어 있지 않은 것으로 보입니다.
if exist "%cd%\python-3.12.2-amd64.exe" (
    echo [INFO] 설치 파일 실행 중...
    start "" "%cd%\python-3.12.2-amd64.exe"
    echo 설치 후 run_pomodoro.bat를 다시 실행해주세요.
) else (
    echo [ERROR] 설치 파일이 없습니다. https://www.python.org/downloads/windows/
)
pause
exit /b

:check_version
for /f "tokens=2 delims= " %%v in ('"%PYTHON_PATH%" --version') do (
    set "PY_VER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("%%v") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
)
echo [INFO] Python 버전 확인됨: !PY_VER!
if "!PY_MAJOR!" LSS "3" (
    echo [ERROR] Python 3 이상이 필요합니다.
    pause
    exit /b
) else if "!PY_MINOR!" LSS "12" (
    echo [ERROR] Python 3.12 이상이 필요합니다.
    pause
    exit /b
)

echo [INFO] pip 설치 또는 업그레이드 중...
"%PYTHON_PATH%" -m ensurepip >nul 2>&1
"%PYTHON_PATH%" -m pip install --upgrade pip >nul 2>&1

if exist "%cd%\requirements.txt" (
    echo [INFO] requirements.txt 설치 중...
    "%PYTHON_PATH%" -m pip install -r "%cd%\requirements.txt"
) else (
    echo [WARN] requirements.txt 파일이 없습니다.
)

if exist "%cd%\app.py" (
    echo [INFO] app.py 실행 중...
    start "" cmd /k "%PYTHON_PATH%" app.py
    timeout /t 5 >nul
    start http://127.0.0.1:5000
) else (
    echo [ERROR] app.py 파일이 존재하지 않습니다.
)

pause

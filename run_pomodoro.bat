@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"

setlocal enabledelayedexpansion

echo [INFO] Python 경로 검색 중...
set "PYTHON_PATH="

:: Python 설치 경로 찾기
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto check_version
)

:: Python이 없을 경우 설치 시도
echo [WARN] Python이 설치되어 있지 않습니다.
if exist "%cd%\python-3.12.2-amd64.exe" (
    echo [INFO] python-3.12.2-amd64.exe 설치 파일 실행 중...
    start "" "%cd%\python-3.12.2-amd64.exe"
    echo 설치 완료 후 run_pomodoro.bat 파일을 다시 실행해주세요.
) else (
    echo [ERROR] python-3.12.2-amd64.exe 파일이 폴더에 없습니다.
    echo 공식 사이트에서 설치 파일을 받아주세요: https://www.python.org/downloads/windows/
)
pause
exit /b

:check_version
for /f "tokens=2 delims= " %%v in ('"%PYTHON_PATH%" --version') do set PY_VER=%%v
set PY_MAJOR=!PY_VER:~0,4!

echo [INFO] Python 버전 감지됨: !PY_VER!
if "!PY_MAJOR!" LSS "3.12" (
    echo [ERROR] Python 3.12 이상이 필요합니다.
    pause
    exit /b
)

:: pip 준비
echo [INFO] pip 설치 확인 중...
"%PYTHON_PATH%" -m ensurepip >nul 2>&1
"%PYTHON_PATH%" -m pip install --upgrade pip >nul 2>&1

:: requirements.txt 설치
if exist "%cd%\requirements.txt" (
    echo [INFO] requirements.txt 설치 중...
    "%PYTHON_PATH%" -m pip install -r "%cd%\requirements.txt"
) else (
    echo [WARN] requirements.txt 파일이 없습니다. 패키지 설치는 건너뜁니다.
)

:: app.py 실행
if exist "%cd%\app.py" (
    echo [INFO] app.py 실행 중...
    start "" cmd /k %PYTHON_PATH% "%cd%\app.py"
    timeout /t 3 >nul
    start http://127.0.0.1:5000
) else (
    echo [ERROR] app.py 파일을 찾을 수 없습니다.
)

pause

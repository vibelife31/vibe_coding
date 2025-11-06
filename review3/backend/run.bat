@echo off

REM 가상환경 활성화 (있는 경우)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 서버 실행
echo Starting backend server...
python main.py



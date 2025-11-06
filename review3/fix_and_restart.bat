@echo off
chcp 65001 > nul
echo ====================================
echo 문제 해결 및 서버 재시작
echo ====================================
echo.

echo [1/4] 기존 서버 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a > nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a > nul 2>&1
)
echo ✓ 기존 서버가 종료되었습니다
echo.

echo [2/4] 환경 설정 파일 확인 중...
if not exist "backend\.env" (
    echo .env 파일을 생성합니다...
    powershell -Command "[System.IO.File]::WriteAllText('backend\.env', 'DATABASE_URL=postgresql://postgres.cleksumdqxxgificirun:Supabase0630!@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres`nGEMINI_API_KEY=AIzaSyD_pzEUk3KMgDoxxyzG4JM_cRaY6-5GdWI`n', [System.Text.Encoding]::UTF8)"
    echo ✓ .env 파일이 생성되었습니다
) else (
    echo ✓ .env 파일이 존재합니다
)
echo.

echo [3/4] 데이터베이스 확인 중...
if not exist "backend\app_review.db" (
    echo ✓ 데이터베이스가 첫 실행 시 자동으로 생성됩니다
) else (
    echo ✓ 데이터베이스 파일이 존재합니다
)
echo.

echo [4/4] 서버 재시작 중...
cd backend
start "Backend Server" cmd /k "python main.py"
cd ..
ping 127.0.0.1 -n 4 > nul

cd frontend
if not exist "node_modules" (
    echo [경고] node_modules 폴더가 없습니다. 패키지를 설치합니다...
    npm install
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
)
start "Frontend Server" cmd /k "npm run dev"
cd ..
echo.

echo ====================================
echo 서버가 재시작되었습니다!
echo ====================================
echo.
echo 브라우저에서 다음 주소로 접속하세요:
echo 👉 http://localhost:3000
echo.
echo Backend API 문서:
echo 👉 http://localhost:8000/docs
echo.
pause


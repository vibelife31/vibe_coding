@echo off
chcp 65001 > nul
echo ====================================
echo 의존성 패키지 설치
echo ====================================
echo.

echo [0/5] 환경 설정 파일 생성 중...
if not exist "backend\.env" (
    powershell -Command "[System.IO.File]::WriteAllText('backend\.env', 'DATABASE_URL=postgresql://postgres.cleksumdqxxgificirun:Supabase0630!@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres`nGEMINI_API_KEY=AIzaSyD_pzEUk3KMgDoxxyzG4JM_cRaY6-5GdWI`n', [System.Text.Encoding]::UTF8)"
    echo ✓ .env 파일이 생성되었습니다
) else (
    echo ✓ .env 파일이 이미 존재합니다
)
echo.

echo [1/5] Backend 패키지 설치 중...
cd backend
echo Python 버전:
python --version
echo.
echo pip로 패키지를 설치합니다...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Backend 패키지 설치 실패
    cd ..
    pause
    exit /b 1
)
echo ✓ Backend 패키지 설치 완료
echo.

echo [2/5] Playwright 브라우저 설치 중...
python -m playwright install chromium
if errorlevel 1 (
    echo ❌ Playwright 브라우저 설치 실패
    cd ..
    pause
    exit /b 1
)
echo ✓ Playwright 브라우저 설치 완료
cd ..
echo.

echo [3/5] Frontend 패키지 설치 중...
cd frontend
echo Node.js 버전:
node --version
echo npm 버전:
npm --version
echo.
echo npm으로 패키지를 설치합니다...
npm install
if errorlevel 1 (
    echo ❌ Frontend 패키지 설치 실패
    cd ..
    pause
    exit /b 1
)
echo ✓ Frontend 패키지 설치 완료
cd ..
echo.

echo [4/5] 로컬 데이터베이스 확인 중...
if not exist "backend\app_review.db" (
    echo ✓ 첫 실행 시 자동으로 생성됩니다
) else (
    echo ✓ 데이터베이스 파일이 이미 존재합니다
)
echo.

echo [5/5] Supabase 테이블 설정 중...
cd backend
python check_and_setup_supabase.py
if errorlevel 1 (
    echo ❌ Supabase 설정 실패
    echo ⚠️  DATABASE_URL을 확인하거나 나중에 수동으로 실행하세요:
    echo    python backend\check_and_setup_supabase.py
    cd ..
) else (
    echo ✓ Supabase 테이블 설정 완료
    cd ..
)
echo.

echo ====================================
echo 모든 의존성 설치 완료!
echo ====================================
echo.
echo 이제 start_all.bat 파일을 실행하여
echo 서버를 시작할 수 있습니다.
echo.
pause


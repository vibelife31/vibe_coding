@echo off
chcp 65001 > nul
echo ====================================
echo Frontend 서버 시작
echo ====================================
echo.

cd frontend

echo Node.js 버전 확인...
node --version
echo npm 버전 확인...
npm --version
echo.

if not exist "node_modules" (
    echo [경고] node_modules 폴더가 없습니다. 패키지를 설치합니다...
    echo.
    npm install
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo.
    echo [완료] 패키지 설치가 완료되었습니다.
    echo.
)

echo Frontend 개발 서버를 시작합니다...
echo 서버 주소: http://localhost:3000
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
echo.

npm run dev

pause



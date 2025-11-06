# 🚀 서버 실행 가이드

## ❌ 일반적인 오류

### 오류 1: 파일을 찾을 수 없음
```
python: can't open file 'C:\\Cursor\\review3\\main.py': [Errno 2] No such file or directory
```

**원인**: 잘못된 디렉토리에서 명령을 실행했습니다.

**해결**: 올바른 경로로 이동해야 합니다.

---

## ✅ 올바른 실행 방법

### 📁 main.py 위치
```
C:\Cursor\review3\app_review_r1\backend\main.py
```

### 방법 1: 배치 파일 사용 (가장 간단) ⭐

**전체 서버 시작 (Backend + Frontend):**
```bash
cd C:\Cursor\review3\app_review_r1
start_all.bat
```

**Backend만 시작:**
```bash
cd C:\Cursor\review3\app_review_r1
start_backend.bat
```

**Frontend만 시작:**
```bash
cd C:\Cursor\review3\app_review_r1
start_frontend.bat
```

---

### 방법 2: 수동 실행

#### Backend 서버:
```bash
# 1단계: 올바른 디렉토리로 이동
cd C:\Cursor\review3\app_review_r1\backend

# 2단계: 서버 실행
python main.py
```

#### Frontend 서버 (새 터미널):
```bash
# 1단계: 올바른 디렉토리로 이동
cd C:\Cursor\review3\app_review_r1\frontend

# 2단계: 서버 실행
npm run dev
```

---

### 방법 3: 전체 경로 지정

```bash
# 어디서든 실행 가능 (하지만 권장하지 않음)
python C:\Cursor\review3\app_review_r1\backend\main.py
```

---

## 🔍 현재 위치 확인 방법

### PowerShell/CMD:
```bash
# 현재 디렉토리 확인
pwd    # PowerShell
cd     # CMD

# main.py 파일 확인
dir main.py

# 또는 전체 경로로 확인
dir C:\Cursor\review3\app_review_r1\backend\main.py
```

---

## 📋 단계별 체크리스트

### ✅ Backend 서버 시작 전 체크리스트:

1. **올바른 디렉토리로 이동**
   ```bash
   cd C:\Cursor\review3\app_review_r1\backend
   ```

2. **Python 버전 확인**
   ```bash
   python --version
   # Python 3.10 이상이어야 함
   ```

3. **필요한 패키지 설치 확인**
   ```bash
   pip list | findstr fastapi
   pip list | findstr uvicorn
   ```

4. **.env 파일 확인**
   ```bash
   type .env
   # DATABASE_URL과 GEMINI_API_KEY가 있어야 함
   ```

5. **서버 시작**
   ```bash
   python main.py
   ```

---

## 🛑 서버 종료 방법

### 배치 파일 사용:
```bash
cd C:\Cursor\review3\app_review_r1
stop_all.bat
```

### 수동 종료:
- 각 터미널에서 `Ctrl + C` 누르기
- 또는 작업 관리자에서 프로세스 종료

---

## 🌐 서버 접속 주소

서버가 정상적으로 시작되면:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

---

## 🐛 일반적인 오류 및 해결 방법

### 1. 포트가 이미 사용 중
```
Error: [Errno 48] Address already in use
```

**해결:**
```bash
# Windows에서 포트 사용 프로세스 확인
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 프로세스 종료
taskkill /F /PID [프로세스ID]

# 또는 stop_all.bat 실행
cd C:\Cursor\review3\app_review_r1
stop_all.bat
```

---

### 2. 모듈을 찾을 수 없음
```
ModuleNotFoundError: No module named 'fastapi'
```

**해결:**
```bash
cd C:\Cursor\review3\app_review_r1\backend
pip install -r requirements.txt
```

---

### 3. 환경 변수 오류
```
ValueError: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다
```

**해결:**
```bash
cd C:\Cursor\review3\app_review_r1\backend

# .env 파일 확인
type .env

# .env 파일이 없으면 생성
python -c "with open('.env', 'w', encoding='utf-8') as f: f.write('DATABASE_URL=postgresql://postgres.cleksumdqxxgificirun:Supabase0630!@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres\nGEMINI_API_KEY=AIzaSyD_pzEUk3KMgDoxxyzG4JM_cRaY6-5GdWI\n')"
```

---

### 4. 데이터베이스 연결 오류
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결:**
```bash
# 데이터베이스 연결 테스트
cd C:\Cursor\review3\app_review_r1\backend
python -c "from database import engine; print('✓ 연결 성공!' if engine.connect() else '✗ 연결 실패')"

# 테이블 설정
python check_and_setup_supabase.py
```

---

### 5. Playwright 브라우저 오류
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**해결:**
```bash
python -m playwright install chromium
```

---

## 🎯 권장 실행 순서 (처음 실행 시)

```bash
# 1. 프로젝트 디렉토리로 이동
cd C:\Cursor\review3\app_review_r1

# 2. 의존성 설치 (처음 한 번만)
install_dependencies.bat

# 3. 서버 시작
start_all.bat

# 4. 브라우저에서 접속
# http://localhost:3000
```

---

## 📞 추가 도움말

더 자세한 정보는 다음 문서를 참고하세요:
- [README.md](README.md) - 전체 프로젝트 가이드
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 문제 해결 가이드
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - 데이터베이스 설정

---

## ⚡ 빠른 명령어 요약

```bash
# 서버 시작
cd C:\Cursor\review3\app_review_r1
start_all.bat

# 서버 종료
stop_all.bat

# 문제 해결 및 재시작
fix_and_restart.bat

# 의존성 재설치
install_dependencies.bat
```

---

## ✅ 정상 작동 확인

서버가 정상적으로 시작되면 다음과 같은 메시지가 표시됩니다:

```
INFO:     Started server process [25400]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

브라우저에서 http://localhost:8000/docs 에 접속하면 API 문서를 볼 수 있습니다.


# 📦 Supabase 설정 가이드

이 문서는 앱 리뷰 분석기의 Supabase 데이터베이스 설정 방법을 안내합니다.

## 🎯 개요

이 프로젝트는 **Supabase PostgreSQL**을 데이터베이스로 사용합니다.
- ✅ 클라우드 기반 PostgreSQL 데이터베이스
- ✅ 자동 백업 및 확장성
- ✅ RLS (Row Level Security) 보안 기능
- ✅ 실시간 기능 (선택사항)

## 🔧 자동 설정 (권장)

가장 간단한 방법은 설치 스크립트를 실행하는 것입니다:

```bash
# 프로젝트 루트에서 실행
install_dependencies.bat
```

이 스크립트는 자동으로:
1. `.env` 파일 생성 (DATABASE_URL 포함)
2. 필요한 패키지 설치
3. Supabase 테이블 생성 및 설정
4. RLS 보안 정책 적용

## 🛠️ 수동 설정

### 1단계: 환경 변수 설정

`backend/.env` 파일을 생성하고 다음 내용을 추가:

```env
DATABASE_URL=postgresql://postgres.cleksumdqxxgificirun:Supabase0630!@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
GEMINI_API_KEY=AIzaSyD_pzEUk3KMgDoxxyzG4JM_cRaY6-5GdWI
```

### 2단계: Supabase 테이블 생성

```bash
cd backend
python check_and_setup_supabase.py
```

### 실행 결과 예시:

```
============================================================
Supabase 테이블 확인 및 설정
============================================================

[1/5] Supabase 연결 확인 중...
✓ 연결 성공: PostgreSQL

[2/5] 테이블 존재 확인 중...
✓ app_info 테이블 존재
✓ app_review 테이블 존재

[3/5] 테이블 구조 확인 중...
📋 app_info 테이블:
   - id: integer (NOT NULL)
   - app_id: character varying (NOT NULL)
   - app_name: character varying (NOT NULL)
   - review_count: character varying (NULL)
   - download_count: character varying (NULL)
   - rating: character varying (NULL)
   - overall_analysis: text (NULL)
   - created_at: timestamp (NULL)

📋 app_review 테이블:
   - id: integer (NOT NULL)
   - app_id: character varying (NOT NULL)
   - rating: double precision (NULL)
   - review_content: text (NULL)
   - review_date: character varying (NULL)
   - individual_analysis: text (NULL)
   - created_at: timestamp (NULL)

[4/5] 인덱스 확인 중...
✓ 인덱스 존재

[5/5] RLS 설정 중...
✓ app_info RLS 활성화
✓ app_review RLS 활성화
✓ RLS 정책 생성 완료

============================================================
✅ Supabase 설정 완료!
============================================================
```

## 📊 데이터베이스 구조

### app_info 테이블
앱의 기본 정보를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| app_id | VARCHAR | 앱 패키지 ID (UNIQUE) |
| app_name | VARCHAR | 앱 이름 |
| review_count | VARCHAR | 리뷰 개수 |
| download_count | VARCHAR | 다운로드 수 |
| rating | VARCHAR | 평균 평점 |
| overall_analysis | TEXT | 전체 리뷰 AI 분석 결과 |
| created_at | TIMESTAMP | 생성 시간 |

**인덱스:**
- PRIMARY KEY (id)
- UNIQUE INDEX (app_id)

### app_review 테이블
개별 리뷰 정보를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| app_id | VARCHAR | 앱 패키지 ID (외래 키) |
| rating | FLOAT | 리뷰 평점 (1-5) |
| review_content | TEXT | 리뷰 내용 |
| review_date | VARCHAR | 리뷰 작성일 |
| individual_analysis | TEXT | 개별 리뷰 AI 분석 결과 |
| created_at | TIMESTAMP | 생성 시간 |

**인덱스:**
- PRIMARY KEY (id)
- FOREIGN KEY (app_id) → app_info(app_id)

**관계:**
- `app_review.app_id` → `app_info.app_id` (ON DELETE CASCADE)

## 🔒 보안 설정 (RLS)

Row Level Security (RLS)가 활성화되어 있습니다:

### 현재 정책
- **정책 이름**: "Allow all operations"
- **적용 테이블**: app_info, app_review
- **권한**: 모든 작업 허용 (SELECT, INSERT, UPDATE, DELETE)

⚠️ **프로덕션 환경에서는 더 엄격한 정책을 설정하세요:**

```sql
-- 예시: 인증된 사용자만 읽기 가능
DROP POLICY IF EXISTS "Allow all operations on app_info" ON app_info;

CREATE POLICY "Authenticated users can read"
ON app_info
FOR SELECT
USING (auth.role() = 'authenticated');

CREATE POLICY "Service role can do everything"
ON app_info
FOR ALL
USING (auth.role() = 'service_role');
```

## 🧪 연결 테스트

데이터베이스 연결을 테스트하려면:

```bash
cd backend
python -c "from database import engine; print('✓ 연결 성공!' if engine.connect() else '✗ 연결 실패')"
```

## 📝 추가 스크립트

### create_supabase_tables.py
기본 테이블 생성만 수행합니다 (RLS 설정 없음).

```bash
python create_supabase_tables.py
```

### check_and_setup_supabase.py (권장)
테이블 생성 + 구조 확인 + RLS 설정을 모두 수행합니다.

```bash
python check_and_setup_supabase.py
```

## 🔍 문제 해결

### 연결 타임아웃
```
Error: Connection terminated due to connection timeout
```

**해결방법:**
1. 인터넷 연결 확인
2. Supabase 프로젝트가 활성화되어 있는지 확인
3. DATABASE_URL이 올바른지 확인
4. 방화벽 설정 확인

### 테이블이 보이지 않음
```bash
# 테이블 목록 확인
cd backend
python -c "from database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')); [print(row[0]) for row in result.fetchall()]"
```

### RLS 정책 확인
```bash
# RLS 상태 확인
cd backend
python -c "from database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = \'public\'')); [print(f'{row[0]}: {row[1]}') for row in result.fetchall()]"
```

## 📚 관련 문서

- [README.md](README.md) - 프로젝트 전체 가이드
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 일반적인 문제 해결
- [Supabase 공식 문서](https://supabase.com/docs) - Supabase 자세한 사용법

## 🎉 완료!

설정이 완료되었다면 이제 애플리케이션을 시작할 수 있습니다:

```bash
start_all.bat
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs


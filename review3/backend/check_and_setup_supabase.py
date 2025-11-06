# -*- coding: utf-8 -*-
"""
Supabase 테이블 확인 및 RLS 설정 스크립트
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, text
from models import Base
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# DATABASE_URL 환경 변수 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[오류] DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    exit(1)

if not DATABASE_URL.startswith("postgresql"):
    print("[오류] DATABASE_URL이 PostgreSQL 형식이 아닙니다.")
    exit(1)

try:
    print("=" * 60)
    print("Supabase 테이블 확인 및 설정")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    # 1. 연결 테스트
    print("\n[1/5] Supabase 연결 확인 중...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✓ 연결 성공: PostgreSQL")
    
    # 2. 테이블 존재 확인
    print("\n[2/5] 테이블 존재 확인 중...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('app_info', 'app_review')
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        if 'app_info' in tables and 'app_review' in tables:
            print("✓ app_info 테이블 존재")
            print("✓ app_review 테이블 존재")
        else:
            print("! 테이블이 없습니다. 생성 중...")
            Base.metadata.create_all(bind=engine)
            print("✓ 테이블 생성 완료")
    
    # 3. 테이블 구조 확인
    print("\n[3/5] 테이블 구조 확인 중...")
    with engine.connect() as conn:
        # app_info 테이블
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'app_info' 
            ORDER BY ordinal_position
        """))
        print("\n📋 app_info 테이블:")
        for row in result.fetchall():
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"   - {row[0]}: {row[1]} ({nullable})")
        
        # app_review 테이블
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'app_review' 
            ORDER BY ordinal_position
        """))
        print("\n📋 app_review 테이블:")
        for row in result.fetchall():
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"   - {row[0]}: {row[1]} ({nullable})")
    
    # 4. 인덱스 확인
    print("\n[4/5] 인덱스 확인 중...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('app_info', 'app_review')
            ORDER BY tablename, indexname
        """))
        indexes = result.fetchall()
        if indexes:
            print("✓ 인덱스 존재:")
            for row in indexes:
                print(f"   - {row[1]}.{row[2]}")
        else:
            print("! 인덱스가 없습니다.")
    
    # 5. RLS (Row Level Security) 상태 확인 및 설정
    print("\n[5/5] RLS (Row Level Security) 설정 중...")
    with engine.connect() as conn:
        # RLS 활성화 확인
        result = conn.execute(text("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('app_info', 'app_review')
        """))
        rls_status = {row[0]: row[1] for row in result.fetchall()}
        
        # app_info RLS 설정
        if not rls_status.get('app_info'):
            conn.execute(text("ALTER TABLE app_info ENABLE ROW LEVEL SECURITY"))
            conn.commit()
            print("✓ app_info RLS 활성화")
        else:
            print("✓ app_info RLS 이미 활성화됨")
        
        # app_review RLS 설정
        if not rls_status.get('app_review'):
            conn.execute(text("ALTER TABLE app_review ENABLE ROW LEVEL SECURITY"))
            conn.commit()
            print("✓ app_review RLS 활성화")
        else:
            print("✓ app_review RLS 이미 활성화됨")
        
        # 기본 정책 생성 (모든 작업 허용 - 필요에 따라 수정 가능)
        # 먼저 기존 정책 삭제 시도
        try:
            conn.execute(text('DROP POLICY IF EXISTS "Allow all operations on app_info" ON app_info'))
            conn.commit()
        except:
            pass
        
        try:
            conn.execute(text('DROP POLICY IF EXISTS "Allow all operations on app_review" ON app_review'))
            conn.commit()
        except:
            pass
        
        try:
            # app_info 정책
            conn.execute(text("""
                CREATE POLICY "Allow all operations on app_info"
                ON app_info
                FOR ALL
                USING (true)
                WITH CHECK (true)
            """))
            conn.commit()
            print("✓ app_info RLS 정책 생성")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ app_info RLS 정책 이미 존재")
            else:
                print(f"⚠ app_info 정책 생성 시 경고: {str(e)[:100]}")
        
        try:
            # app_review 정책
            conn.execute(text("""
                CREATE POLICY "Allow all operations on app_review"
                ON app_review
                FOR ALL
                USING (true)
                WITH CHECK (true)
            """))
            conn.commit()
            print("✓ app_review RLS 정책 생성")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ app_review RLS 정책 이미 존재")
            else:
                print(f"⚠ app_review 정책 생성 시 경고: {str(e)[:100]}")
    
    # 완료 메시지
    print("\n" + "=" * 60)
    print("✅ Supabase 설정 완료!")
    print("=" * 60)
    print("\n다음 정보로 접속할 수 있습니다:")
    print(f"- Backend API: http://localhost:8000")
    print(f"- API 문서: http://localhost:8000/docs")
    print("\n테이블:")
    print("  • app_info: 앱 정보 저장")
    print("  • app_review: 리뷰 정보 저장")
    print("\n보안:")
    print("  • RLS (Row Level Security) 활성화됨")
    print("  • 모든 작업 허용 정책 적용됨")
    print("\n⚠️  주의: 프로덕션 환경에서는 RLS 정책을 더 엄격하게 설정하세요.")
    
except Exception as e:
    print(f"\n[오류] 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)


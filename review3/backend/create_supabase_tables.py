# -*- coding: utf-8 -*-
"""
Supabase 테이블 생성 스크립트
이 스크립트를 실행하면 Supabase에 테이블이 생성됩니다.
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
    print("backend/.env 파일에 DATABASE_URL을 설정해주세요.")
    exit(1)

# PostgreSQL 연결 문자열 확인
if not DATABASE_URL.startswith("postgresql"):
    print("[오류] DATABASE_URL이 PostgreSQL 형식이 아닙니다.")
    print(f"현재 DATABASE_URL: {DATABASE_URL[:50]}...")
    exit(1)

try:
    print("Supabase에 연결 중...")
    engine = create_engine(DATABASE_URL)
    
    # 연결 테스트
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"[성공] 연결 완료: {version[:50]}...")
    
    print("\n테이블 생성 중...")
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    print("[완료] app_info 테이블 생성 완료")
    print("[완료] app_review 테이블 생성 완료")
    
    # 생성된 테이블 확인
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('app_info', 'app_review')
            ORDER BY table_name
        """))
        tables = result.fetchall()
        
        print("\n생성된 테이블:")
        for table in tables:
            print(f"  - {table[0]}")
    
    print("\n모든 테이블이 성공적으로 생성되었습니다!")
    
except Exception as e:
    print(f"\n[오류] 오류 발생: {str(e)}")
    print("\n다음 사항을 확인해주세요:")
    print("1. DATABASE_URL이 올바른지 확인")
    print("2. Supabase 프로젝트가 활성화되어 있는지 확인")
    print("3. 네트워크 연결 상태 확인")
    exit(1)


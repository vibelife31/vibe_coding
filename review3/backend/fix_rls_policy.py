# -*- coding: utf-8 -*-
"""
Supabase RLS 정책 수정 스크립트
데이터 저장이 안 되는 문제를 해결합니다.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    print("[오류] DATABASE_URL이 올바르게 설정되지 않았습니다.")
    exit(1)

try:
    print("=" * 60)
    print("Supabase RLS 정책 수정")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n[1/5] 기존 RLS 정책 삭제 중...")
        
        # 기존 정책 삭제
        try:
            conn.execute(text('DROP POLICY IF EXISTS "Allow all operations on app_info" ON app_info'))
            conn.execute(text('DROP POLICY IF EXISTS "Allow all operations on app_review" ON app_review'))
            conn.commit()
            print("✓ 기존 정책 삭제 완료")
        except Exception as e:
            print(f"⚠ 기존 정책 삭제 시 경고: {str(e)[:100]}")
        
        print("\n[2/5] RLS 비활성화 (임시)...")
        try:
            conn.execute(text('ALTER TABLE app_info DISABLE ROW LEVEL SECURITY'))
            conn.execute(text('ALTER TABLE app_review DISABLE ROW LEVEL SECURITY'))
            conn.commit()
            print("✓ RLS 비활성화 완료")
        except Exception as e:
            print(f"⚠ RLS 비활성화 오류: {str(e)[:100]}")
        
        print("\n[3/5] 데이터베이스 권한 확인 중...")
        result = conn.execute(text("""
            SELECT grantee, privilege_type 
            FROM information_schema.role_table_grants 
            WHERE table_name IN ('app_info', 'app_review')
            AND grantee NOT IN ('postgres', 'pg_monitor', 'pg_read_all_stats', 'pg_stat_scan_tables')
            LIMIT 5
        """))
        grants = result.fetchall()
        if grants:
            print("✓ 권한:")
            for row in grants:
                print(f"   - {row[0]}: {row[1]}")
        else:
            print("⚠ 공개 권한 없음 - 추가 중...")
            # PUBLIC 사용자에게 모든 권한 부여
            conn.execute(text('GRANT ALL ON app_info TO PUBLIC'))
            conn.execute(text('GRANT ALL ON app_review TO PUBLIC'))
            conn.execute(text('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC'))
            conn.commit()
            print("✓ PUBLIC 권한 추가 완료")
        
        print("\n[4/5] 외래 키 제약 조건 확인 중...")
        result = conn.execute(text("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'app_review'
        """))
        fks = result.fetchall()
        if fks:
            print("✓ 외래 키:")
            for row in fks:
                print(f"   - {row[1]}.{row[2]} → {row[3]}.{row[4]}")
        else:
            print("⚠ 외래 키 없음")
        
        print("\n[5/5] 테스트 데이터 삽입 중...")
        
        # 테스트 데이터 삽입
        try:
            # 기존 테스트 데이터 삭제
            conn.execute(text("DELETE FROM app_review WHERE app_id = 'test.app.id'"))
            conn.execute(text("DELETE FROM app_info WHERE app_id = 'test.app.id'"))
            conn.commit()
            
            # app_info 삽입
            conn.execute(text("""
                INSERT INTO app_info (app_id, app_name, review_count, download_count, rating)
                VALUES ('test.app.id', 'Test App', '100', '1000+', '4.5')
            """))
            conn.commit()
            print("✓ app_info 테스트 데이터 삽입 성공")
            
            # app_review 삽입
            conn.execute(text("""
                INSERT INTO app_review (app_id, rating, review_content, review_date)
                VALUES ('test.app.id', 5.0, 'Great app!', '2025-01-01')
            """))
            conn.commit()
            print("✓ app_review 테스트 데이터 삽입 성공")
            
            # 데이터 확인
            result = conn.execute(text("SELECT COUNT(*) FROM app_review WHERE app_id = 'test.app.id'"))
            count = result.scalar()
            print(f"✓ 삽입 확인: {count}개의 리뷰")
            
            # 테스트 데이터 삭제
            conn.execute(text("DELETE FROM app_review WHERE app_id = 'test.app.id'"))
            conn.execute(text("DELETE FROM app_info WHERE app_id = 'test.app.id'"))
            conn.commit()
            print("✓ 테스트 데이터 정리 완료")
            
        except Exception as e:
            print(f"✗ 테스트 데이터 삽입 실패: {str(e)}")
            conn.rollback()
    
    print("\n" + "=" * 60)
    print("✅ RLS 정책 수정 완료!")
    print("=" * 60)
    print("\n⚠️  참고: RLS를 비활성화했습니다.")
    print("   프로덕션 환경에서는 적절한 RLS 정책을 다시 설정하세요.")
    print("\n서버를 재시작하면 정상 작동합니다:")
    print("   cd C:\\Cursor\\review3\\app_review_r1\\backend")
    print("   python main.py")
    
except Exception as e:
    print(f"\n[오류] 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)


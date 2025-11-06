# -*- coding: utf-8 -*-
"""
데이터베이스 연결 및 데이터 저장 테스트
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import engine
from sqlalchemy import text

print("=" * 60)
print("Supabase 연결 및 데이터 저장 테스트")
print("=" * 60)

try:
    with engine.connect() as conn:
        print("\n[1/4] 데이터베이스 연결 테스트...")
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✓ 연결 성공: {version[:50]}...")
        
        print("\n[2/4] 기존 테스트 데이터 삭제...")
        conn.execute(text("DELETE FROM app_review WHERE app_id = 'test.app.id'"))
        conn.execute(text("DELETE FROM app_info WHERE app_id = 'test.app.id'"))
        conn.commit()
        print("✓ 삭제 완료")
        
        print("\n[3/4] 테스트 데이터 삽입...")
        
        # app_info 삽입
        conn.execute(text("""
            INSERT INTO app_info (app_id, app_name, review_count, download_count, rating)
            VALUES ('test.app.id', 'Test App', '100개', '1,000+', '4.5')
        """))
        conn.commit()
        print("✓ app_info 데이터 삽입 성공")
        
        # app_review 삽입
        conn.execute(text("""
            INSERT INTO app_review (app_id, rating, review_content, review_date)
            VALUES ('test.app.id', 5.0, '정말 좋은 앱입니다!', '2025-01-01')
        """))
        conn.commit()
        print("✓ app_review 데이터 삽입 성공")
        
        print("\n[4/4] 데이터 확인...")
        
        # app_info 확인
        result = conn.execute(text("SELECT COUNT(*) FROM app_info WHERE app_id = 'test.app.id'"))
        count = result.scalar()
        print(f"✓ app_info 데이터: {count}개")
        
        # app_review 확인
        result = conn.execute(text("SELECT COUNT(*) FROM app_review WHERE app_id = 'test.app.id'"))
        count = result.scalar()
        print(f"✓ app_review 데이터: {count}개")
        
        # 상세 데이터 확인
        result = conn.execute(text("SELECT * FROM app_info WHERE app_id = 'test.app.id'"))
        row = result.fetchone()
        print(f"\n✓ 삽입된 app_info:")
        print(f"   - ID: {row[0]}")
        print(f"   - App ID: {row[1]}")
        print(f"   - App Name: {row[2]}")
        print(f"   - Rating: {row[7]}")
        
        result = conn.execute(text("SELECT * FROM app_review WHERE app_id = 'test.app.id'"))
        row = result.fetchone()
        print(f"\n✓ 삽입된 app_review:")
        print(f"   - ID: {row[0]}")
        print(f"   - App ID: {row[1]}")
        print(f"   - Rating: {row[2]}")
        print(f"   - Content: {row[4]}")
        
        # 테스트 데이터 삭제
        print("\n[정리] 테스트 데이터 삭제 중...")
        conn.execute(text("DELETE FROM app_review WHERE app_id = 'test.app.id'"))
        conn.execute(text("DELETE FROM app_info WHERE app_id = 'test.app.id'"))
        conn.commit()
        print("✓ 테스트 데이터 정리 완료")
        
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 통과!")
    print("=" * 60)
    print("\nSupabase 데이터베이스가 정상적으로 작동합니다.")
    print("이제 애플리케이션에서 데이터를 저장할 수 있습니다.")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)


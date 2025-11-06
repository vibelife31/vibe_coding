-- Supabase 테이블 생성 스크립트
-- app_info 테이블
CREATE TABLE IF NOT EXISTS app_info (
    id SERIAL PRIMARY KEY,
    app_id VARCHAR UNIQUE NOT NULL,
    app_name VARCHAR NOT NULL,
    review_count VARCHAR,
    download_count VARCHAR,
    rating VARCHAR,
    overall_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_app_info_app_id ON app_info(app_id);

-- app_review 테이블
CREATE TABLE IF NOT EXISTS app_review (
    id SERIAL PRIMARY KEY,
    app_id VARCHAR NOT NULL,
    rating FLOAT,
    review_content TEXT,
    review_date VARCHAR,
    individual_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_review_app_info FOREIGN KEY (app_id) REFERENCES app_info(app_id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_app_review_app_id ON app_review(app_id);

-- 테이블 생성 확인
SELECT 'Tables created successfully!' AS status;


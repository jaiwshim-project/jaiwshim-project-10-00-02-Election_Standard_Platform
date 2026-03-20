-- Additional tables for Supabase integration
-- Created for blog articles, simplified competitors list, and app settings

-- ========== NEW TABLES ==========

-- blog_articles (블로그 게시물)
CREATE TABLE IF NOT EXISTS blog_articles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(500) NOT NULL,
    content         TEXT NOT NULL,
    category        VARCHAR(100),
    tags            TEXT[],
    author          VARCHAR(200),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_blog_articles_created ON blog_articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blog_articles_category ON blog_articles(category);

-- competitors_list (경쟁자 목록 - 간소화)
CREATE TABLE IF NOT EXISTS competitors_list (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(200) NOT NULL,
    party           VARCHAR(100),
    region          VARCHAR(100),
    approval_rate   DECIMAL(5,2),
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_competitors_name ON competitors_list(name);
CREATE INDEX IF NOT EXISTS idx_competitors_region ON competitors_list(region);

-- app_settings (앱 설정 - API 키 등)
CREATE TABLE IF NOT EXISTS app_settings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key             VARCHAR(255) UNIQUE NOT NULL,
    value           TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_settings_key ON app_settings(key);

-- ========== MODIFY candidates TABLE ==========
-- Add columns to store app configuration if not exists
ALTER TABLE candidates
ADD COLUMN IF NOT EXISTS gemini_api_key VARCHAR(500),
ADD COLUMN IF NOT EXISTS gemini_model VARCHAR(100) DEFAULT 'gemini-2.0-flash';

-- ========== INITIAL DATA ==========
-- Sample blog articles
INSERT INTO blog_articles (title, content, category, tags)
VALUES
  ('정치 전략 수립 완료', '2024년 선거 전략 수립이 완료되었습니다.', '전략', ARRAY['선거', '전략']),
  ('여론조사 결과 발표', '최신 여론조사 결과를 발표합니다.', '여론조사', ARRAY['여론', '분석'])
ON CONFLICT DO NOTHING;

-- Sample competitors
INSERT INTO competitors_list (name, party, region, approval_rate, notes)
VALUES
  ('경쟁자A', '국민의힘', '서울', 42.5, '강점: 경제 정책'),
  ('경쟁자B', '더불어민주당', '서울', 38.2, '강점: 복지 정책')
ON CONFLICT DO NOTHING;

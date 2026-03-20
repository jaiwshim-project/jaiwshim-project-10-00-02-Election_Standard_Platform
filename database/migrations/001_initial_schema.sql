-- Election Moon Un Platform — Initial Schema
-- PostgreSQL with pgvector support

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ========== ENUM TYPES ==========
CREATE TYPE candidate_status AS ENUM ('active','inactive','candidate','elected','defeated');
CREATE TYPE party_affiliation AS ENUM ('더불어민주당','국민의힘','정의당','무소속','기타');
CREATE TYPE report_type AS ENUM ('polling','news_analysis','sns_analysis','competitor_report','voter_survey');

-- ========== MAIN TABLES ==========

-- candidates (후보자)
CREATE TABLE candidates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    party           party_affiliation NOT NULL DEFAULT '무소속',
    status          candidate_status NOT NULL DEFAULT 'active',
    district        VARCHAR(200),
    region          VARCHAR(100),
    bio             TEXT,
    meta            JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_candidates_name ON candidates(name);
CREATE INDEX idx_candidates_region ON candidates(region);

-- policies (공약) with vector embeddings
CREATE TABLE policies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    category        VARCHAR(100),
    embedding       vector(1536),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_policies_candidate ON policies(candidate_id);
CREATE INDEX idx_policies_embedding ON policies
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- competitors (경쟁자 매핑)
CREATE TABLE competitors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id),
    competitor_id   UUID NOT NULL REFERENCES candidates(id),
    election_year   INTEGER,
    strength_score  DECIMAL(5,2),
    CONSTRAINT unique_competitor UNIQUE (candidate_id, competitor_id, election_year)
);
CREATE INDEX idx_competitors_candidate ON competitors(candidate_id);

-- reports (분석 리포트)
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID REFERENCES candidates(id),
    title           VARCHAR(500) NOT NULL,
    report_type     report_type NOT NULL,
    content         TEXT,
    file_url        TEXT,
    is_processed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_reports_candidate ON reports(candidate_id);
CREATE INDEX idx_reports_processed ON reports(is_processed);

-- report_chunks (PDF 청킹 + 벡터화)
CREATE TABLE report_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id       UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    chunk_text      TEXT NOT NULL,
    embedding       vector(1536),
    page_number     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_chunks_report ON report_chunks(report_id);
CREATE INDEX idx_chunks_embedding ON report_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- voters (유권자 분석)
CREATE TABLE voters (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district        VARCHAR(200) NOT NULL,
    age_group       VARCHAR(20),
    political_lean  VARCHAR(50),
    concern_issues  TEXT[],
    sentiment_score DECIMAL(5,2),
    survey_date     DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_voters_district ON voters(district);
CREATE INDEX idx_voters_survey_date ON voters(survey_date);

-- analytics (판세 수치)
CREATE TABLE analytics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID REFERENCES candidates(id),
    metric_type     VARCHAR(100) NOT NULL,
    metric_value    DECIMAL(15,4),
    district        VARCHAR(200),
    measured_at     TIMESTAMPTZ NOT NULL,
    source_name     VARCHAR(200),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_analytics_candidate ON analytics(candidate_id);
CREATE INDEX idx_analytics_measured_at ON analytics(measured_at);

-- chat_sessions (AI 채팅)
CREATE TABLE chat_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_token   VARCHAR(500) UNIQUE NOT NULL,
    candidate_id    UUID REFERENCES candidates(id),
    message_count   INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant','system')),
    content         TEXT NOT NULL,
    intent          VARCHAR(100),
    retrieved_chunks UUID[],
    tokens_used     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_messages_session ON chat_messages(session_id);

-- news_feed (실시간 뉴스)
CREATE TABLE news_feed (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID REFERENCES candidates(id),
    title           VARCHAR(1000) NOT NULL,
    content         TEXT,
    url             TEXT UNIQUE,
    source_name     VARCHAR(200),
    sentiment       VARCHAR(20),
    sentiment_score DECIMAL(5,2),
    embedding       vector(1536),
    published_at    TIMESTAMPTZ,
    is_processed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_news_candidate ON news_feed(candidate_id);
CREATE INDEX idx_news_processed ON news_feed(is_processed);
CREATE INDEX idx_news_embedding ON news_feed
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- api_keys (인증)
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash        VARCHAR(500) UNIQUE NOT NULL,
    candidate_id    UUID REFERENCES candidates(id),
    scopes          TEXT[] DEFAULT ARRAY['read'],
    rate_limit      INTEGER DEFAULT 1000,
    is_active       BOOLEAN DEFAULT TRUE,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- Vector search for report chunks
CREATE OR REPLACE FUNCTION match_report_chunks(
    query_embedding  vector(1536),
    match_count      int DEFAULT 5,
    candidate_id     uuid DEFAULT NULL
)
RETURNS TABLE (
    id              uuid,
    report_id       uuid,
    chunk_text      text,
    page_number     int,
    similarity      float,
    report_title    text,
    report_type     text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.id,
        rc.report_id,
        rc.chunk_text,
        rc.page_number,
        1 - (rc.embedding <=> query_embedding) AS similarity,
        r.title AS report_title,
        r.report_type::text
    FROM report_chunks rc
    JOIN reports r ON rc.report_id = r.id
    WHERE
        (candidate_id IS NULL OR r.candidate_id = match_report_chunks.candidate_id)
    ORDER BY rc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Initial sample data
INSERT INTO candidates (name, party, district, region) VALUES
('오세훈', '국민의힘', '서울시장', '서울'),
('조은희', '더불어민주당', '서울시장', '서울');

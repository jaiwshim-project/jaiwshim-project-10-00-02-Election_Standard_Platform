-- Phase 1: Camp Model 마이그레이션
-- 링크 기반 공동 사용 모델을 위한 테이블 구조

-- ========== 1. candidates 테이블 수정 ==========
-- camp_code: 캠프별 고유 링크 코드 (예: kim-dongjaek-2024)
-- admin_password: 관리자 대시보드 접근용 해시된 비밀번호
-- is_active: 캠프 활성화 여부

ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS camp_code VARCHAR(100) UNIQUE NOT NULL DEFAULT '';

ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS admin_password VARCHAR(255) DEFAULT '';

ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- camp_code로 빠른 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_candidates_camp_code ON candidates(camp_code);


-- ========== 2. camp_members 테이블 생성 ==========
-- 캠프 멤버 목록 (관리자가 관리)

CREATE TABLE IF NOT EXISTS camp_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  role VARCHAR(100),                -- '후보자' | '캠프 리더' | '스탭' | '기자' | '자원봉사자' 등
  phone VARCHAR(50),
  email VARCHAR(200),
  notes TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_camp_members_candidate ON camp_members(candidate_id);
CREATE INDEX IF NOT EXISTS idx_camp_members_active ON camp_members(is_active);


-- ========== 3. shared_files 테이블 생성 ==========
-- Supabase Storage 메타데이터 + 파일 관리

CREATE TABLE IF NOT EXISTS shared_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  file_type VARCHAR(20) NOT NULL,                    -- 'type-1' ~ 'type-8'
  file_name VARCHAR(500) NOT NULL,
  storage_path TEXT NOT NULL,                        -- Supabase Storage 경로
  file_size BIGINT,
  mime_type VARCHAR(200),
  uploaded_by_name VARCHAR(200),                     -- 업로드한 관리자 이름
  upload_date TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shared_files_candidate ON shared_files(candidate_id);
CREATE INDEX IF NOT EXISTS idx_shared_files_type ON shared_files(candidate_id, file_type);
CREATE INDEX IF NOT EXISTS idx_shared_files_active ON shared_files(is_active);


-- ========== 4. blog_articles, competitors_list, app_settings에 candidate_id 추가 ==========

ALTER TABLE blog_articles
  ADD COLUMN IF NOT EXISTS candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE competitors_list
  ADD COLUMN IF NOT EXISTS candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE app_settings
  ADD COLUMN IF NOT EXISTS candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_blog_articles_candidate ON blog_articles(candidate_id);
CREATE INDEX IF NOT EXISTS idx_competitors_list_candidate ON competitors_list(candidate_id);
CREATE INDEX IF NOT EXISTS idx_app_settings_candidate ON app_settings(candidate_id);


-- ========== 5. 샘플 데이터 ==========
-- 테스트용 캠프 데이터 (선택사항)

-- 기존 후보자에 camp_code 할당 (비어있는 경우만)
UPDATE candidates
SET camp_code = LOWER(REPLACE(REPLACE(name, ' ', '-'), '시', '')) || '-2024'
WHERE camp_code = '' OR camp_code IS NULL;

-- 예시:
-- INSERT INTO candidates (name, party, camp_code, admin_password, is_active)
-- VALUES ('김철수', '국민의힘', 'kim-dongjaek-2024', '$2b$10$...bcrypt_hash...', TRUE);

-- INSERT INTO camp_members (candidate_id, name, role, email, phone)
-- SELECT id, '김철수', '후보자', 'kim@example.com', '010-1234-5678'
-- FROM candidates WHERE camp_code = 'kim-dongjaek-2024';

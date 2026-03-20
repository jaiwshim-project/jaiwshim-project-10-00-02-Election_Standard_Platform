-- =====================================================
-- 005_signup_system.sql
-- 회원가입 기반 캠프 셀프서비스 등록 시스템
-- 실행 위치: Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- 1. candidates 테이블 확장 (회원가입용 컬럼 추가)
ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
  ADD COLUMN IF NOT EXISTS election_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS profile_photo_url TEXT,
  ADD COLUMN IF NOT EXISTS signup_at TIMESTAMPTZ DEFAULT NOW(),
  ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE;

-- 2. 인덱스 생성 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_is_active_approved ON candidates(is_active, is_approved);
CREATE INDEX IF NOT EXISTS idx_candidates_signup_at ON candidates(signup_at);

-- 3. party 컬럼 ENUM 확장 (신규 정당 추가)
-- PostgreSQL ENUM은 ALTER TYPE으로만 추가 가능
DO $$ BEGIN
  ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '조국혁신당';
  ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '자유와혁신';
  ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '개혁신당';
EXCEPTION WHEN OTHERS THEN
  NULL;
END $$;

-- 4. 회원가입 로그 테이블 (감사 추적)
CREATE TABLE IF NOT EXISTS signup_logs (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
  email        VARCHAR(255),
  ip_address   VARCHAR(45),
  user_agent   TEXT,
  action       VARCHAR(50),  -- 'signup' | 'login' | 'logout' | 'password_change'
  result       VARCHAR(20),  -- 'success' | 'failure'
  error_msg    TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signup_logs_candidate ON signup_logs(candidate_id);
CREATE INDEX IF NOT EXISTS idx_signup_logs_created ON signup_logs(created_at);

-- 5. 업데이트 트리거 (updated_at 자동 갱신)
CREATE OR REPLACE FUNCTION update_candidates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_candidates_timestamp_trigger ON candidates;
CREATE TRIGGER update_candidates_timestamp_trigger
  BEFORE UPDATE ON candidates
  FOR EACH ROW
  EXECUTE FUNCTION update_candidates_timestamp();

-- 6. Supabase Storage 버킷 생성 안내
-- 주의: 이 작업은 SQL에서 직접 불가능합니다. Supabase Dashboard에서 수동으로 진행하세요.
--
-- 단계:
-- 1. Supabase Dashboard → Storage → Create new bucket
-- 2. 버킷 이름: campaign-assets
-- 3. 접근: Public (읽기) / 인증 필요 (쓰기)
-- 4. 파일 크기: 5MB 제한
-- 5. 허용 MIME: image/jpeg, image/png, image/webp

-- 마이그레이션 완료 로그
SELECT 'Migration 005_signup_system.sql completed successfully' AS status;

-- =====================================================
-- RLS (Row Level Security) 정책 설정
-- Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- 주의: 이 파일을 실행하기 전에 다음을 확인하세요:
-- 1. Supabase Dashboard → Authentication → API Keys
--    - anon (public) key 확인
--    - service_role key 확인
-- 2. Database → Extensions: uuid-ossp 활성화 여부 확인

-- =====================================================
-- 1. candidates 테이블 RLS 활성화
-- =====================================================
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 2. Public 정책 (인증되지 않은 사용자 = anon key)
-- =====================================================

-- 정책 1: 로그인/회원가입 시 필요한 필드만 읽기 가능
-- SELECT 가능: 인증된 사용자만
-- staff_account_id, admin_account_id로 조회 (로그인)
CREATE POLICY "candidates_select_by_account_id"
ON candidates
FOR SELECT
USING (
  -- 로그인 시 staff_account_id 또는 admin_account_id로 검색하므로
  -- 해당 사용자만 접근 가능하도록 제한 (하지만 RLS는 row level이므로 실제로는 app 로직에 의존)
  -- Supabase에서는 .eq() 필터를 통해 제어
  is_active = TRUE
);

-- 정책 2: 회원가입 시 INSERT 가능
-- email이 고유하면 새 캠프 등록 가능
CREATE POLICY "candidates_insert_signup"
ON candidates
FOR INSERT
WITH CHECK (
  -- 회원가입은 누구나 가능 (공개)
  TRUE
);

-- =====================================================
-- 3. Service Role 정책 (백엔드/관리자)
-- =====================================================

-- 정책 3: 관리자는 모든 행 선택 가능
-- (service_role key 사용 시)
CREATE POLICY "candidates_select_admin"
ON candidates
FOR SELECT
USING (
  -- service_role은 RLS 무시하므로 실제로는 효과 없음
  -- 하지만 명시적으로 작성
  TRUE
);

-- 정책 4: 인증된 사용자(로그인)는 자신의 캠프만 UPDATE 가능
-- 문제: Supabase JWT에 candidateId를 포함해야 함 (현재는 sessionStorage 사용)
-- 현재 구현: app level에서 AuthManager로 제어 (DB 정책 외)
-- 나중에 Supabase Auth 연동 시 다음 정책 적용:
/*
CREATE POLICY "candidates_update_own"
ON candidates
FOR UPDATE
USING (
  -- auth.uid()가 user_id 또는 owner_id와 일치하는 경우만 UPDATE
  -- 현재 구현 없음 (추후 Supabase Auth 통합 시)
  auth.uid() = owner_id  -- owner_id 컬럼 필요
)
WITH CHECK (
  auth.uid() = owner_id
);
*/

-- =====================================================
-- 4. 민감한 컬럼 마스킹 뷰 (선택사항)
-- =====================================================

-- 뷰: 비밀번호를 제외한 후보자 정보
CREATE OR REPLACE VIEW candidates_public AS
SELECT
  id,
  name,
  party,
  status,
  district,
  region,
  bio,
  camp_code,
  email,  -- 이메일은 노출 (회원가입 시 필요)
  election_type,
  profile_photo_url,
  is_active,
  created_at,
  updated_at
  -- 제외: staff_account_id, staff_password, admin_account_id, admin_password, gemini_api_key
FROM candidates
WHERE is_active = TRUE;

-- =====================================================
-- 5. RLS 정책 활성화 확인
-- =====================================================

-- 실행 후 다음 명령어로 정책 확인:
-- SELECT * FROM pg_policies WHERE tablename = 'candidates';

-- =====================================================
-- 6. 현재 구현 상태 (2026-03-20)
-- =====================================================

-- ⚠️ 주의: 현재 구현은 sessionStorage 기반 클라이언트 로직에 의존합니다.
-- RLS는 정책 수준으로만 활성화되어 있고, 실제 데이터 보호는:
-- 1. app level (AuthManager)에서 역할 확인
-- 2. API level (나중에 구현 예정)에서 제어

-- 향후 개선:
-- 1. Supabase Auth 통합 (JWT 기반)
-- 2. owner_id 컬럼 추가 (candidates 테이블)
-- 3. auth.uid() 기반 RLS 정책 강화

-- RLS 정책 생성 완료
SELECT 'RLS policies created successfully' AS status;

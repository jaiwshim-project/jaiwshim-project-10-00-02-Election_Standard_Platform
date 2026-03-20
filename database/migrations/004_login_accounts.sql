-- 004_login_accounts.sql
-- 로그인 기반 캠프 공유 계정 모델
-- candidates 테이블에 스태프/관리자 계정 정보 추가

-- 스태프 계정 및 비밀번호 컬럼 추가
ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS staff_account_id VARCHAR(100) UNIQUE,
  ADD COLUMN IF NOT EXISTS staff_password VARCHAR(255);

-- 관리자 계정 ID 컬럼 추가 (admin_password는 기존 컬럼 재활용)
ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS admin_account_id VARCHAR(100) UNIQUE;

-- 기존 데이터 마이그레이션: camp_code가 있으면 staff_account_id로 사용
-- (수동 실행 시 필요하면 아래 쿼리 실행)
-- UPDATE candidates SET staff_account_id = camp_code WHERE camp_code IS NOT NULL;
-- UPDATE candidates SET admin_account_id = 'admin_' || camp_code WHERE camp_code IS NOT NULL;

-- 예제 데이터 (선택사항 - 실제 운영시 제거)
-- INSERT INTO candidates (name, party, district, region, staff_account_id, staff_password, admin_account_id, admin_password)
-- VALUES (
--   '김동재', 'dem', '서울 종로구', '서울',
--   'kim2024', 'dc2e0f1e0019d0c0f1b5e9f5c5c9d7c5',  -- SHA-256('staff123')
--   'admin_kim2024', 'a4c6d4a5e7c5b9c9c5c5c5c5c5c5c5c5'  -- SHA-256('admin456')
-- )
-- ON CONFLICT DO NOTHING;

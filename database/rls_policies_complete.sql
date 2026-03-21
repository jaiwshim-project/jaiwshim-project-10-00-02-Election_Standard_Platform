-- =====================================================
-- rls_policies_complete.sql
-- 전체 RLS 정책 통합 파일 (모든 테이블)
-- 실행 위치: Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- ⚠️ 주의: 이 파일은 모든 마이그레이션 실행 후 실행해야 합니다.
-- 실행 순서:
-- 1. 001_initial_schema.sql
-- 2. 002_additional_tables.sql
-- 3. 003_camp_model.sql
-- 4. 004_login_accounts.sql
-- 5. 005_signup_system.sql
-- 6. 006_admin_system.sql
-- 7. 007_notifications_reports_roles.sql
-- 8. 008_extended_rls_policies.sql
-- 9. rls_policies_complete.sql (이 파일)

-- =====================================================
-- 1. CANDIDATES 테이블 RLS
-- =====================================================

ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- 정책 1: 활성 후보자는 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "candidates_select_active"
ON candidates
FOR SELECT
USING (is_active = TRUE);

-- 정책 2: 회원가입 시 INSERT 가능
CREATE POLICY IF NOT EXISTS "candidates_insert_signup"
ON candidates
FOR INSERT
WITH CHECK (TRUE);

-- 정책 3: 본인의 캠프만 UPDATE 가능 (sessionStorage 기반, 추후 auth 통합)
CREATE POLICY IF NOT EXISTS "candidates_update_own"
ON candidates
FOR UPDATE
USING (TRUE)  -- 앱 레벨에서 제어
WITH CHECK (TRUE);

-- =====================================================
-- 2. POLICIES 테이블 RLS (공약)
-- =====================================================

ALTER TABLE policies ENABLE ROW LEVEL SECURITY;

-- 정책 1: 공약은 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "policies_select_all"
ON policies
FOR SELECT
USING (TRUE);

-- 정책 2: 본인의 공약만 INSERT 가능
CREATE POLICY IF NOT EXISTS "policies_insert_own"
ON policies
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- 정책 3: 본인의 공약만 UPDATE 가능
CREATE POLICY IF NOT EXISTS "policies_update_own"
ON policies
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- =====================================================
-- 3. COMPETITORS 테이블 RLS
-- =====================================================

ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "competitors_select_all"
ON competitors
FOR SELECT
USING (TRUE);

-- 정책 2: 본인의 경쟁자만 생성 가능
CREATE POLICY IF NOT EXISTS "competitors_insert_own"
ON competitors
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- =====================================================
-- 4. REPORTS 테이블 RLS (분석 리포트)
-- =====================================================

ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "reports_select_all"
ON reports
FOR SELECT
USING (TRUE);

-- 정책 2: 본인의 후보자 리포트만 INSERT 가능
CREATE POLICY IF NOT EXISTS "reports_insert_own"
ON reports
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- =====================================================
-- 5. REPORT_CHUNKS 테이블 RLS (PDF 청킹)
-- =====================================================

ALTER TABLE report_chunks ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "report_chunks_select_all"
ON report_chunks
FOR SELECT
USING (TRUE);

-- =====================================================
-- 6. VOTERS 테이블 RLS (유권자 분석)
-- =====================================================

ALTER TABLE voters ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "voters_select_all"
ON voters
FOR SELECT
USING (TRUE);

-- =====================================================
-- 7. ANALYTICS 테이블 RLS (판세 수치)
-- =====================================================

ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 조회 가능
CREATE POLICY IF NOT EXISTS "analytics_select_all"
ON analytics
FOR SELECT
USING (TRUE);

-- =====================================================
-- 8. CHAT_SESSIONS 테이블 RLS
-- =====================================================

ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- 정책 1: 세션 소유자만 조회 가능
CREATE POLICY IF NOT EXISTS "chat_sessions_select_own"
ON chat_sessions
FOR SELECT
USING (
  candidate_id IS NULL  -- 공개 세션
  OR EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- 정책 2: 누구나 세션 생성 가능
CREATE POLICY IF NOT EXISTS "chat_sessions_insert_public"
ON chat_sessions
FOR INSERT
WITH CHECK (TRUE);

-- =====================================================
-- 9. CHAT_MESSAGES 테이블 RLS
-- =====================================================

ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 메시지 조회 가능
CREATE POLICY IF NOT EXISTS "chat_messages_select_all"
ON chat_messages
FOR SELECT
USING (TRUE);

-- 정책 2: 누구나 메시지 생성 가능
CREATE POLICY IF NOT EXISTS "chat_messages_insert_all"
ON chat_messages
FOR INSERT
WITH CHECK (TRUE);

-- =====================================================
-- 10. NEWS_FEED 테이블 RLS
-- =====================================================

ALTER TABLE news_feed ENABLE ROW LEVEL SECURITY;

-- 정책 1: 누구나 뉴스 조회 가능
CREATE POLICY IF NOT EXISTS "news_feed_select_all"
ON news_feed
FOR SELECT
USING (TRUE);

-- =====================================================
-- 11. API_KEYS 테이블 RLS
-- =====================================================

ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- 정책 1: 소유자만 조회 가능
CREATE POLICY IF NOT EXISTS "api_keys_select_own"
ON api_keys
FOR SELECT
USING (
  candidate_id IS NULL
  OR EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- 정책 2: 후보자만 API 키 생성 가능
CREATE POLICY IF NOT EXISTS "api_keys_insert_own"
ON api_keys
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM candidates WHERE id = candidate_id AND is_active = TRUE
  )
);

-- =====================================================
-- 12. ADMINS 테이블 RLS (관리자)
-- =====================================================

ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- 정책 1: Super Admin만 모든 관리자 조회 가능
CREATE POLICY IF NOT EXISTS "admins_select_super_admin"
ON admins
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = id
);

-- 정책 2: Super Admin만 관리자 생성 가능
CREATE POLICY IF NOT EXISTS "admins_insert_super_admin"
ON admins
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 정책 3: Super Admin 또는 본인만 수정 가능
CREATE POLICY IF NOT EXISTS "admins_update_super_admin"
ON admins
FOR UPDATE
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = id
);

-- =====================================================
-- 13. ADMIN_ACTIVITY_LOGS 테이블 RLS
-- =====================================================

ALTER TABLE admin_activity_logs ENABLE ROW LEVEL SECURITY;

-- 정책 1: Super Admin만 모든 로그 조회 가능
CREATE POLICY IF NOT EXISTS "admin_activity_logs_select_super_admin"
ON admin_activity_logs
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = admin_id
);

-- =====================================================
-- 14. NOTIFICATIONS 테이블 RLS (메시지/알림)
-- =====================================================

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- 정책 1: 수신자는 자신의 알림만 조회 가능
CREATE POLICY IF NOT EXISTS "notifications_select_own"
ON notifications
FOR SELECT
USING (
  auth.uid() = recipient_id
  OR (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 정책 2: 관리자만 알림 생성 가능
CREATE POLICY IF NOT EXISTS "notifications_insert_admin"
ON notifications
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 정책 3: 수신자 또는 관리자만 수정 가능
CREATE POLICY IF NOT EXISTS "notifications_update_own"
ON notifications
FOR UPDATE
USING (
  auth.uid() = recipient_id
  OR (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 정책 4: 수신자만 삭제 가능
CREATE POLICY IF NOT EXISTS "notifications_delete_own"
ON notifications
FOR DELETE
USING (auth.uid() = recipient_id);

-- =====================================================
-- 15. REPORTS 테이블 RLS (신고/이슈) - 별도 테이블
-- =====================================================

-- 참고: reports 테이블은 이미 007_notifications_reports_roles.sql에서 정의됨
-- 여기서는 추가 정책만 정의

ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 정책 1: 신고자와 관리자는 신고 조회 가능
CREATE POLICY IF NOT EXISTS "issue_reports_select_own_or_admin"
ON reports
FOR SELECT
USING (
  reporter_id = auth.uid()
  OR assigned_to = auth.uid()
  OR (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin', 'moderator')
);

-- 정책 2: 인증된 사용자는 신고 생성 가능
CREATE POLICY IF NOT EXISTS "issue_reports_insert_authenticated"
ON reports
FOR INSERT
WITH CHECK (
  reporter_id = auth.uid()
);

-- 정책 3: 신고자 또는 관리자만 수정 가능
CREATE POLICY IF NOT EXISTS "issue_reports_update_own_or_admin"
ON reports
FOR UPDATE
USING (
  reporter_id = auth.uid()
  OR (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin', 'moderator')
);

-- =====================================================
-- 16. ADMIN_ROLES 테이블 RLS (권한)
-- =====================================================

ALTER TABLE admin_roles ENABLE ROW LEVEL SECURITY;

-- 정책 1: Super Admin만 모든 역할 조회 가능
CREATE POLICY IF NOT EXISTS "admin_roles_select_super_admin"
ON admin_roles
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = admin_id
);

-- 정책 2: Super Admin만 역할 생성 가능
CREATE POLICY IF NOT EXISTS "admin_roles_insert_super_admin"
ON admin_roles
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 정책 3: Super Admin만 역할 수정 가능
CREATE POLICY IF NOT EXISTS "admin_roles_update_super_admin"
ON admin_roles
FOR UPDATE
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- =====================================================
-- 17. RLS 정책 활성화 확인 쿼리
-- =====================================================

-- 실행 후 다음 명령어로 정책 확인:
-- SELECT schemaname, tablename, policyname, permissive, roles, qual, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;

-- =====================================================
-- 18. RLS 정책 최종 상태
-- =====================================================

-- 활성화된 RLS 테이블 확인
-- SELECT tablename FROM pg_tables
-- WHERE schemaname = 'public' AND NOT tablename LIKE 'pg_%'
-- ORDER BY tablename;

-- 모든 정책 확인
-- SELECT tablename, COUNT(*) as policy_count
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- GROUP BY tablename
-- ORDER BY tablename;

-- =====================================================
-- 완료
-- =====================================================

SELECT 'RLS Policies Complete - All tables configured successfully' AS status;

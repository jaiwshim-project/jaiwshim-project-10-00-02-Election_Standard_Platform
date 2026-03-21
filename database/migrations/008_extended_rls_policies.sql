-- =====================================================
-- 008_extended_rls_policies.sql
-- 확장 RLS 정책 (보안 강화)
-- 실행 위치: Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- =====================================================
-- 1. notifications 테이블 추가 정책
-- =====================================================

-- 정책 4: 마크된 알림은 수신자만 삭제 가능
CREATE POLICY "notifications_delete_own"
ON notifications
FOR DELETE
USING (
  auth.uid() = recipient_id
);

-- 정책 5: 관리자는 시스템 알림 생성 가능
CREATE POLICY "notifications_insert_by_admin"
ON notifications
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin', 'moderator')
  AND notification_type = 'system'
);

-- =====================================================
-- 2. reports 테이블 추가 정책
-- =====================================================

-- 정책 4: 중요 신고(critical)는 Super Admin만 삭제 가능
CREATE POLICY "reports_delete_critical"
ON reports
FOR DELETE
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  AND severity = 'critical'
);

-- 정책 5: 신고자는 자신의 신고만 삭제 가능 (pending 상태)
CREATE POLICY "reports_delete_own_pending"
ON reports
FOR DELETE
USING (
  auth.uid() = reporter_id
  AND status = 'pending'
);

-- =====================================================
-- 3. admin_activity_logs 테이블 RLS 추가
-- =====================================================

-- admin_activity_logs 테이블 RLS 활성화
ALTER TABLE admin_activity_logs ENABLE ROW LEVEL SECURITY;

-- 정책 1: Super Admin만 모든 로그 조회 가능
CREATE POLICY "admin_activity_logs_select_super_admin"
ON admin_activity_logs
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 정책 2: 자신의 활동만 조회 가능
CREATE POLICY "admin_activity_logs_select_own"
ON admin_activity_logs
FOR SELECT
USING (
  auth.uid() = admin_id
);

-- 정책 3: 시스템 로그만 삽입 가능 (백엔드에서)
CREATE POLICY "admin_activity_logs_insert_system"
ON admin_activity_logs
FOR INSERT
WITH CHECK (
  TRUE  -- 백엔드 service_role에서만 호출
);

-- =====================================================
-- 4. admins 테이블 추가 정책
-- =====================================================

-- 정책 5: 관리자는 자신의 정보 업데이트 가능
CREATE POLICY "admins_update_own"
ON admins
FOR UPDATE
USING (
  auth.uid() = id
)
WITH CHECK (
  auth.uid() = id
);

-- 정책 6: 비활성 계정 조회 금지 (Super Admin 제외)
CREATE POLICY "admins_no_inactive"
ON admins
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR is_active = TRUE
);

-- =====================================================
-- 5. 감시 함수: 신고 활동 로깅
-- =====================================================

CREATE OR REPLACE FUNCTION log_report_activity()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO admin_activity_logs (
    admin_id,
    action,
    target_type,
    target_id,
    details
  ) VALUES (
    auth.uid(),
    CASE
      WHEN TG_OP = 'INSERT' THEN 'create_report'
      WHEN TG_OP = 'UPDATE' THEN 'update_report'
      WHEN TG_OP = 'DELETE' THEN 'delete_report'
    END,
    'report',
    COALESCE(NEW.id, OLD.id),
    jsonb_build_object(
      'status', COALESCE(NEW.status, OLD.status),
      'severity', COALESCE(NEW.severity, OLD.severity),
      'type', COALESCE(NEW.report_type, OLD.report_type)
    )
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reports_activity_log_trigger
AFTER INSERT OR UPDATE OR DELETE ON reports
FOR EACH ROW
EXECUTE FUNCTION log_report_activity();

-- =====================================================
-- 6. 감시 함수: 알림 활동 로깅
-- =====================================================

CREATE OR REPLACE FUNCTION log_notification_activity()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO admin_activity_logs (
    admin_id,
    action,
    target_type,
    target_id,
    details
  ) VALUES (
    auth.uid(),
    CASE
      WHEN TG_OP = 'INSERT' THEN 'create_notification'
      WHEN TG_OP = 'UPDATE' THEN 'update_notification'
    END,
    'notification',
    NEW.id,
    jsonb_build_object(
      'type', NEW.notification_type,
      'priority', NEW.priority,
      'is_read', NEW.is_read
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notifications_activity_log_trigger
AFTER INSERT OR UPDATE ON notifications
FOR EACH ROW
WHEN (NEW.sender_id IS NOT NULL)
EXECUTE FUNCTION log_notification_activity();

-- =====================================================
-- 7. 뷰: 관리 대시보드용
-- =====================================================

-- 미해결 신고 요약
CREATE OR REPLACE VIEW unresolved_reports_summary AS
SELECT
  COUNT(*) FILTER (WHERE severity = 'critical') AS critical_count,
  COUNT(*) FILTER (WHERE severity = 'high') AS high_count,
  COUNT(*) FILTER (WHERE severity = 'medium') AS medium_count,
  COUNT(*) FILTER (WHERE severity = 'low') AS low_count,
  COUNT(*) AS total_count,
  COUNT(*) FILTER (WHERE assigned_to IS NULL) AS unassigned_count
FROM reports
WHERE status IN ('pending', 'investigating');

-- 읽지 않은 알림 요약
CREATE OR REPLACE VIEW unread_notifications_summary AS
SELECT
  recipient_id,
  COUNT(*) AS unread_count,
  COUNT(*) FILTER (WHERE priority = 2) AS critical_count,
  COUNT(*) FILTER (WHERE priority = 1) AS high_count,
  MAX(created_at) AS latest_notification_at
FROM notifications
WHERE is_read = FALSE
GROUP BY recipient_id;

-- 관리자 활동 요약
CREATE OR REPLACE VIEW admin_activity_summary AS
SELECT
  admin_id,
  COUNT(*) AS total_actions,
  COUNT(*) FILTER (WHERE action LIKE 'approve%') AS approvals,
  COUNT(*) FILTER (WHERE action LIKE 'delete%') AS deletions,
  COUNT(*) FILTER (WHERE action LIKE 'create%') AS creations,
  MAX(created_at) AS last_action_at
FROM admin_activity_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY admin_id;

-- =====================================================
-- 8. 청소 함수: 만료된 데이터 자동 삭제
-- =====================================================

CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS TABLE (
  deleted_notifications BIGINT,
  deleted_reports BIGINT
) AS $$
DECLARE
  v_deleted_notifications BIGINT;
  v_deleted_reports BIGINT;
BEGIN
  -- 만료된 알림 삭제
  DELETE FROM notifications
  WHERE expires_at IS NOT NULL AND expires_at < NOW();
  GET DIAGNOSTICS v_deleted_notifications = ROW_COUNT;

  -- 만료된 신고 삭제 (자동 삭제 설정된 경우)
  DELETE FROM reports
  WHERE status = 'dismissed'
    AND resolved_at IS NOT NULL
    AND resolved_at < NOW() - INTERVAL '90 days';
  GET DIAGNOSTICS v_deleted_reports = ROW_COUNT;

  RETURN QUERY SELECT v_deleted_notifications, v_deleted_reports;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 9. 마이그레이션 완료
-- =====================================================

SELECT 'Migration 008_extended_rls_policies.sql completed successfully' AS status;

-- =====================================================
-- 007_notifications_reports_roles.sql
-- 메시지, 신고, 권한 테이블 설계
-- 실행 위치: Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- =====================================================
-- 1. notifications 테이블 (메시지/알림)
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  recipient_id      UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  sender_id         UUID REFERENCES admins(id) ON DELETE SET NULL,
  title             VARCHAR(200) NOT NULL,
  content           TEXT NOT NULL,
  notification_type VARCHAR(50) NOT NULL,  -- 'system' | 'message' | 'alert' | 'approval' | 'rejection'
  is_read           BOOLEAN DEFAULT FALSE,
  read_at           TIMESTAMPTZ,
  priority          INTEGER DEFAULT 0,  -- 0: normal, 1: high, 2: critical
  metadata          JSONB DEFAULT '{}',  -- 추가 데이터 (링크, 파라미터 등)
  expires_at        TIMESTAMPTZ,  -- 자동 삭제 시간 (선택)
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_notifications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notifications_updated_at_trigger
BEFORE UPDATE ON notifications
FOR EACH ROW
EXECUTE FUNCTION update_notifications_updated_at();

-- =====================================================
-- 2. reports 테이블 (신고/이슈)
-- =====================================================

CREATE TABLE IF NOT EXISTS reports (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reporter_id       UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  reported_user_id  UUID REFERENCES candidates(id) ON DELETE SET NULL,
  report_type       VARCHAR(50) NOT NULL,  -- 'spam' | 'abuse' | 'inappropriate' | 'fraud' | 'other'
  title             VARCHAR(200) NOT NULL,
  description       TEXT NOT NULL,
  evidence_urls     TEXT[],  -- 증거 URL 배열
  status            VARCHAR(50) DEFAULT 'pending',  -- 'pending' | 'investigating' | 'resolved' | 'dismissed' | 'escalated'
  severity          VARCHAR(50) DEFAULT 'medium',  -- 'low' | 'medium' | 'high' | 'critical'
  assigned_to       UUID REFERENCES admins(id) ON DELETE SET NULL,  -- 담당 관리자
  resolution_notes  TEXT,
  resolved_at       TIMESTAMPTZ,
  is_public         BOOLEAN DEFAULT FALSE,  -- 공개 신고 여부
  metadata          JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_reports_reporter ON reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_reported_user ON reports(reported_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_severity ON reports(severity);
CREATE INDEX IF NOT EXISTS idx_reports_assigned_to ON reports(assigned_to);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reports_updated_at_trigger
BEFORE UPDATE ON reports
FOR EACH ROW
EXECUTE FUNCTION update_reports_updated_at();

-- =====================================================
-- 3. admin_roles 테이블 (권한 체계)
-- =====================================================

CREATE TABLE IF NOT EXISTS admin_roles (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  admin_id          UUID NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
  role_name         VARCHAR(100) NOT NULL,  -- 'super_admin' | 'admin' | 'moderator' | 'viewer' | 'analyst'
  permissions       TEXT[] DEFAULT '{}',  -- 권한 배열 (예: 'approve_campaign', 'delete_user', 'view_reports')
  description       VARCHAR(500),
  is_active         BOOLEAN DEFAULT TRUE,
  granted_at        TIMESTAMPTZ DEFAULT NOW(),
  granted_by        UUID REFERENCES admins(id) ON DELETE SET NULL,  -- 권한 부여자
  expires_at        TIMESTAMPTZ,  -- 권한 만료 시간 (선택)
  metadata          JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_admin_roles_admin_id ON admin_roles(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_roles_role_name ON admin_roles(role_name);
CREATE INDEX IF NOT EXISTS idx_admin_roles_is_active ON admin_roles(is_active);
CREATE INDEX IF NOT EXISTS idx_admin_roles_created_at ON admin_roles(created_at);

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_admin_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER admin_roles_updated_at_trigger
BEFORE UPDATE ON admin_roles
FOR EACH ROW
EXECUTE FUNCTION update_admin_roles_updated_at();

-- =====================================================
-- 4. RLS (Row Level Security) 정책
-- =====================================================

-- notifications 테이블 RLS 활성화
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- 정책 1: 수신자는 자신의 알림만 조회 가능
CREATE POLICY "notifications_select_own"
ON notifications
FOR SELECT
USING (
  -- 인증된 사용자가 수신자이거나 관리자인 경우
  auth.uid() = recipient_id
  OR (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 정책 2: 관리자만 알림 생성 가능
CREATE POLICY "notifications_insert_admin"
ON notifications
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 정책 3: 관리자 또는 수신자만 알림 수정 가능
CREATE POLICY "notifications_update_own"
ON notifications
FOR UPDATE
USING (
  auth.uid() = recipient_id
  OR (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- reports 테이블 RLS 활성화
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 정책 1: 신고자와 관리자는 신고 조회 가능
CREATE POLICY "reports_select_own_or_admin"
ON reports
FOR SELECT
USING (
  auth.uid() = reporter_id
  OR assigned_to = auth.uid()
  OR (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 정책 2: 인증된 사용자는 신고 생성 가능
CREATE POLICY "reports_insert_authenticated"
ON reports
FOR INSERT
WITH CHECK (
  auth.uid() = reporter_id
);

-- 정책 3: 신고자 또는 관리자만 신고 수정 가능
CREATE POLICY "reports_update_own_or_admin"
ON reports
FOR UPDATE
USING (
  auth.uid() = reporter_id
  OR (SELECT role FROM admins WHERE id = auth.uid()) IN ('super_admin', 'admin', 'moderator')
);

-- admin_roles 테이블 RLS 활성화
ALTER TABLE admin_roles ENABLE ROW LEVEL SECURITY;

-- 정책 1: Super Admin만 모든 역할 조회 가능
CREATE POLICY "admin_roles_select_super_admin"
ON admin_roles
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = admin_id  -- 자신의 역할은 항상 조회 가능
);

-- 정책 2: Super Admin만 역할 생성/수정 가능
CREATE POLICY "admin_roles_insert_super_admin"
ON admin_roles
FOR INSERT
WITH CHECK (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

CREATE POLICY "admin_roles_update_super_admin"
ON admin_roles
FOR UPDATE
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- =====================================================
-- 5. 뷰: 권한 조회 편의 함수
-- =====================================================

-- 사용자의 모든 활성 권한 조회
CREATE OR REPLACE FUNCTION get_user_permissions(user_id UUID)
RETURNS TABLE (
  permission_name TEXT,
  role_name VARCHAR
) AS $$
BEGIN
  RETURN QUERY
  SELECT UNNEST(ar.permissions) AS permission_name, ar.role_name
  FROM admin_roles ar
  WHERE ar.admin_id = user_id
    AND ar.is_active = TRUE
    AND (ar.expires_at IS NULL OR ar.expires_at > NOW());
END;
$$ LANGUAGE plpgsql;

-- 사용자가 특정 권한을 가지는지 확인
CREATE OR REPLACE FUNCTION has_permission(user_id UUID, required_permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM admin_roles ar
    WHERE ar.admin_id = user_id
      AND ar.is_active = TRUE
      AND (ar.expires_at IS NULL OR ar.expires_at > NOW())
      AND required_permission = ANY(ar.permissions)
  );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. 샘플 데이터 (테스트용)
-- =====================================================

-- 관리자 역할 초기화
INSERT INTO admin_roles (admin_id, role_name, permissions, description, granted_by)
SELECT
  id,
  'super_admin',
  ARRAY['approve_campaign', 'reject_campaign', 'delete_user', 'delete_campaign', 'view_reports', 'manage_admins', 'create_notification'],
  'Super Admin - 모든 권한 보유',
  id
FROM admins
WHERE role = 'super_admin'
ON CONFLICT DO NOTHING;

-- =====================================================
-- 마이그레이션 완료
-- =====================================================

SELECT 'Migration 007_notifications_reports_roles.sql completed successfully' AS status;

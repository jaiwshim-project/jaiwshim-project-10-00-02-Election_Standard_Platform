-- =====================================================
-- 006_admin_system.sql
-- 시스템 관리자 (Super Admin) 테이블 추가
-- 실행 위치: Supabase Dashboard → SQL Editor → 복사-붙여넣기
-- =====================================================

-- 1. admins 테이블 생성 (시스템 관리자 계정)
CREATE TABLE IF NOT EXISTS admins (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email             VARCHAR(255) UNIQUE NOT NULL,
  username          VARCHAR(100) UNIQUE NOT NULL,
  password_hash     VARCHAR(255) NOT NULL,
  role              VARCHAR(50) DEFAULT 'admin',  -- 'super_admin' | 'admin' | 'viewer'
  is_active         BOOLEAN DEFAULT TRUE,
  last_login_at     TIMESTAMPTZ,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);
CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username);
CREATE INDEX IF NOT EXISTS idx_admins_is_active ON admins(is_active);
CREATE INDEX IF NOT EXISTS idx_admins_role ON admins(role);

-- 3. admin_activity_logs 테이블 (감사 추적)
CREATE TABLE IF NOT EXISTS admin_activity_logs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  admin_id        UUID REFERENCES admins(id) ON DELETE SET NULL,
  action          VARCHAR(100),  -- 'login' | 'approve_campaign' | 'reject_campaign' | 'delete_campaign'
  target_type     VARCHAR(50),   -- 'campaign' | 'user' | 'admin'
  target_id       UUID,
  details         JSONB,
  ip_address      VARCHAR(45),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_activity_logs_admin_id ON admin_activity_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_activity_logs_created_at ON admin_activity_logs(created_at);

-- 4. campaign_approval_status 테이블 (캠프 승인 상태)
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending';  -- 'pending' | 'approved' | 'rejected'
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES admins(id) ON DELETE SET NULL;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS approval_reason TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_candidates_approval_status ON candidates(approval_status);

-- 5. RLS 정책 (Admins 테이블)
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- Super Admin: 모든 행 조회 가능
CREATE POLICY "admins_select_super_admin"
ON admins
FOR SELECT
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
  OR auth.uid() = id  -- 자신의 정보는 항상 조회 가능
);

-- Super Admin: 모든 행 수정 가능
CREATE POLICY "admins_update_super_admin"
ON admins
FOR UPDATE
USING (
  (SELECT role FROM admins WHERE id = auth.uid()) = 'super_admin'
);

-- 마이그레이션 완료
SELECT 'Migration 006_admin_system.sql completed successfully' AS status;

# Supabase SQL 실행 가이드

## 실행 순서 (중요!)

Supabase Dashboard → SQL Editor에서 아래 순서대로 실행합니다.

---

### Step 1: 007_notifications_reports_roles.sql

**경로**: `database/migrations/007_notifications_reports_roles.sql`

생성 항목:
- `notifications` 테이블 + 인덱스 + 트리거
- `reports` 테이블 + 인덱스 + 트리거
- `admin_roles` 테이블 + 인덱스 + 트리거
- RLS 정책 (notifications, reports, admin_roles)
- DB 함수: `get_user_permissions()`, `has_permission()`
- 샘플 데이터: super_admin 역할 초기화

성공 확인: `Migration 007_notifications_reports_roles.sql completed successfully`

---

### Step 2: 008_extended_rls_policies.sql

**경로**: `database/migrations/008_extended_rls_policies.sql`

생성 항목:
- notifications 추가 정책 (delete, system insert)
- reports 추가 정책 (critical delete, pending delete)
- `admin_activity_logs` RLS 활성화 + 정책 3개
- `admins` 테이블 추가 정책 2개
- 트리거: `log_report_activity()`, `log_notification_activity()`
- 뷰: `unresolved_reports_summary`, `unread_notifications_summary`, `admin_activity_summary`
- 함수: `cleanup_expired_data()`

성공 확인: `Migration 008_extended_rls_policies.sql completed successfully`

---

### Step 3: rls_policies_complete.sql

**경로**: `database/rls_policies_complete.sql`

생성 항목:
- 모든 테이블 RLS 통합 정책
- candidates, policies, competitors, reports, report_chunks, voters
- analytics, chat_sessions, chat_messages, news_feed, api_keys
- admins, admin_activity_logs, notifications, admin_roles

성공 확인: `RLS Policies Complete - All tables configured successfully`

---

## 실행 후 검증 쿼리

Supabase SQL Editor에서 실행:

```sql
-- 1. 생성된 테이블 확인
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('notifications', 'reports', 'admin_roles')
ORDER BY tablename;

-- 2. RLS 활성화 확인
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- 3. 정책 수 확인
SELECT tablename, COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- 4. admin_roles 초기 데이터 확인
SELECT admin_id, role_name, permissions, is_active
FROM admin_roles
LIMIT 10;
```

---

## 주의사항

- 007 → 008 → rls_policies_complete 순서 필수
- 007 실행 전 `admins`, `candidates` 테이블이 존재해야 함
- 008의 `admin_activity_logs` RLS는 해당 테이블이 006에서 생성된 후 실행
- rls_policies_complete는 `IF NOT EXISTS` 구문으로 중복 실행 안전

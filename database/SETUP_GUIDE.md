# Supabase 테이블 설정 가이드

## 빠른 시작 (Quick Start)

### 1단계: 파일 준비
다음 SQL 파일들이 준비되어 있는지 확인하세요:
- `/database/migrations/007_notifications_reports_roles.sql`
- `/database/migrations/008_extended_rls_policies.sql`
- `/database/rls_policies_complete.sql`

### 2단계: Supabase 접속
1. Supabase 대시보드 로그인
2. 프로젝트 선택
3. SQL Editor 탭 클릭

### 3단계: 순서대로 실행

#### Step A: 마이그레이션 파일 실행
1. SQL Editor에서 새 쿼리 생성
2. `007_notifications_reports_roles.sql` 내용 복사-붙여넣기
3. **실행** 버튼 클릭
4. 완료 메시지 확인

#### Step B: 확장 정책 실행
1. SQL Editor에서 새 쿼리 생성
2. `008_extended_rls_policies.sql` 내용 복사-붙여넣기
3. **실행** 버튼 클릭
4. 완료 메시지 확인

#### Step C: 통합 정책 실행
1. SQL Editor에서 새 쿼리 생성
2. `rls_policies_complete.sql` 내용 복사-붙여넣기
3. **실행** 버튼 클릭
4. 완료 메시지 확인

---

## 상세 실행 가이드

### Supabase SQL Editor 접속 방법

```
https://app.supabase.com/project/[PROJECT_ID]/sql
```

### 각 파일별 상세 설명

#### 007_notifications_reports_roles.sql

**생성되는 테이블:**
- `notifications`: 메시지/알림 시스템
- `reports`: 신고/이슈 관리
- `admin_roles`: 관리자 권한 체계

**생성되는 함수:**
- `get_user_permissions()`: 사용자 권한 조회
- `has_permission()`: 권한 확인

**생성되는 인덱스:**
- 성능 최적화를 위한 22개 인덱스

**예상 실행 시간:** 30초 이내

**체크리스트:**
- [ ] 테이블 3개 생성 확인
- [ ] 인덱스 생성 완료 확인
- [ ] "Migration 007... completed successfully" 메시지 확인

---

#### 008_extended_rls_policies.sql

**생성되는 RLS 정책:**
- admin_activity_logs 테이블 정책
- reports 테이블 추가 정책
- notifications 테이블 추가 정책

**생성되는 함수:**
- `log_report_activity()`: 신고 활동 로깅
- `log_notification_activity()`: 알림 활동 로깅
- `cleanup_expired_data()`: 만료 데이터 청소

**생성되는 뷰:**
- `unresolved_reports_summary`: 미해결 신고 요약
- `unread_notifications_summary`: 읽지 않은 알림 요약
- `admin_activity_summary`: 관리자 활동 요약

**생성되는 트리거:**
- reports_activity_log_trigger
- notifications_activity_log_trigger

**예상 실행 시간:** 1분 이내

**체크리스트:**
- [ ] 뷰 3개 생성 확인
- [ ] 함수 3개 생성 확인
- [ ] 트리거 2개 생성 확인
- [ ] "Migration 008... completed successfully" 메시지 확인

---

#### rls_policies_complete.sql

**활성화되는 RLS:**
- candidates, policies, competitors 테이블
- reports, voters, analytics 테이블
- chat_sessions, news_feed, api_keys 테이블
- admins, admin_roles, notifications 테이블

**생성되는 정책:**
- 총 47개 정책

**예상 실행 시간:** 2분 이내

**체크리스트:**
- [ ] 모든 테이블 RLS 활성화 확인
- [ ] 정책 47개 생성 확인
- [ ] "RLS Policies Complete... All tables configured successfully" 메시지 확인

---

## 검증 쿼리

### 생성된 테이블 확인

```sql
-- notifications 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_name = 'notifications' AND table_schema = 'public';

-- reports 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_name = 'reports' AND table_schema = 'public';

-- admin_roles 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_name = 'admin_roles' AND table_schema = 'public';
```

### RLS 정책 확인

```sql
-- 모든 정책 조회
SELECT schemaname, tablename, policyname, permissive
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- 테이블별 정책 수 집계
SELECT tablename, COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;
```

### 함수 확인

```sql
-- 생성된 함수 확인
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name IN ('get_user_permissions', 'has_permission', 'cleanup_expired_data')
ORDER BY routine_name;
```

### 뷰 확인

```sql
-- 생성된 뷰 확인
SELECT table_name FROM information_schema.tables
WHERE table_type = 'VIEW'
  AND table_schema = 'public'
  AND table_name LIKE '%summary%'
ORDER BY table_name;
```

### 인덱스 확인

```sql
-- notifications 테이블 인덱스 확인
SELECT indexname FROM pg_indexes
WHERE tablename = 'notifications'
ORDER BY indexname;

-- reports 테이블 인덱스 확인
SELECT indexname FROM pg_indexes
WHERE tablename = 'reports'
ORDER BY indexname;

-- admin_roles 테이블 인덱스 확인
SELECT indexname FROM pg_indexes
WHERE tablename = 'admin_roles'
ORDER BY indexname;
```

---

## 테스트 데이터 삽입

### 테스트용 관리자 생성

```sql
-- admins 테이블에 관리자가 있다고 가정
INSERT INTO admin_roles (admin_id, role_name, permissions, description)
SELECT
  id,
  'test_admin',
  ARRAY['view_reports', 'create_notification'],
  'Test Admin for Development'
FROM admins
WHERE role = 'super_admin'
LIMIT 1;
```

### 테스트용 알림 생성

```sql
-- candidates 테이블의 첫 번째 사용자에게 테스트 알림 전송
INSERT INTO notifications (recipient_id, sender_id, title, content, notification_type, priority)
SELECT
  c.id,
  a.id,
  'Test Notification',
  'This is a test notification for development and testing.',
  'message',
  1
FROM candidates c, admins a
WHERE c.is_active = TRUE AND a.role = 'super_admin'
LIMIT 1;
```

### 테스트용 신고 생성

```sql
-- 테스트 신고 생성
INSERT INTO reports (reporter_id, report_type, title, description, severity)
SELECT
  id,
  'spam',
  'Test Spam Report',
  'This is a test report for spam content.',
  'low'
FROM candidates
WHERE is_active = TRUE
LIMIT 1;
```

---

## 문제 해결

### 문제 1: "relation does not exist" 에러

**원인:** 마이그레이션 파일이 순서대로 실행되지 않음

**해결:**
1. 파일들을 정확한 순서대로 실행
2. 각 파일 실행 후 완료 메시지 확인
3. 필요시 이전 파일부터 다시 실행

### 문제 2: 권한(Permission) 부족 에러

**원인:** 사용 중인 Supabase 키가 service_role 키가 아님

**해결:**
1. Supabase 대시보드 → Settings → API
2. service_role secret 사용
3. RLS 정책이 있으므로 일반 키로는 제한됨

### 문제 3: RLS 정책 적용 안 됨

**원인:** 이전 설정의 정책과 충돌

**해결:**
```sql
-- 기존 정책 제거 (주의: 신중하게 실행)
DROP POLICY IF EXISTS "policy_name" ON table_name;

-- 새 정책 다시 생성
CREATE POLICY "policy_name" ON table_name ...;
```

### 문제 4: 함수 실행 오류

**원인:** 함수가 참조하는 테이블/컬럼이 없음

**해결:**
1. 선행 마이그레이션 파일들이 모두 실행되었는지 확인
2. 기존 테이블(admins, candidates) 존재 확인

---

## 실행 결과 예상

### 성공 시

```
Migration 007_notifications_reports_roles.sql completed successfully
Migration 008_extended_rls_policies.sql completed successfully
RLS Policies Complete - All tables configured successfully
```

### 데이터베이스 상태

```
테이블: 21개 (기존 14개 + 신규 3개 + 뷰 4개)
정책: 47개 (모든 테이블 RLS)
함수: 9개 (기존 1개 + 신규 8개)
트리거: 7개 (신규 7개)
인덱스: 48개+ (성능 최적화)
```

---

## 마이그레이션 후 애플리케이션 설정

### JavaScript 클라이언트 수정 필요

#### 알림 조회

```javascript
// supabase-client.js에 추가
async getNotifications() {
  if (!await this.init()) return [];

  try {
    const { data, error } = await this.client
      .from('notifications')
      .select('*')
      .eq('recipient_id', candidateId)
      .order('created_at', { ascending: false })
      .limit(10);

    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('알림 조회 실패:', error);
    return [];
  }
}
```

#### 신고 생성

```javascript
async createReport(reportData) {
  if (!await this.init()) return null;

  try {
    const { data, error } = await this.client
      .from('reports')
      .insert([reportData])
      .select()
      .single();

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('신고 생성 실패:', error);
    return null;
  }
}
```

#### 권한 확인

```javascript
async hasPermission(adminId, permission) {
  if (!await this.init()) return false;

  try {
    const { data, error } = await this.client
      .rpc('has_permission', {
        user_id: adminId,
        required_permission: permission
      });

    if (error) throw error;
    return data || false;
  } catch (error) {
    console.error('권한 확인 실패:', error);
    return false;
  }
}
```

---

## 보안 체크리스트

- [ ] RLS가 모든 새 테이블에 활성화됨
- [ ] 관리자만 민감한 작업 가능하도록 정책 설정
- [ ] 사용자는 자신의 데이터만 접근 가능
- [ ] 감사 로그(admin_activity_logs)가 작동 중
- [ ] 권한 만료 시간(expires_at) 설정됨

---

## 정기 유지보수

### 일일 작업
- 신고 상태 확인
- 미처리 알림 확인

### 주간 작업
- 관리자 활동 로그 검토
- 신고 통계 확인

### 월간 작업
- 만료된 데이터 청소
```sql
SELECT * FROM cleanup_expired_data();
```

### 분기별 작업
- 권한 검토 및 업데이트
- 성능 인덱스 최적화 검토

---

## 지원 연락처

**담당자:** Alpha 1분대장 (정규병: database-developer)

**생성일:** 2026-03-21

**최종 수정일:** 2026-03-21

---

## 다음 단계

1. ✅ SQL 스크립트 작성 완료
2. 📌 Supabase에 직접 생성 (또는 실행 대기)
3. 📌 애플리케이션 통합
4. 📌 테스트 및 검증
5. 📌 운영 배포

---

## 참고 자료

- Supabase 공식 문서: https://supabase.com/docs
- PostgreSQL RLS: https://www.postgresql.org/docs/current/sql-createrole.html
- 설계 문서: `TABLE_DESIGN.md`


# Supabase 테이블 설계 문서

## 개요
이 문서는 메시지, 신고, 권한 체계를 위한 Supabase 테이블 설계를 정의합니다.

---

## 1. NOTIFICATIONS 테이블 (메시지/알림)

### 목적
후보자(candidates)에게 시스템 메시지, 알림, 승인/거부 알림 등을 전달

### 스키마

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | UUID | PK, Default uuid_generate_v4() | 알림 고유 ID |
| recipient_id | UUID | NOT NULL, FK(candidates.id) | 수신자 (후보자) |
| sender_id | UUID | FK(admins.id), nullable | 발신자 (관리자) |
| title | VARCHAR(200) | NOT NULL | 알림 제목 |
| content | TEXT | NOT NULL | 알림 내용 |
| notification_type | VARCHAR(50) | NOT NULL | 'system', 'message', 'alert', 'approval', 'rejection' |
| is_read | BOOLEAN | Default FALSE | 읽음 여부 |
| read_at | TIMESTAMPTZ | nullable | 읽은 시간 |
| priority | INTEGER | Default 0 | 0: normal, 1: high, 2: critical |
| metadata | JSONB | Default {} | 추가 데이터 (링크, 파라미터) |
| expires_at | TIMESTAMPTZ | nullable | 자동 삭제 시간 |
| created_at | TIMESTAMPTZ | Default NOW() | 생성 시간 |
| updated_at | TIMESTAMPTZ | Default NOW() | 수정 시간 |

### 인덱스
- idx_notifications_recipient: 수신자별 조회 성능
- idx_notifications_is_read: 읽음 여부 필터링
- idx_notifications_created_at: 시간 정렬
- idx_notifications_priority: 우선순위 필터링
- idx_notifications_type: 타입별 조회

### RLS 정책

**정책 1: 수신자 조회 권한**
- 수신자는 자신의 알림만 조회 가능
- Super Admin은 모든 알림 조회 가능

**정책 2: 생성 권한**
- 관리자(admin, super_admin)만 알림 생성 가능

**정책 3: 수정 권한**
- 수신자 또는 Super Admin만 수정 가능

**정책 4: 삭제 권한**
- 수신자만 삭제 가능

### 사용 사례

1. **캠프 승인 알림**
   ```json
   {
     "notification_type": "approval",
     "title": "캠프 승인되었습니다",
     "content": "귀하의 캠프가 관리자에 의해 승인되었습니다.",
     "priority": 2,
     "metadata": {"campaign_id": "uuid", "approved_by": "admin_id"}
   }
   ```

2. **시스템 공지**
   ```json
   {
     "notification_type": "system",
     "title": "시스템 점검 안내",
     "content": "2026-03-21 23:00 ~ 2026-03-22 01:00에 시스템 점검이 있습니다.",
     "priority": 1
   }
   ```

3. **중요 메시지**
   ```json
   {
     "notification_type": "message",
     "title": "관리자 메시지",
     "content": "귀하의 캠프 운영에 문제가 있습니다. 확인 부탁드립니다.",
     "priority": 2
   }
   ```

---

## 2. REPORTS 테이블 (신고/이슈)

### 목적
부정행위, 스팸, 부적절한 콘텐츠 등을 신고하는 시스템

### 스키마

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | UUID | PK, Default uuid_generate_v4() | 신고 고유 ID |
| reporter_id | UUID | NOT NULL, FK(candidates.id) | 신고자 |
| reported_user_id | UUID | FK(candidates.id), nullable | 피신고자 |
| report_type | VARCHAR(50) | NOT NULL | 'spam', 'abuse', 'inappropriate', 'fraud', 'other' |
| title | VARCHAR(200) | NOT NULL | 신고 제목 |
| description | TEXT | NOT NULL | 상세 설명 |
| evidence_urls | TEXT[] | nullable | 증거 URL 배열 |
| status | VARCHAR(50) | Default 'pending' | 'pending', 'investigating', 'resolved', 'dismissed', 'escalated' |
| severity | VARCHAR(50) | Default 'medium' | 'low', 'medium', 'high', 'critical' |
| assigned_to | UUID | FK(admins.id), nullable | 담당 관리자 |
| resolution_notes | TEXT | nullable | 해결 노트 |
| resolved_at | TIMESTAMPTZ | nullable | 해결 시간 |
| is_public | BOOLEAN | Default FALSE | 공개 신고 여부 |
| metadata | JSONB | Default {} | 추가 정보 |
| created_at | TIMESTAMPTZ | Default NOW() | 생성 시간 |
| updated_at | TIMESTAMPTZ | Default NOW() | 수정 시간 |

### 인덱스
- idx_reports_reporter: 신고자별 조회
- idx_reports_reported_user: 피신고자별 조회
- idx_reports_status: 상태별 필터링
- idx_reports_severity: 심각도별 필터링
- idx_reports_assigned_to: 담당자별 조회
- idx_reports_created_at: 시간 정렬
- idx_reports_type: 타입별 조회

### RLS 정책

**정책 1: 조회 권한**
- 신고자: 자신의 신고만 조회
- 담당 관리자: 자신이 할당받은 신고만 조회
- Super Admin, Admin, Moderator: 모든 신고 조회

**정책 2: 생성 권한**
- 인증된 사용자(candidates.id = auth.uid())만 신고 생성 가능

**정책 3: 수정 권한**
- 신고자 또는 관리자만 수정 가능

**정책 4: 삭제 권한**
- Super Admin: critical 심각도 신고만 삭제
- 신고자: pending 상태 신고만 삭제

### 사용 사례

1. **스팸 신고**
   ```json
   {
     "report_type": "spam",
     "title": "반복된 광고성 메시지",
     "description": "사용자가 반복적으로 광고성 메시지를 보내고 있습니다.",
     "severity": "low",
     "evidence_urls": ["https://example.com/evidence1"]
   }
   ```

2. **부정행위 신고**
   ```json
   {
     "report_type": "fraud",
     "title": "허위 사실 유포",
     "description": "후보자가 거짓된 자격 요건을 등록했습니다.",
     "severity": "critical",
     "evidence_urls": ["https://example.com/evidence1", "https://example.com/evidence2"]
   }
   ```

3. **부적절한 콘텐츠**
   ```json
   {
     "report_type": "inappropriate",
     "title": "혐오 발언",
     "description": "프로필에 혐오 발언이 포함되어 있습니다.",
     "severity": "high"
   }
   ```

### 워크플로우

```
pending -> investigating -> resolved (또는 dismissed/escalated)
                          ↓
                    resolution_notes 기록
                    resolved_at 시간 기록
```

---

## 3. ADMIN_ROLES 테이블 (권한 체계)

### 목적
관리자의 역할과 권한을 계층적으로 관리

### 스키마

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| id | UUID | PK, Default uuid_generate_v4() | 역할 고유 ID |
| admin_id | UUID | NOT NULL, FK(admins.id) | 관리자 ID |
| role_name | VARCHAR(100) | NOT NULL | 'super_admin', 'admin', 'moderator', 'viewer', 'analyst' |
| permissions | TEXT[] | Default {} | 권한 배열 |
| description | VARCHAR(500) | nullable | 역할 설명 |
| is_active | BOOLEAN | Default TRUE | 활성화 여부 |
| granted_at | TIMESTAMPTZ | Default NOW() | 권한 부여 시간 |
| granted_by | UUID | FK(admins.id), nullable | 권한 부여자 |
| expires_at | TIMESTAMPTZ | nullable | 권한 만료 시간 |
| metadata | JSONB | Default {} | 추가 정보 |
| created_at | TIMESTAMPTZ | Default NOW() | 생성 시간 |
| updated_at | TIMESTAMPTZ | Default NOW() | 수정 시간 |

### 인덱스
- idx_admin_roles_admin_id: 관리자별 역할 조회
- idx_admin_roles_role_name: 역할명 검색
- idx_admin_roles_is_active: 활성 역할만 필터링
- idx_admin_roles_created_at: 시간 정렬

### RLS 정책

**정책 1: 조회 권한**
- Super Admin: 모든 역할 조회 가능
- 개인: 자신의 역할만 조회 가능

**정책 2: 생성 권한**
- Super Admin만 역할 생성 가능

**정책 3: 수정 권한**
- Super Admin만 역할 수정 가능

### 권한 정의 (Permissions)

#### Super Admin 권한
- approve_campaign: 캠프 승인
- reject_campaign: 캠프 거부
- delete_user: 사용자 삭제
- delete_campaign: 캠프 삭제
- view_reports: 신고 조회
- manage_admins: 관리자 관리
- create_notification: 알림 생성
- manage_roles: 역할 관리
- access_audit_logs: 감사 로그 조회

#### Admin 권한
- approve_campaign
- reject_campaign
- view_reports
- create_notification
- manage_moderators: Moderator 관리

#### Moderator 권한
- view_reports
- update_report_status
- create_notification

#### Analyst 권한
- view_reports (읽기만)
- view_analytics: 분석 데이터 조회

#### Viewer 권한
- view_candidates: 후보자 조회
- view_campaigns: 캠프 조회

### 사용 사례

1. **Super Admin 역할 부여**
   ```json
   {
     "role_name": "super_admin",
     "permissions": [
       "approve_campaign", "reject_campaign",
       "delete_user", "delete_campaign",
       "view_reports", "manage_admins",
       "create_notification", "manage_roles"
     ],
     "description": "시스템 최고 권한자"
   }
   ```

2. **Moderator 역할 부여 (임시)**
   ```json
   {
     "role_name": "moderator",
     "permissions": ["view_reports", "update_report_status", "create_notification"],
     "description": "신고 처리 담당자",
     "expires_at": "2026-12-31T23:59:59Z"
   }
   ```

3. **Analyst 역할 부여**
   ```json
   {
     "role_name": "analyst",
     "permissions": ["view_reports", "view_analytics"],
     "description": "데이터 분석 담당자"
   }
   ```

---

## 4. 도움말 함수

### 1. get_user_permissions(user_id UUID)

사용자의 모든 활성 권한을 조회합니다.

**사용법**
```sql
SELECT * FROM get_user_permissions('admin-id-uuid');
```

**반환값**
```
permission_name | role_name
----------------+------------
approve_campaign | super_admin
reject_campaign | super_admin
delete_user | super_admin
...
```

### 2. has_permission(user_id UUID, required_permission TEXT)

사용자가 특정 권한을 가지는지 확인합니다.

**사용법**
```sql
SELECT has_permission('admin-id-uuid', 'approve_campaign');
```

**반환값**
```
true 또는 false
```

### 3. cleanup_expired_data()

만료된 데이터를 자동 삭제합니다.

**사용법**
```sql
SELECT * FROM cleanup_expired_data();
```

**반환값**
```
deleted_notifications | deleted_reports
---------------------+-----------------
5                    | 2
```

---

## 5. 뷰 (Views)

### 1. unresolved_reports_summary

미해결 신고의 요약 통계입니다.

**쿼리 예시**
```sql
SELECT * FROM unresolved_reports_summary;
```

**결과**
```
critical_count | high_count | medium_count | low_count | total_count | unassigned_count
---------------+------------+--------------+-----------+-------------+------------------
2              | 5          | 12           | 8         | 27          | 3
```

### 2. unread_notifications_summary

읽지 않은 알림의 요약입니다.

**쿼리 예시**
```sql
SELECT * FROM unread_notifications_summary WHERE recipient_id = 'uuid';
```

**결과**
```
recipient_id | unread_count | critical_count | high_count | latest_notification_at
--------------+--------------+----------------+------------+------------------------
uuid         | 5            | 1              | 2          | 2026-03-21 10:30:00+00
```

### 3. admin_activity_summary

관리자 활동 요약입니다 (최근 30일).

**쿼리 예시**
```sql
SELECT * FROM admin_activity_summary WHERE admin_id = 'uuid';
```

**결과**
```
admin_id | total_actions | approvals | deletions | creations | last_action_at
---------+---------------+-----------+-----------+-----------+------------------------
uuid    | 25            | 10        | 3         | 5         | 2026-03-21 15:45:00+00
```

---

## 6. 트리거 (Triggers)

### 1. notifications_updated_at_trigger
수정 시 `updated_at`을 자동으로 갱신합니다.

### 2. reports_updated_at_trigger
수정 시 `updated_at`을 자동으로 갱신합니다.

### 3. admin_roles_updated_at_trigger
수정 시 `updated_at`을 자동으로 갱신합니다.

### 4. reports_activity_log_trigger
신고 생성/수정/삭제 시 `admin_activity_logs`에 로그를 기록합니다.

### 5. notifications_activity_log_trigger
알림 생성/수정 시 `admin_activity_logs`에 로그를 기록합니다.

---

## 7. 데이터 마이그레이션 계획

### Phase 1: 테이블 생성
1. 007_notifications_reports_roles.sql 실행
   - notifications 테이블
   - reports 테이블
   - admin_roles 테이블
   - 기본 RLS 정책

### Phase 2: 확장 정책
2. 008_extended_rls_policies.sql 실행
   - 추가 RLS 정책
   - 트리거 및 함수
   - 뷰 생성

### Phase 3: 통합 정책
3. rls_policies_complete.sql 실행
   - 모든 테이블 RLS 활성화
   - 정책 통합

---

## 8. 보안 고려사항

### Row Level Security (RLS)
- 모든 테이블에 RLS가 활성화됨
- 사용자는 자신의 권한에 따라서만 데이터 접근 가능
- Super Admin은 모든 데이터 접근 가능

### 감사 추적 (Audit Trail)
- admin_activity_logs 테이블로 모든 관리자 활동 기록
- 트리거를 통해 자동 로깅

### 데이터 만료
- notifications, admin_roles는 `expires_at` 지원
- cleanup_expired_data() 함수로 정기적 청소

---

## 9. 성능 최적화

### 인덱스 전략
- 자주 조회되는 컬럼: recipient_id, reporter_id, status, is_read
- 정렬/필터링: created_at, priority, severity
- 고유성 보장: 필요시 UNIQUE 인덱스

### 쿼리 예시

**최근 알림 조회**
```sql
SELECT * FROM notifications
WHERE recipient_id = $1 AND is_read = FALSE
ORDER BY created_at DESC
LIMIT 10;
```

**미처리 신고 조회**
```sql
SELECT * FROM reports
WHERE status IN ('pending', 'investigating')
  AND assigned_to = $1
ORDER BY severity DESC, created_at ASC;
```

**권한 확인**
```sql
SELECT has_permission($1, 'approve_campaign');
```

---

## 10. 향후 개선사항

1. **실시간 업데이트**: Supabase Realtime을 통한 실시간 알림
2. **웹훅**: 신고 상태 변경 시 웹훅 트리거
3. **권한 계층화**: 더 세분화된 권한 체계
4. **알림 템플릿**: 사전 정의된 알림 템플릿 시스템
5. **신고 자동 분류**: AI 기반 신고 자동 분류

---

## 11. 실행 순서

### Supabase SQL Editor에서 순서대로 실행

```
1. 001_initial_schema.sql
2. 002_additional_tables.sql
3. 003_camp_model.sql
4. 004_login_accounts.sql
5. 005_signup_system.sql
6. 006_admin_system.sql
7. 007_notifications_reports_roles.sql     ← NEW
8. 008_extended_rls_policies.sql           ← NEW
9. rls_policies_complete.sql               ← NEW
```

---

## 생성일

2026-03-21

## 담당자

Alpha 1분대장 (정규병: database-developer)

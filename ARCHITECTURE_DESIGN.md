# 선거 워룸 — 시스템 아키텍처 설계

> Alpha 분대 산출물 | 작성일: 2026-03-20 | 담당: Alpha 분대장

---

## 1. 전체 흐름도

### 1-1. 랜딩페이지 → 인증 → 대시보드 흐름

```
[index.html — 랜딩페이지]
        |
        |── 미인증 상태 ──────────────────────────────────────┐
        |                                                       |
        |   [회원가입 섹션 표시]          [로그인 섹션 표시]    |
        |        |                              |               |
        |   캠프명/이메일/비밀번호         아이디/비밀번호      |
        |   후보자명/선거지역/정당         입력 및 제출         |
        |   입력 후 가입 버튼                   |               |
        |        |                              |               |
        |   POST /api/auth/signup          AuthManager.login()  |
        |   → candidates 테이블 INSERT     → Supabase 조회     |
        |   → sessionStorage 세션 생성     → SHA-256 검증      |
        |        |                         → sessionStorage     |
        |        └──────────────┬───────────────┘              |
        |                       |                               |
        |               로그인 성공                             |
        |                       |                               |
        |   [헤더 상태 변경]                                    |
        |   - "대시보드 바로가기" 버튼 표시                     |
        |   - 설정 메뉴 활성화                                  |
        |   - 캠프명 헤더 표시                                  |
        |   - 관리자: "관리자 설정" 메뉴 추가 표시              |
        |                       |                               |
        └───────────────────────┼───────────────────────────────┘
                                |
                    [pages/dashboard.html]
                    - AuthManager.requireAuth() 체크
                    - 미인증 → pages/login.html 리다이렉트
                    - 인증 완료 → 캠프 데이터 로드 및 표시
```

### 1-2. 역할별 접근 제어 흐름

```
로그인 성공 후 role 분기:
                    ┌──────────────┐
                    │  sessionStorage │
                    │  role: 'staff'  │
                    │  role: 'admin'  │
                    └──────┬───────┘
                           |
          ┌────────────────┴────────────────┐
          |                                  |
      role = 'staff'                    role = 'admin'
          |                                  |
   [Staff 접근 가능]                  [Admin 접근 가능]
   - 대시보드 열람                    - 대시보드 열람
   - 판세/전략/공약 열람              - 판세/전략/공약 열람
   - 워룸 참여                        - 워룸 참여
   - 블로그/외부자료 열람             - 블로그/외부자료 작성/삭제
   - 조직도 열람                      - 조직도 관리
                                       - settings.html 접근 가능
                                       - 후보자정보 수정
                                       - Supabase 연결 설정
                                       - 관리자 비밀번호 변경
```

### 1-3. settings.html 관리자 게이트 흐름

```
[settings.html 접근]
        |
   AuthManager.requireAuth()
   → 미인증: login.html 리다이렉트
        |
   AuthManager.getRole()
        |
   ┌────┴────────────┐
   |                  |
role = 'staff'   role = 'admin'
   |                  |
[제한된 설정만]   [관리자 비밀번호 2차 인증 게이트]
 - 테마/정당 변경      |
 - 개인 설정만    비밀번호 입력 모달
                       |
              ┌────────┴────────┐
              |                  |
         비밀번호 틀림      비밀번호 맞음
              |                  |
         오류 메시지        [전체 설정 표시]
         (최대 5회)         - 후보자정보 수정
                            - API 키 관리
                            - 계정 관리
                            - 데이터 마이그레이션
```

---

## 2. DB 스키마

### 2-1. 현재 candidates 테이블 (누적 마이그레이션 결과)

`candidates` 테이블이 캠프(camp) 단위의 핵심 엔티티로 사용됨.

```sql
-- 현재 candidates 테이블 전체 컬럼 (001~004 마이그레이션 누적)
CREATE TABLE candidates (
  -- 기본 식별
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name              VARCHAR(100) NOT NULL,           -- 후보자명 (= 캠프명)
  party             party_affiliation NOT NULL DEFAULT '무소속',
  status            candidate_status DEFAULT 'active',
  district          VARCHAR(200),                    -- 선거지역 (선거구)
  region            VARCHAR(100),                    -- 광역 지역
  bio               TEXT,
  meta              JSONB DEFAULT '{}',

  -- 캠프 코드 (003 마이그레이션)
  camp_code         VARCHAR(100) UNIQUE,             -- 예: kim-dongjaek-2024

  -- 인증 계정 (004 마이그레이션)
  staff_account_id  VARCHAR(100) UNIQUE,             -- 일반 스태프 아이디
  staff_password    VARCHAR(255),                    -- SHA-256 해시
  admin_account_id  VARCHAR(100) UNIQUE,             -- 관리자 아이디
  admin_password    VARCHAR(255),                    -- SHA-256 해시

  -- 상태
  is_active         BOOLEAN DEFAULT TRUE,

  -- API 설정
  gemini_api_key    TEXT,
  gemini_model      VARCHAR(100) DEFAULT 'gemini-2.0-flash',

  -- 타임스탬프
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### 2-2. 신규 추가 필요 컬럼 (회원가입 시스템)

현재 `candidates` 테이블은 관리자가 직접 INSERT하는 방식. 회원가입(self-service) 흐름을 위해 아래 컬럼을 추가:

```sql
-- 005_signup_system.sql (신규 마이그레이션)

ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,     -- 가입 이메일
  ADD COLUMN IF NOT EXISTS election_type VARCHAR(50),     -- 선거유형 (presidential 등)
  ADD COLUMN IF NOT EXISTS profile_photo_url TEXT,        -- Supabase Storage URL
  ADD COLUMN IF NOT EXISTS signup_at TIMESTAMPTZ,         -- 회원가입 시각
  ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE;  -- 관리자 승인 여부 (선택)

CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_is_active_approved
  ON candidates(is_active, is_approved);
```

### 2-3. 관계 정의: candidates (1) ← → (N) 하위 테이블

```
candidates (1)
    ├── (N) camp_members        -- 캠프 구성원
    ├── (N) blog_articles       -- 블로그 게시물
    ├── (N) competitors_list    -- 경쟁자 목록
    ├── (N) app_settings        -- 앱 설정 (key-value)
    ├── (N) shared_files        -- 업로드 파일
    ├── (N) policies            -- 공약
    ├── (N) reports             -- 분석 리포트
    ├── (N) analytics           -- 판세 수치
    ├── (N) chat_sessions       -- AI 채팅 세션
    └── (N) news_feed           -- 뉴스 피드
```

관계 유형: **1:N (one-to-many)**
- 1개 캠프(candidate) = 여러 개의 블로그, 파일, 분석 데이터
- 다대다(M:N)는 없음 (competitors 테이블만 자기참조 1:N)

### 2-4. 전체 SQL 마이그레이션 스크립트 (신규: 005)

```sql
-- =====================================================
-- 005_signup_system.sql
-- 회원가입 기반 캠프 셀프서비스 등록 시스템
-- =====================================================

-- 1. candidates 테이블 확장
ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
  ADD COLUMN IF NOT EXISTS election_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS profile_photo_url TEXT,
  ADD COLUMN IF NOT EXISTS signup_at TIMESTAMPTZ DEFAULT NOW(),
  ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE;

-- 2. 인덱스
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_approved ON candidates(is_approved);

-- 3. party 컬럼 ENUM 확장 (조국혁신당, 자유와혁신, 개혁신당 추가)
-- PostgreSQL ENUM은 ALTER TYPE으로만 추가 가능
ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '조국혁신당';
ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '자유와혁신';
ALTER TYPE party_affiliation ADD VALUE IF NOT EXISTS '개혁신당';

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

-- 5. Supabase Storage 버킷 생성 (SQL에서 직접 불가 - Supabase Dashboard에서 설정)
-- 버킷명: 'profile-photos'
-- 접근: public (읽기) / 인증 필요 (쓰기)
-- 파일 크기 제한: 5MB
-- 허용 MIME: image/jpeg, image/png, image/webp
```

### 2-5. Row Level Security (RLS) 정책

```sql
-- candidates 테이블 RLS (Supabase Auth 미사용, 앱 레벨 제어)
-- Supabase anon key는 읽기 전용으로 사용
-- 쓰기는 service_role key (서버사이드) 또는 RLS policy로 제한

ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- 공개 읽기: is_active = true인 캠프만 조회 가능
CREATE POLICY "Public read active candidates"
  ON candidates FOR SELECT
  USING (is_active = true);

-- 쓰기: service_role만 (관리자 API 경유)
-- 클라이언트 사이드 직접 INSERT/UPDATE 차단
```

---

## 3. API 엔드포인트

> 현재 아키텍처: 순수 프론트엔드 + Supabase JS SDK 직접 호출 방식
> 별도 백엔드 서버 없음 (server/ 디렉터리 존재하나 현재 미사용)
> 아래는 Supabase Client SDK 기준 논리적 API 명세

### 3-1. 인증 (AuthManager.js)

| 작업 | 메서드 | Supabase 쿼리 | 설명 |
|------|--------|---------------|------|
| 로그인 | `AuthManager.login(accountId, password)` | `supabase.from('candidates').select().eq(column, id).eq('is_active', true)` | SHA-256 해시 비교 |
| 회원가입 | `AuthManager.signup(data)` | `supabase.from('candidates').insert([data])` | 신규 캠프 등록 |
| 세션 확인 | `AuthManager.isAuthenticated()` | sessionStorage 조회 (8시간 타임아웃) | 클라이언트 전용 |
| 로그아웃 | `AuthManager.logout()` | sessionStorage.removeItem() | 세션 삭제 |
| 역할 조회 | `AuthManager.getRole()` | sessionStorage 조회 | 'staff' or 'admin' |

### 3-2. 캠프 정보 (SupabaseDB)

| 작업 | 논리 엔드포인트 | Supabase 쿼리 |
|------|----------------|---------------|
| GET /api/campaigns/:id | `SupabaseDB.getCandidate(id)` | `supabase.from('candidates').select('*').eq('id', id)` |
| PUT /api/campaigns/:id | `SupabaseDB.upsertCandidate(data)` | `supabase.from('candidates').update(data).eq('id', id)` — admin only |
| POST /api/campaigns | `SupabaseDB.createCampaign(data)` | `supabase.from('candidates').insert([data])` |

### 3-3. 콘텐츠 관리

| 작업 | 논리 엔드포인트 | 비고 |
|------|----------------|------|
| GET /api/blog | `SupabaseDB.getBlogArticles()` | 전체 조회 (candidate_id 필터) |
| POST /api/blog | `SupabaseDB.upsertBlogArticle(data)` | admin only |
| DELETE /api/blog/:id | `SupabaseDB.deleteBlogArticle(id)` | admin only |
| GET /api/competitors | `SupabaseDB.getCompetitors()` | candidate_id 필터 |
| POST /api/competitors | `SupabaseDB.upsertCompetitor(data)` | admin only |
| PUT /api/settings/:key | `SupabaseDB.setSetting(key, value)` | admin only |

### 3-4. 파일 업로드 (Supabase Storage)

```
POST   Storage: profile-photos/{candidate_id}/{filename}
GET    Storage URL: https://{project}.supabase.co/storage/v1/object/public/profile-photos/{path}
DELETE Storage: profile-photos/{candidate_id}/{filename}
```

---

## 4. 보안 설계

### 4-1. 비밀번호 해싱 전략

**현재 구현: SHA-256 (Web Crypto API)**

```javascript
// auth-manager.js 기존 구현
async hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
```

**한계 및 권고사항:**
- SHA-256은 레인보우 테이블 공격에 취약 (솔트 없음)
- 브라우저에서 실행되므로 bcrypt 사용 불가 (CPU 집약적)
- **단기 권고**: SHA-256 + 고정 솔트 (캠프 ID 기반) 적용
- **중장기 권고**: Supabase Edge Function에서 bcrypt 처리

```sql
-- 권고: 솔트 포함 해시 저장
-- staff_password = SHA256(candidate_id + ':' + raw_password)
-- 클라이언트에서: hashPassword(candidateId + ':' + rawPassword)
```

### 4-2. 역할 기반 접근 제어 (RBAC)

**역할 정의:**

| 역할 | 계정 ID 패턴 | 접근 범위 |
|------|-------------|-----------|
| `staff` | `kim2024` (일반 형식) | 읽기 전용 + 워룸 참여 |
| `admin` | `admin_kim2024` (admin_ prefix) | 전체 쓰기 + 설정 관리 |

**구현 방식 (클라이언트 사이드 RBAC):**

```javascript
// 각 페이지 상단에서 역할 체크
AuthManager.requireAuth();        // 인증 필수
AuthManager.requireAdmin();       // 관리자 전용

// UI 레벨 제어
const role = AuthManager.getRole();
if (role === 'admin') {
  document.getElementById('admin-menu').style.display = 'block';
  document.getElementById('edit-btn').disabled = false;
} else {
  document.getElementById('admin-menu').style.display = 'none';
  document.getElementById('edit-btn').disabled = true;
}
```

**Supabase RLS 보완 (서버 사이드):**
- anon key: `SELECT` 허용 (is_active = true 필터)
- service_role key: 전체 권한 (관리자 전용 작업에만 사용)
- 민감 컬럼 (admin_password, staff_password, gemini_api_key): 클라이언트 SELECT에서 제외

```sql
-- 민감 컬럼 마스킹 뷰 (선택적 적용)
CREATE VIEW candidates_public AS
  SELECT id, name, party, district, region, is_active,
         camp_code, staff_account_id, admin_account_id,
         profile_photo_url, election_type
  FROM candidates
  WHERE is_active = true;
  -- admin_password, staff_password, gemini_api_key 제외
```

### 4-3. 세션 만료 정책

```javascript
// auth-manager.js 기존 구현
SESSION_KEY: 'campSession',
SESSION_TIMEOUT_MS: 8 * 60 * 60 * 1000, // 8시간

// 세션 객체 구조
{
  candidateId: "uuid",
  campName: "김철수 캠프",
  role: "admin",         // 'staff' | 'admin'
  loginAt: 1234567890,   // Unix timestamp (ms)
  accountId: "admin_kim2024"
}
```

**세션 정책:**
- 저장소: `sessionStorage` (탭 닫으면 자동 삭제)
- 만료: 로그인 후 8시간 (절대 만료)
- 갱신: 없음 (재로그인 필요)
- 다중 탭: 각 탭 독립 세션 (sessionStorage 특성)
- 보안: localStorage 미사용 (다른 탭/세션 공유 방지)

### 4-4. 관리자 비밀번호 2차 게이트 (settings.html)

```javascript
// settings.html 구현 명세
async function verifyAdminPassword(inputPassword) {
  const candidateId = AuthManager.getCandidateId();
  const passwordHash = await AuthManager.hashPassword(inputPassword);

  const { data } = await supabase
    .from('candidates')
    .select('admin_password')
    .eq('id', candidateId)
    .single();

  return data.admin_password === passwordHash;
}

// 실패 시 잠금 처리
let failCount = 0;
const MAX_ATTEMPTS = 5;
if (failCount >= MAX_ATTEMPTS) {
  // 15분 잠금 (sessionStorage에 lockUntil 저장)
}
```

### 4-5. XSS / CSRF 방어

- 모든 사용자 입력: `innerHTML` 대신 `textContent` 사용
- 외부 스크립트: CDN에서만 로드 (SRI hash 권고)
- CSRF: 별도 백엔드 없으므로 해당 없음 (Supabase JWT 토큰 방식)
- Content-Security-Policy 헤더: Vercel vercel.json에서 설정 권고

---

## 5. 페이지별 구현 명세

### 5-1. index.html (랜딩페이지) — 신규 추가 사항

**현재 상태:** localStorage 기반 설정 폼 (후보자명, 선거지역, 정당, 사진)
**변경 목표:** 회원가입 + 로그인 섹션 추가, Supabase 연동

#### 미인증 상태 UI:

```
[헤더]
  🚨 선거 워룸 — AI 정치 전략 플랫폼

[Hero 섹션]
  기존 플랫폼 소개 유지

[인증 섹션] ← 신규 추가
  ┌─────────────────────┬─────────────────────┐
  │     회원가입         │       로그인         │
  │ ─────────────────── │ ─────────────────── │
  │ 캠프명 (후보자명)    │ 아이디               │
  │ 이메일               │ 비밀번호             │
  │ 비밀번호             │                     │
  │ 비밀번호 확인        │   [로그인 버튼]      │
  │ 선거지역             │                     │
  │ 선거유형             │ 또는                │
  │ 소속정당             │                     │
  │ 프로필 사진 업로드   │ [워룸 둘러보기]     │
  │                     │ (데모 모드)         │
  │   [가입 신청 버튼]   │                     │
  └─────────────────────┴─────────────────────┘

[기능 소개 섹션] (기존 유지)
[메뉴 그리드] (기존 유지)
```

#### 로그인 성공 상태 UI:

```
[헤더]
  👤 김철수 선거 워룸 | [역할: 관리자] | [로그아웃]

[인증 섹션 → 대시보드 안내로 교체]
  ✅ 김철수 캠프에 로그인되었습니다.
  [대시보드 바로가기 →]   [설정 관리] (admin만 표시)
```

#### JavaScript 구현 (신규 함수):

```javascript
// index.html 추가 스크립트

// 페이지 로드 시 인증 상태 체크
document.addEventListener('DOMContentLoaded', async () => {
  if (AuthManager.isAuthenticated()) {
    showLoggedInState();
  } else {
    showAuthSection();
  }
});

// 회원가입 처리
async function handleSignup(event) {
  event.preventDefault();
  const data = {
    name: document.getElementById('signupCampName').value,
    email: document.getElementById('signupEmail').value,
    password: document.getElementById('signupPassword').value,
    confirmPassword: document.getElementById('signupConfirmPassword').value,
    region: document.getElementById('signupRegion').value,
    election_type: document.getElementById('signupElectionType').value,
    party: document.querySelector('input[name="signupParty"]:checked')?.value
  };

  // 검증
  if (data.password !== data.confirmPassword) {
    showError('비밀번호가 일치하지 않습니다.');
    return;
  }

  // 아이디 자동 생성: 이름의 영문 변환 + 연도
  const staffId = generateAccountId(data.name);
  const adminId = 'admin_' + staffId;

  const staffHash = await AuthManager.hashPassword(data.password);
  const adminHash = staffHash; // 초기에는 동일, 설정에서 변경 가능

  // Supabase INSERT
  const { error } = await supabase.from('candidates').insert([{
    name: data.name,
    email: data.email,
    party: data.party,
    region: data.region,
    election_type: data.election_type,
    staff_account_id: staffId,
    staff_password: staffHash,
    admin_account_id: adminId,
    admin_password: adminHash,
    is_active: true,
    signup_at: new Date().toISOString()
  }]);

  if (!error) {
    // 자동 로그인 처리
    await AuthManager.login(staffId, data.password);
    showLoggedInState();
  }
}

// 로그인 성공 후 상태 전환
function showLoggedInState() {
  const campName = AuthManager.getCampName();
  const role = AuthManager.getRole();

  document.getElementById('authSection').style.display = 'none';
  document.getElementById('loggedInSection').style.display = 'block';
  document.getElementById('campNameDisplay').textContent = campName;

  if (role === 'admin') {
    document.getElementById('adminMenuBtn').style.display = 'inline-block';
  }
}
```

---

### 5-2. pages/settings.html (관리자 설정) — 신규 게이트 추가

**현재 상태:** 테마/정당 설정, Supabase 연결 설정, 후보자 정보 폼
**변경 목표:** 역할 기반 접근 제어 + 관리자 비밀번호 2차 게이트

#### 페이지 진입 로직:

```javascript
// settings.html 상단 스크립트
document.addEventListener('DOMContentLoaded', () => {
  // 1단계: 인증 확인
  AuthManager.requireAuth('../pages/login.html');

  const role = AuthManager.getRole();

  if (role === 'admin') {
    // 2단계: 관리자 비밀번호 2차 인증 게이트
    showAdminPasswordGate();
  } else {
    // staff: 제한된 설정만 표시
    showStaffSettings();
  }
});
```

#### 화면 구조:

```
[관리자 비밀번호 게이트 모달]
  ┌────────────────────────────────┐
  │  🔐 관리자 인증                │
  │                                │
  │  관리자 비밀번호를 입력하세요. │
  │  ┌──────────────────────────┐ │
  │  │ ●●●●●●●●                 │ │
  │  └──────────────────────────┘ │
  │                                │
  │  [인증] [취소]                 │
  │                                │
  │  남은 시도: 5회                │
  └────────────────────────────────┘

[인증 성공 후 전체 설정 표시]
  ├── 섹션 1: 후보자 정보
  │     - 후보자명, 선거지역, 선거유형, 소속정당
  │     - 프로필 사진 (Supabase Storage 업로드)
  │     - [저장] 버튼 → candidates 테이블 UPDATE
  │
  ├── 섹션 2: 계정 관리
  │     - 스태프 아이디/비밀번호 변경
  │     - 관리자 비밀번호 변경
  │
  ├── 섹션 3: API 설정
  │     - Gemini API 키, 모델 선택
  │     - Supabase URL/Key 설정
  │
  └── 섹션 4: 데이터 관리
        - localStorage → Supabase 마이그레이션
        - 데이터 초기화 (위험)
```

---

### 5-3. pages/dashboard.html (대시보드) — 인증 필수

**현재 상태:** 레이아웃만 구현, 인증 체크 없음
**변경 목표:** 인증 필수 + 캠프 데이터 로드

```javascript
// dashboard.html 상단
document.addEventListener('DOMContentLoaded', async () => {
  // 인증 필수
  AuthManager.requireAuth('../pages/login.html');

  const candidateId = AuthManager.getCandidateId();
  const campName = AuthManager.getCampName();
  const role = AuthManager.getRole();

  // 캠프 데이터 로드
  const candidate = await SupabaseDB.getCandidate(candidateId);

  // 헤더 업데이트
  document.getElementById('campTitle').textContent =
    `🚨 ${campName} 선거 워룸`;

  // 역할별 메뉴 제어
  if (role !== 'admin') {
    document.querySelectorAll('[data-admin-only]').forEach(el => {
      el.style.display = 'none';
    });
  }

  // 정당 테마 적용
  if (candidate?.party) {
    PartyTheme.setParty(candidate.party);
  }
});
```

---

### 5-4. pages/login.html (로그인) — 기존 유지, 소수 개선

**현재 상태:** 완전히 구현된 로그인 폼 (AuthManager 연동)
**추가 사항:** 회원가입 링크 추가

```html
<!-- login.html 하단 help-section에 추가 -->
<div style="margin-top: 16px; text-align: center;">
  <a href="../index.html#signup" style="color: var(--primary-color); font-size: 13px;">
    캠프를 새로 등록하시겠어요? → 회원가입
  </a>
</div>
```

---

## 6. 기술 스택 확정

| 레이어 | 기술 | 비고 |
|--------|------|------|
| 프론트엔드 | HTML5 / CSS3 / Vanilla JS | 프레임워크 없음 |
| 스타일 | CSS 변수 기반 테마 시스템 | theme.css, responsive.css |
| 인증 | sessionStorage + SHA-256 (Web Crypto API) | auth-manager.js |
| 데이터베이스 | Supabase PostgreSQL | supabase-client.js |
| 파일 저장 | Supabase Storage | profile-photos 버킷 |
| AI | Google Gemini API (gemini-2.0-flash) | 설정에서 키 입력 |
| 배포 | Vercel (정적 호스팅) | vercel.json 설정됨 |
| 벡터 검색 | pgvector (Supabase) | report_chunks 테이블 |

---

## 7. 마이그레이션 계획 (localStorage → Supabase DB)

### Phase 1 (현재 완료)
- candidates 테이블 기본 구조
- blog_articles, competitors_list, app_settings 테이블
- camp_code, admin_password 컬럼 추가
- staff/admin 계정 컬럼 추가

### Phase 2 (이번 스프린트 목표)
- `005_signup_system.sql` 마이그레이션 실행
- index.html 회원가입 폼 추가
- settings.html 관리자 게이트 구현
- dashboard.html 인증 필수 적용
- 모든 페이지: localStorage 읽기를 Supabase 조회로 전환

### Phase 3 (향후)
- Supabase Edge Function으로 bcrypt 전환
- 이메일 인증 (Supabase Auth 통합 고려)
- 관리자 승인 워크플로우 (is_approved 컬럼 활용)

---

## 8. 파일 구조 (신규 추가 파일)

```
10-00-02 정치인 표준 플랫폼/
├── js/
│   ├── auth-manager.js          ← 기존 (signup 메서드 추가 필요)
│   ├── supabase-client.js       ← 기존 (createCampaign 메서드 추가 필요)
│   └── camp-context.js          ← 기존 (Supabase 연동 강화 필요)
├── pages/
│   ├── login.html               ← 기존 (회원가입 링크 소수 추가)
│   ├── settings.html            ← 기존 (관리자 게이트 추가 필요)
│   └── dashboard.html           ← 기존 (인증 체크 추가 필요)
├── index.html                   ← 기존 (회원가입 섹션 추가 필요)
└── database/
    └── migrations/
        ├── 001_initial_schema.sql    ← 기존
        ├── 002_additional_tables.sql ← 기존
        ├── 003_camp_model.sql        ← 기존
        ├── 004_login_accounts.sql    ← 기존
        └── 005_signup_system.sql     ← [신규 생성 필요]
```

---

## 9. 구현 우선순위 (다음 분대 작업 지침)

| 우선순위 | 작업 | 담당 분대 |
|----------|------|-----------|
| P0 | 005_signup_system.sql Supabase에 실행 | Alpha/DB |
| P0 | index.html 회원가입 폼 추가 | Bravo/UI |
| P0 | auth-manager.js signup() 메서드 추가 | Bravo/Auth |
| P1 | settings.html 관리자 게이트 구현 | Charlie/Settings |
| P1 | dashboard.html requireAuth 적용 | Charlie/Dashboard |
| P1 | 모든 페이지 역할별 UI 제어 | Delta/RBAC |
| P2 | Supabase Storage 프로필 사진 업로드 | Bravo/Storage |
| P2 | localStorage → Supabase 마이그레이션 실행 | Alpha/Migration |
| P3 | 관리자 비밀번호 솔트 강화 | Alpha/Security |

---

*Alpha 분대장 서명 — 2026-03-20*
*문서 경로: C:/01 Claude-Code/10-00-02 정치인 표준 플랫폼/ARCHITECTURE_DESIGN.md*

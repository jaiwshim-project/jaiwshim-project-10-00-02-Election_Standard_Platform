# 🔍 디버깅 리뷰 - 작업 세션 문제 분석

**작업 기간:** 2026-03-22
**주요 이슈:** 4가지 문제 (다중 재시도 필요)

---

## 📋 목차
1. [문제 1: 로그인 오류 (window.supabase)](#문제-1-로그인-오류)
2. [문제 2: 회원가입 오류 (SupabaseDB 초기화)](#문제-2-회원가입-오류)
3. [문제 3: 상태 저장 오류 (DB 스키마 부재)](#문제-3-상태-저장-오류)
4. [문제 4: 캠프 삭제 기능 (RLS 정책)](#문제-4-캠프-삭제-기능)

---

## 문제 1: 로그인 오류

### 증상
```
auth-manager.js:70 ❌ 로그인 오류: TypeError: window.supabase.from is not a function
```

### 발생 위치
- `auth-manager.js:38` - login() 함수
- `pages/login.html` - 캠프 로그인 탭

### 근본 원인
```javascript
// ❌ 잘못된 방식
const { data, error } = await window.supabase
  .from('candidates')
  .select(...)

// ✅ 올바른 방식
await SupabaseDB.init();  // 필수!
const { data, error } = await SupabaseDB.client
  .from('candidates')
  .select(...)
```

**핵심:**
- `window.supabase`는 초기화되지 않은 전역 객체
- `SupabaseDB.client`는 초기화 후에만 사용 가능
- `SupabaseDB.init()` 호출 없이는 클라이언트가 null

### 해결 과정
| 시도 | 파일 | 결과 |
|------|------|------|
| 1차 | index.html (handleSignup) | ✅ 수정 완료 |
| 2차 | auth-manager.js (login) | ✅ 수정 완료 |
| 3차 | auth-manager.js (changePassword) | ✅ 수정 완료 |

**총 3개 파일, 3개 함수에서 같은 문제 발생**

### 📌 배운 점
- **전역 검색 필수:** `window.supabase` 사용 지점을 모두 찾아야 함
- **일관성:** 한 파일에서 패턴을 찾으면 다른 파일도 동일 패턴이 있을 가능성
- **초기화 순서:** Supabase 클라이언트는 항상 사용 전에 초기화

### ✅ 다음번 예방법
```javascript
// 함수 시작할 때 항상
async function someFunction() {
  await SupabaseDB.init();
  if (!SupabaseDB.client) {
    throw new Error('Supabase 클라이언트 초기화 실패');
  }
  // 이제 안전하게 사용 가능
}
```

---

## 문제 2: 회원가입 오류

### 증상
```
index.html:1277 회원가입 예외: TypeError: window.supabase.from is not a function
```

### 발생 위치
- `index.html:1276` - handleSignup() 함수

### 근본 원인
**문제 1과 동일:** `window.supabase` 직접 사용

```javascript
// ❌ 처음 코드
const { data, error } = await window.supabase.from('candidates').insert([...])

// ✅ 수정 후
const { data, error } = await SupabaseDB.client.from('candidates').insert([...])
```

### 해결 과정
| 단계 | 액션 | 결과 |
|------|------|------|
| 발견 | 콘솔 오류 확인 | TypeError 식별 |
| 진단 | 코드 검토 | window.supabase 사용 발견 |
| 수정 | SupabaseDB.client로 변경 | ✅ 성공 |
| 커밋 | c92e8b1 | 배포 완료 |

**재시도 횟수:** 1회 (짧음)

### 📌 배운 점
- **콘솔 오류가 명확한 경우** 빠르게 해결됨
- **TypeError는 정확한 위치 제시** → 쉬운 진단
- 문제 1과의 연관성을 빨리 파악했으면 더 빨랐을 것

### ✅ 다음번 예방법
```javascript
// 패턴: Supabase 쿼리 시작 전 체크
const executeQuery = async (queryFn) => {
  if (!SupabaseDB.client) {
    await SupabaseDB.init();
  }
  return queryFn();
};
```

---

## 문제 3: 상태 저장 오류

### 증상
```
najtwocfrlguctmduvfs.supabase.co/rest/v1/candidates?id=eq.xxx:1
Failed to load resource: the server responded with a status of 400 ()

오류: Could not find the 'approval_reason' column of 'candidates' in the schema cache
```

### 발생 위치
- `admin-members.html:283` - saveMemberStatus() 함수
- 회원 상세정보 모달에서 상태 변경 시도

### 근본 원인
**데이터베이스 스키마 부재**

```javascript
// ❌ 존재하지 않는 컬럼 사용
const updateData = {
  approval_status: status,      // ← 컬럼 없음!
  approval_reason: reason,       // ← 컬럼 없음!
  approved_by: admin.adminId,   // ← 컬럼 없음!
  approved_at: new Date()       // ← 컬럼 없음!
};
```

candidates 테이블의 실제 컬럼:
```
name, staff_account_id, admin_account_id,
staff_password, admin_password, is_active, election_type
```

### 해결 과정
| 시도 | 액션 | 결과 |
|------|------|------|
| 1차 | saveMemberStatus 함수 수정 | ❌ 여전히 400 오류 |
| 2차 | AdminAuth.logActivity 매개변수 수정 | ❌ admin_activity_logs 400 오류 |
| 3차 | 상태 필드 제거 | ✅ 성공 |

**총 시도:** 3회 (가장 오래 걸림)

### 문제가 해결되지 않은 이유
1. **DB 스키마를 확인하지 않고 코드만 수정**
   - 콘솔 오류 메시지: "Could not find column"
   - 명확하지만 무시함

2. **가정 기반 개발**
   - "상태 기능이 있을 것"이라고 가정
   - 실제 DB 구조 확인 전에 코드 작성

3. **오류 메시지 해석 부족**
   - 400 오류는 DB 문제 신호
   - 콘솔에 명확한 메시지가 있었음

### 📌 배운 점
- **DB 우선 접근:** 새 기능 추가 전에 스키마 확인 필수
- **오류 메시지 읽기:** "Could not find column" = DB에 컬럼 없음
- **코드가 아닌 데이터 문제일 수 있음**

### ✅ 다음번 예방법
```javascript
// 단계 1: DB 스키마 확인
// SELECT * FROM candidates LIMIT 1;  // 실제 컬럼 확인

// 단계 2: 존재하는 컬럼만 사용
// 컬럼이 없으면 먼저 추가
// ALTER TABLE candidates ADD COLUMN approval_status TEXT;

// 단계 3: 코드 작성
const updateData = {
  // 존재하는 컬럼만
};
```

---

## 문제 4: 캠프 삭제 기능

### 증상
```
✅ 삭제 성공 메시지 표시
BUT 테이블에는 여전히 캠프 존재
```

### 발생 위치
- `admin-members.html:284-301` - deleteMember() 함수

### 근본 원인
**Supabase RLS (Row Level Security) 정책**

```
DELETE 쿼리 응답: {
  data: Array(0),              // 삭제된 레코드 없음
  error: null,                 // 하지만 오류 없음
  status: 200,                 // HTTP 200 (성공)
  삭제된_레코드_수: 0          // 실제로는 삭제 안 됨
}
```

**이유:**
- Supabase RLS가 DELETE 작업을 차단
- 오류가 반환되지 않음 (정책에 의한 조용한 실패)
- HTTP 200이지만 실제 삭제 안 됨

### 해결 과정
| 시도 | 액션 | 결과 |
|------|------|------|
| 1차 | 삭제 후 loadMembers() 호출 | ❌ 테이블에 여전히 표시 |
| 2차 | 지연 시간 추가 (500ms→800ms) | ❌ 여전히 표시 |
| 3차 | 상세 로깅 추가 | ✅ 원인 파악: 0개 삭제됨 |
| 4차 | Supabase RLS 정책 수정 | ✅ 삭제 성공 |

**총 시도:** 4회 (가장 많음, 약 1시간 소요)

### 문제가 해결되지 않은 이유
1. **HTTP 200의 함정**
   - 200 = 성공으로 착각
   - 실제로는 정책에 의한 조용한 실패

2. **로깅 부재**
   - 초기에 DELETE 응답 내용 확인 안 함
   - "data: Array(0)" = 삭제된 레코드 0 → 힌트!

3. **DB 구조 외부 요인**
   - RLS 정책은 코드가 아닌 DB 레벨 설정
   - 개발자가 직접 접근 어려움

4. **점진적 디버깅 부족**
   - 삭제 성공 여부를 명확히 검증하지 않음
   - "data.length > 0" 체크 필수였음

### 📌 배운 점
- **HTTP 상태 코드만으로는 부족**
  - 200이어도 실제 작업 완료 여부 확인 필요
  - `.select()` 사용해 삭제된 레코드 반환받기

- **조용한 실패 (Silent Failure) 감지**
  - 오류 없이 작동하지 않는 경우 주의
  - 응답 데이터 상세 검사 필수

- **RLS는 보안이지만 복잡함**
  - DB 레벨 정책이 코드에 숨겨진 영향
  - 초기 테스트 시 RLS 비활성화 후 기능 검증

### ✅ 다음번 예방법
```javascript
// 1단계: 삭제 확인
const { data, error } = await SupabaseDB.client
  .from('table')
  .delete()
  .eq('id', id)
  .select();  // ← 삭제된 레코드 반환받기

// 2단계: 검증 (필수!)
if (!data || data.length === 0) {
  console.warn('⚠️ 삭제 실패 - RLS 정책 확인');
  // RLS 정책이 DELETE를 차단했을 가능성
  return;
}

// 3단계: 성공
toast('삭제되었습니다');
await loadMembers();  // 화면 갱신
```

---

## 🎯 종합 분석

### 문제별 소요 시간
| 문제 | 유형 | 시도 | 시간 |
|------|------|------|------|
| 1. window.supabase | 코드 | 3회 | 15분 |
| 2. SupabaseDB 초기화 | 코드 | 1회 | 5분 |
| 3. 없는 컬럼 | DB | 3회 | 20분 |
| 4. RLS 정책 | DB | 4회 | 60분 |
| **합계** | - | **11회** | **100분** |

### 실패 패턴 분석
```
코드 문제 (60%)      → 빠른 해결 (콘솔 오류 명확)
├─ TypeError         → 1~2회 시도
└─ 초기화 누락       → 1회 시도

데이터/인프라 문제 (40%)  → 느린 해결 (원인 숨김)
├─ 없는 스키마       → 3회 시도
└─ RLS 정책          → 4회 시도
```

### 공통점
1. **초기 진단 부족**
   - 콘솔 오류를 제대로 읽지 않음
   - "400 오류" → DB 문제 신호

2. **가정 기반 접근**
   - 실제 상태 확인 전에 수정 시도
   - "아마 이렇겠지" 식 코딩

3. **외부 요인 간과**
   - Supabase 설정 (RLS, 스키마)
   - 코드가 아닌 DB 구조 확인 필요

---

## ✨ 개선 체크리스트

### 새로운 기능 추가 시
- [ ] DB 스키마 먼저 확인
- [ ] 필요한 컬럼 미리 추가
- [ ] RLS 정책 확인 (필요시 테스트용 비활성화)
- [ ] 코드 작성 전에 DB 준비 완료

### 오류 발생 시
- [ ] 콘솔 오류 전문 읽기
- [ ] 오류 유형 분류 (코드/DB/네트워크)
- [ ] 관련 파일 전체 grep (같은 패턴)
- [ ] HTTP 상태 코드 + 응답 데이터 모두 확인

### 데이터 변경 기능 (CREATE/UPDATE/DELETE)
- [ ] `.select()` 추가해 변경 내용 확인
- [ ] `data.length > 0` 검증
- [ ] RLS 정책이 작업을 차단했는지 확인
- [ ] 로깅: 변경 전/후 데이터 기록

### 디버깅 전략
```
1단계: 콘솔 오류 읽기
       ↓
2단계: 오류 유형 분류 (코드? DB? 정책?)
       ↓
3단계: 원인별 접근
       ├─ TypeError → 코드 검토
       ├─ "column not found" → DB 스키마 확인
       └─ 200이지만 작동 안 함 → RLS 정책 확인
       ↓
4단계: 전체 검색 (다른 파일도 같은 문제?)
       ↓
5단계: 근본 원인 제거 (증상 치료 아님)
```

---

## 📚 참고 자료

### Supabase 주요 개념
- **RLS (Row Level Security):** DB 레벨 접근 제어
- **스키마:** 테이블 구조 (컬럼 정의)
- **HTTP 200:** 요청 처리 성공 (실제 작업과 별개)

### 한번에 해결되지 않은 이유
```
문제 유형        해결 방법         소요 시간
─────────────────────────────────────────
코드 버그        콘솔 읽기        5~15분
DB 스키마        쿼리 또는 UI      15~20분
정책/권한        설정 수정         45~60분
                 (외부 접근)
```

---

**작성일:** 2026-03-22
**목표:** 향후 유사 문제 발생 시 평균 해결 시간 50% 단축

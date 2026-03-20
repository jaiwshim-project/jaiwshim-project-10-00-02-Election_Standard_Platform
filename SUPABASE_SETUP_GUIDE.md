# Supabase 설정 가이드

> 작성일: 2026-03-20 | 플랫폼: 선거 워룸 AI 플랫폼

---

## 📋 목차
1. [Supabase 프로젝트 생성](#1-supabase-프로젝트-생성)
2. [마이그레이션 실행](#2-마이그레이션-실행)
3. [RLS 정책 설정](#3-rls-정책-설정)
4. [Storage 버킷 생성](#4-storage-버킷-생성)
5. [환경 변수 설정](#5-환경-변수-설정)
6. [검증](#6-검증)

---

## 1. Supabase 프로젝트 생성

### 1-1. 계정 생성
- [supabase.com](https://supabase.com) 방문
- GitHub/Google로 로그인 또는 이메일 가입
- 프로젝트 생성

### 1-2. 프로젝트 설정
```
프로젝트명: election-warroom
지역: Asia, Singapore (또는 Seoul)
데이터베이스 암호: 안전한 비밀번호 설정 (저장해두세요)
```

### 1-3. API Keys 확보
Supabase Dashboard → Settings → API → Copy
```
✅ Project URL: https://xxxxx.supabase.co
✅ anon (public) key: eyJhbG...
✅ service_role key: eyJhbG... (비밀 - 서버에서만 사용)
```

---

## 2. 마이그레이션 실행

### 단계 1: SQL Editor 열기
1. Supabase Dashboard → SQL Editor
2. "New query" 버튼 클릭

### 단계 2: 마이그레이션 SQL 복사
파일: `database/migrations/005_signup_system.sql`
```sql
-- 파일 내용 전체 복사
ALTER TABLE candidates
  ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
  ...
```

### 단계 3: 실행
1. SQL Editor에 붙여넣기
2. "▶ Run" 버튼 클릭
3. 완료 메시지 확인: "Migration 005_signup_system.sql completed successfully"

### 마이그레이션 확인
```sql
-- 새 컬럼 확인
SELECT column_name FROM information_schema.columns
WHERE table_name = 'candidates'
  AND column_name IN ('email', 'election_type', 'profile_photo_url');

-- 인덱스 확인
SELECT * FROM pg_indexes WHERE tablename = 'candidates';
```

---

## 3. RLS 정책 설정

### 단계 1: RLS 활성화 확인
1. Supabase Dashboard → Database → Tables → candidates
2. "RLS" 섹션 확인
3. "Enable RLS" 버튼 클릭 (아직 안 되어 있으면)

### 단계 2: RLS 정책 SQL 실행
파일: `database/rls_policies.sql`
```sql
-- SQL Editor에 복사-붙여넣기
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "candidates_select_by_account_id" ...
```

### 단계 3: 정책 확인
```sql
SELECT * FROM pg_policies WHERE tablename = 'candidates';
```

**예상 결과:**
- `candidates_select_by_account_id`
- `candidates_insert_signup`
- `candidates_select_admin`
- (추가 정책)

---

## 4. Storage 버킷 생성

### 단계 1: Storage 설정
1. Supabase Dashboard → Storage
2. "Create a new bucket" 클릭

### 단계 2: 버킷 생성
```
버킷명: campaign-assets
접근성: Public
```

### 단계 3: 파일 정책 설정
Storage → campaign-assets → "Policies" 탭

**읽기 정책 (모든 사용자 가능):**
```sql
CREATE POLICY "Allow public read"
ON storage.objects
FOR SELECT
USING (bucket_id = 'campaign-assets');
```

**쓰기 정책 (인증된 사용자만):**
```sql
CREATE POLICY "Allow authenticated upload"
ON storage.objects
FOR INSERT
WITH CHECK (
  bucket_id = 'campaign-assets'
  AND auth.role() = 'authenticated'
);
```

---

## 5. 환경 변수 설정

### 방법 1: localStorage 설정 (클라이언트)
브라우저 콘솔에서 실행:
```javascript
// Supabase URL과 Key 저장
localStorage.setItem('supabaseUrl', 'https://xxxxx.supabase.co');
localStorage.setItem('supabaseKey', 'eyJhbG...');

// 확인
console.log(localStorage.getItem('supabaseUrl'));
```

### 방법 2: HTML 페이지에서 설정
`pages/settings.html` 또는 `index.html`에 설정 폼 추가:
```html
<!-- Supabase API 키 설정 폼 -->
<div class="settings-section">
  <h3>🔧 Supabase 연결 설정</h3>
  <label>
    Supabase URL:
    <input type="text" id="supabaseUrl" placeholder="https://xxxxx.supabase.co" />
  </label>
  <label>
    Supabase Key (anon):
    <input type="password" id="supabaseKey" placeholder="eyJhbG..." />
  </label>
  <button onclick="saveSupabaseSettings()">저장</button>
</div>

<script>
function saveSupabaseSettings() {
  const url = document.getElementById('supabaseUrl').value;
  const key = document.getElementById('supabaseKey').value;

  if (!url || !key) {
    alert('URL과 Key를 입력하세요');
    return;
  }

  localStorage.setItem('supabaseUrl', url);
  localStorage.setItem('supabaseKey', key);
  alert('✅ Supabase 설정 저장됨');
}
</script>
```

---

## 6. 검증

### 테스트 1: 연결 확인
브라우저 콘솔에서:
```javascript
// Supabase 초기화 테스트
const supabaseUrl = localStorage.getItem('supabaseUrl');
const supabaseKey = localStorage.getItem('supabaseKey');

if (supabaseUrl && supabaseKey) {
  const client = window.supabase.createClient(supabaseUrl, supabaseKey);

  // candidates 테이블 조회
  client
    .from('candidates')
    .select('*')
    .limit(1)
    .then(({ data, error }) => {
      if (error) {
        console.error('❌ 에러:', error);
      } else {
        console.log('✅ 연결 성공:', data);
      }
    });
}
```

### 테스트 2: 회원가입 흐름
1. `index.html` 방문
2. "✍️ 회원가입" 탭 클릭
3. 폼 입력:
   - 캠프명: 테스트캠프
   - 스탭 ID: test2024
   - 관리자 ID: admin_test2024
   - 비밀번호: Test1234!
4. "가입" 버튼 클릭
5. Supabase Dashboard → Database → candidates → 데이터 확인

### 테스트 3: 로그인 흐름
1. `index.html` 방문
2. "🔑 로그인" 탭 클릭
3. 방금 생성한 계정으로 로그인
4. 성공 메시지 확인
5. "🚀 선거 워룸 바로가기" 버튼 표시 확인

### 테스트 4: 관리자 설정 접근
1. `pages/settings.html` 방문
2. 관리자 비밀번호 입력
3. 후보자 정보 폼 표시 확인
4. 프로필 사진 업로드 테스트

---

## 📊 완료 체크리스트

- [ ] Supabase 프로젝트 생성 및 API Keys 확보
- [ ] 마이그레이션 005 실행 (candidates 테이블 확장)
- [ ] RLS 정책 생성
- [ ] Storage 버킷 생성 (campaign-assets)
- [ ] localStorage에 supabaseUrl/supabaseKey 저장
- [ ] 브라우저 콘솔에서 연결 테스트
- [ ] 회원가입 흐름 테스트
- [ ] 로그인 흐름 테스트
- [ ] 관리자 설정 페이지 접근 테스트

---

## 🔗 참고 자료

- [Supabase 공식 문서](https://supabase.com/docs)
- [Supabase JavaScript SDK](https://supabase.com/docs/reference/javascript)
- [Row Level Security (RLS)](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage API](https://supabase.com/docs/guides/storage)

---

## ⚠️ 주의사항

1. **anon key 노출**: localStorage에는 anon key만 저장하세요. service_role key는 서버에서만 사용.
2. **RLS 정책**: 현재 구현은 sessionStorage 기반이므로, app level에서 역할 확인.
3. **프로필 사진**: Supabase Storage에 업로드되지만, 이미지 URL은 DB에 저장해야 함.
4. **이메일 인덱스**: 회원가입 시 이메일 중복 확인을 위해 UNIQUE 인덱스 활용.

---

## 🚀 다음 단계

설정 완료 후:
1. 모든 페이지에서 Supabase 데이터 사용으로 전환
2. localStorage → Supabase 마이그레이션 (`SupabaseDB.migrateFromLocalStorage()`)
3. 백엔드 API 구축 (Node.js/Python)
4. Supabase Auth 통합 (현재는 수동 login-based)

---

작성: Alpha 분대 | 검증: Bravo/Charlie 분대

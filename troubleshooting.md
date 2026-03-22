# 🔧 Troubleshooting Guide - 선거 워룸 문제 진단 및 해결책

## 📌 빠른 진단 (Quick Diagnostic)

```javascript
// F12 → Console에서 실행하여 현재 상태 확인
console.log({
  campSession: localStorage.getItem('campSession'),
  candidateId: localStorage.getItem('candidateId'),
  campName: localStorage.getItem('campName'),
  supabaseUrl: localStorage.getItem('supabaseUrl'),
  isSupabaseConnected: !!window.supabase?.createClient
});
```

---

## 🚨 문제별 해결책

### 1. 로그인 관련 오류

#### 문제: "존재하지 않는 계정입니다" 또는 "비밀번호가 틀렸습니다"

**진단:**
```javascript
// 1. Supabase 연결 확인
localStorage.getItem('supabaseUrl')  // null이면 Supabase 미설정
localStorage.getItem('supabaseKey')  // null이면 Supabase 미설정

// 2. 입력 값 확인
console.log('입력한 아이디:', document.getElementById('loginId')?.value);
console.log('입력한 비밀번호 길이:', document.getElementById('loginPassword')?.value?.length);
```

**해결책:**
1. **Supabase 자격증명 확인:**
   - Settings 페이지 → Supabase URL/Key 입력
   - 또는 localStorage에 자동 저장됨

2. **계정 존재 여부 확인:**
   - Supabase 대시보드 → candidates 테이블
   - staff_account_id 또는 admin_account_id 확인

3. **비밀번호 재설정:**
   - admin-members.html에서 관리자가 비밀번호 설정
   - 최소 8자 이상

---

#### 문제: 로그인 후 candidateId가 null

**원인:** auth-manager.js에서 localStorage에 candidateId 저장 안 함

**진단:**
```javascript
// 로그인 후 확인
localStorage.getItem('candidateId')  // null이면 로그인 실패
sessionStorage.getItem('campSession')  // 있으면 로그인됨
```

**해결책:**
1. **브라우저 새로고침 (Ctrl+F5)**
   - 최신 코드 로드

2. **수동으로 localStorage에 설정** (임시):
   ```javascript
   // Supabase 대시보드에서 candidates 테이블의 ID 복사
   localStorage.setItem('candidateId', 'UUID-HERE');
   ```

3. **코드 확인:** auth-manager.js line 63-65에 다음 있는지 확인:
   ```javascript
   localStorage.setItem('candidateId', data.id);
   localStorage.setItem('campName', data.name);
   ```

---

### 2. Supabase 초기화 오류

#### 문제: "Supabase 초기화 중입니다" 또는 "window.supabase.createClient is not a function"

**원인:**
- Supabase 라이브러리가 로드되지 않음
- 중복 초기화로 인한 충돌
- SupabaseDB.client가 undefined

**진단:**
```javascript
console.log('window.supabase 타입:', typeof window.supabase);
console.log('SupabaseDB.client:', typeof SupabaseDB?.client);
console.log('라이브러리 로드 여부:', !!window.supabase?.createClient);
```

**해결책:**

1. **스크립트 로드 순서 확인:**
   ```html
   <!-- 올바른 순서 -->
   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
   <script src="../js/supabase-client.js"></script>
   <script src="../js/auth-manager.js"></script>
   ```

2. **중복 초기화 제거:**
   - external-materials.html에서 inline 초기화 제거
   - supabase-client.js에서만 초기화

3. **SupabaseDB 초기화 호출:**
   ```javascript
   await SupabaseDB.init();
   console.log(SupabaseDB.client); // client object 확인
   ```

---

#### 문제: "파일 업로드 실패: Bucket not found"

**원인:** Supabase Storage에 'campaign-files' 버킷 미생성

**해결책:**

**방법 1: SQL로 생성** (권장)
```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('campaign-files', 'campaign-files', true)
ON CONFLICT (id) DO NOTHING;
```

**방법 2: Supabase 대시보드**
1. Storage → Create new bucket
2. 버킷명: `campaign-files`
3. Public bucket 체크
4. Create bucket

---

### 3. 파일 업로드 오류

#### 문제: "파일 저장에 실패했습니다"

**진단:**
```javascript
// F12 → Console 확인
// 다음 중 어떤 에러인지 확인:
// 1. "invalid input syntax for type uuid: local-user"
// 2. "new row violates row-level security policy"
// 3. "Cannot read properties of undefined"
```

**해결책별:**

**1. UUID 에러 ("invalid input syntax for type uuid: local-user")**
- 로그인하지 않음
- 해결: 캠프 계정으로 로그인 후 시도

**2. RLS 정책 에러 ("new row violates row-level security policy")**
```sql
-- shared_files 테이블 RLS 정책 추가
CREATE POLICY "Allow all inserts"
ON public.shared_files FOR INSERT
WITH CHECK (true);

-- Storage RLS 정책 추가
CREATE POLICY "Allow public uploads"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'campaign-files');

CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
USING (bucket_id = 'campaign-files');
```

**3. undefined 에러**
```javascript
// file-store-cloud.js에서 SupabaseDB.client 사용 확인
console.log('SupabaseDB.client:', SupabaseDB?.client);
```

---

#### 문제: "캠프 관리자 비밀번호가 틀렸습니다"

**원인:**
- admin_password가 설정되지 않음
- 비밀번호 해싱 불일치
- staff_password와 다른 password 입력

**진단:**
```javascript
// 1. admin_password 확인
localStorage.getItem('candidateId')  // UUID 확인
// Supabase 대시보드에서 candidates 테이블의 admin_password 확인

// 2. 입력한 비밀번호 확인
document.getElementById('uploadPassword').value  // 입력값 확인
```

**해결책:**

1. **admin_password 설정:**
   - admin-members.html에서 캠프 선택
   - "관리자 비밀번호" 입력 (최소 8자)
   - 저장 후 "✅ 설정됨" 표시 확인

2. **올바른 비밀번호 입력:**
   - 캠프 생성 시 설정한 비밀번호
   - 또는 admin-members.html에서 설정한 비밀번호

3. **password 해싱 불일치:**
   ```javascript
   // 수동 테스트
   const pw = '123456789';
   const hash = await AuthManager.hashPassword(pw);
   console.log('계산된 해시:', hash);
   // Supabase에서 저장된 해시와 비교
   ```

---

### 4. 페이지 접근 오류

#### 문제: "external-materials.html에 접근하면 로그인 안 됨"

**원인:** 직접 URL로 접근 → candidateId 없음

**올바른 접근 방법:**
```
1. https://10-00-02.vercel.app 방문
2. "🔑 로그인" 탭에서 캠프 로그인
3. 로그인 완료 후 대시보드에서 "외부 자료" 탭 선택
```

**대신 직접 접근하면:**
```
❌ https://10-00-02.vercel.app/pages/external-materials.html
   → candidateId가 "local-user"가 됨 → UUID 오류
```

---

## 🔍 고급 진단 (Advanced Debugging)

### 상세 에러 로깅 활성화

```javascript
// external-materials.html의 uploadFileNow() 함수에서:
console.log('🔍 파일 업로드 시작:', {
  candidateId: localStorage.getItem('candidateId'),
  fileName: file.name,
  fileSize: file.size,
  fileType: file.type,
  uploadType: type
});
```

### Supabase 네트워크 요청 확인

```javascript
// F12 → Network 탭에서:
// 1. GET /rest/v1/candidates - 캠프 조회
// 2. POST /rest/v1/shared_files - 메타데이터 저장
// 3. POST /storage/v1/b/campaign-files/o - 파일 업로드

// 각각의 상태 코드와 응답 확인
```

### RLS 정책 디버깅

```sql
-- 현재 RLS 정책 확인
SELECT * FROM pg_policies
WHERE schemaname = 'public';

-- shared_files 테이블의 정책만 보기
SELECT * FROM pg_policies
WHERE tablename = 'shared_files';
```

---

## ✅ 체크리스트 (Pre-Launch Checklist)

### 필수 설정 항목
- [ ] Supabase 프로젝트 생성
- [ ] campaign-files 버킷 생성
- [ ] shared_files 테이블 RLS 정책 설정
- [ ] storage.objects RLS 정책 설정
- [ ] 테스트 캠프 계정 생성
- [ ] admin-members.html에서 관리자 비밀번호 설정

### 배포 전 테스트
- [ ] 캠프 로그인 성공
- [ ] localStorage에 candidateId 저장됨
- [ ] 파일 업로드 성공
- [ ] 비밀번호 검증 성공

### 환경변수 확인
- [ ] Supabase URL 설정됨
- [ ] Supabase API Key 설정됨
- [ ] 로컬/개발/프로덕션별로 다른 Key 사용

---

## 📞 문제 해결 플로우

```
1. 에러 메시지 기록
2. F12 Console에서 진단 코드 실행
3. localStorage/sessionStorage 확인
4. Supabase 대시보드에서 데이터 확인
5. Network 탭에서 API 요청/응답 확인
6. 해당 파일의 코드 검토
7. 필요시 SQL 정책 수정
8. 브라우저 새로고침 (Ctrl+F5) 후 재시도
```

---

## 🔗 관련 파일 맵

| 기능 | 파일 | 역할 |
|------|------|------|
| 캠프 로그인 | js/auth-manager.js | candidateId 저장 |
| Supabase 초기화 | js/supabase-client.js | SupabaseDB 초기화 |
| 파일 업로드 | js/file-store-cloud.js | Storage 및 메타데이터 저장 |
| 관리자 비밀번호 | pages/admin-members.html | 비밀번호 설정 |
| 파일 업로드 UI | pages/external-materials.html | 비밀번호 검증 및 업로드 |

---

**마지막 업데이트:** 2026-03-23
**작성:** Claude Haiku 4.5

# Vercel 배포 가이드

> 작성일: 2026-03-20 | 플랫폼: 선거 워룸 AI 플랫폼

---

## 📋 개요

Vercel은 정적 사이트 호스팅 및 서버리스 함수를 제공하는 플랫폼입니다. 선거 워룸 플랫폼을 Vercel에 배포하면:

- ✅ 자동 HTTPS (SSL/TLS)
- ✅ CDN을 통한 글로벌 캐싱
- ✅ 자동 배포 (GitHub 연동)
- ✅ 환경 변수 관리
- ✅ 실시간 로그 확인

---

## 🚀 배포 단계

### Step 1: Vercel 계정 생성

1. [vercel.com](https://vercel.com) 방문
2. GitHub 계정으로 로그인 (또는 이메일 가입)
3. 프로젝트 인증

### Step 2: GitHub 저장소 연결

1. Vercel Dashboard → "New Project"
2. "Import Git Repository" 클릭
3. GitHub 저장소 선택: `10-00-02-Election_Standard_Platform`
4. Root Directory: `./` (또는 프로젝트 루트)
5. "Deploy" 클릭

### Step 3: 환경 변수 설정

**배포 중 또는 배포 후:**

1. Vercel Dashboard → Project Settings → Environment Variables
2. 다음 변수 추가:

```
이름: SUPABASE_URL
값: https://xxxxx.supabase.co
범위: Production, Preview, Development
```

```
이름: SUPABASE_KEY
값: eyJhbG... (anon key)
범위: Production, Preview, Development
```

3. "Save" 클릭
4. 재배포 (또는 자동 재배포 대기)

### Step 4: 배포 확인

1. Vercel Dashboard → Deployments
2. 최신 배포 클릭
3. URL 확인: `https://election-warroom-xxxxx.vercel.app`
4. 브라우저에서 열어서 테스트

---

## 🔧 배포 설정 (vercel.json)

프로젝트에 포함된 `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_KEY": "@supabase_key"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600"
        }
      ]
    }
  ]
}
```

**주요 설정:**
- `builds`: 정적 파일 빌드
- `routes`: URL 라우팅 규칙
- `env`: 환경 변수 매핑
- `headers`: HTTP 헤더 (캐싱, 보안)

---

## ✅ 배포 후 검증

### 1. 기본 페이지 접근
```
https://your-project.vercel.app/
```
✅ 랜딩페이지 표시되는지 확인

### 2. 회원가입/로그인 테스트
```javascript
// 브라우저 콘솔에서 실행
localStorage.setItem('supabaseUrl', 'https://xxxxx.supabase.co');
localStorage.setItem('supabaseKey', 'eyJhbG...');

// 페이지 새로고침
location.reload();
```

### 3. Supabase 연결 확인
```javascript
// 콘솔에서
console.log(localStorage.getItem('supabaseUrl'));
// ✅ URL이 출력되면 성공
```

### 4. 페이지별 접근 확인
- [ ] `/index.html` — 랜딩페이지
- [ ] `/pages/login.html` — 로그인 페이지
- [ ] `/pages/dashboard.html` — 대시보드 (인증 필요)
- [ ] `/pages/settings.html` — 설정 (관리자 전용)

---

## 🔄 자동 배포 (GitHub 연동)

### GitHub Push → 자동 배포

1. 로컬에서 코드 변경 및 커밋
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push origin main
   ```

2. Vercel은 자동으로:
   - GitHub 변경 감지
   - 새 Preview 배포 생성 (PR 시)
   - Production 배포 실행 (main branch 시)

3. 배포 상태 확인:
   - Vercel Dashboard → Deployments
   - GitHub PR 댓글에 배포 URL 표시

---

## 📊 성능 최적화

### 1. 캐싱 전략
```json
{
  "headers": [
    {
      "source": "/css/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

- CSS/JS: 1년 캐싱 (파일명 변경 시 무효화)
- HTML: 1시간 캐싱 (자주 변경됨)

### 2. CDN 활용
Vercel은 자동으로:
- 전 세계 CDN으로 정적 파일 배포
- 사용자 위치에서 가장 가까운 서버에서 제공
- 성능 향상 (로딩 시간 단축)

### 3. 이미지 최적화
프로필 사진 등은 Supabase Storage에서 제공:
- Vercel 서버 부하 감소
- 이미지 CDN 활용

---

## 🔐 보안 설정

### 1. HTTPS 자동 설정
- Vercel은 모든 배포에 자동 SSL 인증서 발급
- HTTPS 강제 리다이렉트 활성화

### 2. 환경 변수 보안
- **절대 코드에 API 키 하드코딩 금지**
- Vercel Environment Variables 사용
- localStorage에만 anon key 저장 (service_role key는 비공개)

### 3. HTTP 헤더 보안
```json
{
  "headers": [
    {
      "key": "X-Content-Type-Options",
      "value": "nosniff"
    },
    {
      "key": "X-Frame-Options",
      "value": "SAMEORIGIN"
    }
  ]
}
```

---

## 🆘 트러블슈팅

### 문제 1: 404 에러 (페이지를 찾을 수 없음)

**증상:**
```
404 - This page could not be found
```

**해결:**
1. `vercel.json`의 `routes` 확인
2. 파일 경로 확인 (대소문자 구분)
3. 재배포: Vercel Dashboard → "Redeploy"

### 문제 2: Supabase 연결 실패

**증상:**
```
⚠️ Supabase 설정이 필요합니다.
```

**해결:**
1. 환경 변수 확인: Settings → Environment Variables
2. 변수명 정확히 입력: `SUPABASE_URL`, `SUPABASE_KEY`
3. 값 확인: 복사-붙여넣기 시 공백 없이 확인
4. 재배포 필요

### 문제 3: 캐싱 문제 (옛날 버전 보임)

**증상:**
```
새 코드가 반영되지 않음 (캐시된 버전 보임)
```

**해결:**
1. 브라우저 캐시 삭제: Ctrl+Shift+Delete
2. 개발자 도구 → Network → "Disable cache" 체크
3. 또는 프라이빗 탭에서 테스트

### 문제 4: 환경 변수 미적용

**증상:**
```
Production에서는 작동하지만 Preview에서는 안 됨
```

**해결:**
1. Environment Variables → 각 변수의 "범위(Scope)" 확인
2. "Preview"와 "Production" 모두 체크
3. 재배포

---

## 📈 모니터링

### Vercel Analytics
1. Vercel Dashboard → Analytics
2. 트래픽, 성능, 에러 확인
3. 성능 최적화 제안 참고

### 실시간 로그
1. Vercel Dashboard → Deployments → 최신 배포
2. "Logs" 탭 → 실시간 로그 확인
3. 에러 디버깅 시 유용

---

## 🎯 배포 체크리스트

- [ ] GitHub 저장소 생성 및 코드 푸시
- [ ] Vercel 계정 생성
- [ ] GitHub 저장소 연결
- [ ] 환경 변수 설정 (SUPABASE_URL, SUPABASE_KEY)
- [ ] 배포 완료 및 URL 확인
- [ ] 랜딩페이지 접근 테스트
- [ ] Supabase 연결 테스트
- [ ] 회원가입/로그인 흐름 테스트
- [ ] 관리자 설정 페이지 테스트
- [ ] 성능 최적화 (Lighthouse 점수 확인)

---

## 🚀 프로덕션 배포 완료

배포 후:
1. 도메인 커스터마이징 (선택사항)
   - Vercel Dashboard → Settings → Domains
   - 커스텀 도메인 추가: `election-warroom.com` 등

2. 팀 협업 설정 (선택사항)
   - Settings → Team → 멤버 초대
   - 역할 설정: Admin, Member, Viewer

3. 배포 알림 설정 (선택사항)
   - Integrations → Slack/Discord 연동
   - 배포 성공/실패 알림 수신

---

## 📞 지원

- Vercel 공식 문서: https://vercel.com/docs
- 커뮤니티: https://github.com/vercel/vercel

---

작성: 소대 | 배포 설정: Vercel v2 정적 사이트 호스팅

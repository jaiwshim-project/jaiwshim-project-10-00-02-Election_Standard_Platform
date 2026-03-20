# GitHub 저장소 생성 및 Vercel 연결

> 선거 워룸 플랫폼 배포 사전 단계

---

## 📋 Step 1: GitHub 저장소 생성

### 1-1. GitHub에 로그인
- [github.com](https://github.com) 방문
- 로그인

### 1-2. 새 저장소 생성
1. 우상단 "+" → "New repository" 클릭
2. 저장소 설정:
   ```
   Repository name: 10-00-02-Election-Standard-Platform
   Description: AI 정치 전략 플랫폼 - 선거 워룸
   Visibility: Public
   Initialize: ❌ (기존 코드가 있으므로 체크하지 않음)
   ```
3. "Create repository" 클릭

### 1-3. 로컬 저장소 연결
```bash
cd "C:\01 Claude-Code\10-00-02 정치인 표준 플랫폼"

# 기존 origin 확인
git remote -v

# 기존 origin이 없는 경우: 새로 추가
git remote add origin https://github.com/YOUR_USERNAME/10-00-02-Election-Standard-Platform.git

# 기존 origin을 교체해야 하는 경우:
git remote set-url origin https://github.com/YOUR_USERNAME/10-00-02-Election-Standard-Platform.git

# main 브랜치로 변경 (master → main)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

### 1-4. GitHub에서 확인
1. GitHub 저장소 페이지 방문
2. 파일이 업로드되었는지 확인
3. commit 히스토리 확인

---

## 🚀 Step 2: Vercel 연결 및 배포

### 2-1. Vercel에 로그인
1. [vercel.com](https://vercel.com) 방문
2. GitHub 계정으로 로그인

### 2-2. GitHub 저장소 연결
1. Vercel Dashboard → "New Project"
2. "Import Git Repository"
3. GitHub에서 인증 (처음이면)
4. 저장소 검색: `10-00-02-Election-Standard-Platform`
5. 선택하고 "Import"

### 2-3. Vercel 프로젝트 설정
```
Project Name: election-warroom
Framework: Other (정적 사이트)
Root Directory: ./
Build & Output Settings:
  Build Command: (비워둠 — 정적 사이트)
  Output Directory: ./
```

### 2-4. 환경 변수 설정
"Environment Variables" 섹션에서 추가:

```
SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_KEY = eyJhbG... (anon key)
```

**범위:** Production, Preview, Development 모두 체크

### 2-5. 배포
"Deploy" 클릭 → 배포 시작 (약 30초~1분)

배포 완료 후:
```
🎉 Deployment Successful!
URL: https://election-warroom-xxxxx.vercel.app
```

---

## ✅ 배포 후 검증

### 1. 접근 테스트
```
https://election-warroom-xxxxx.vercel.app/
```

### 2. Supabase 연결
브라우저 콘솔:
```javascript
localStorage.setItem('supabaseUrl', 'https://xxxxx.supabase.co');
localStorage.setItem('supabaseKey', 'eyJhbG...');
location.reload();
```

### 3. 기능 테스트
- [ ] 랜딩페이지 로드
- [ ] 회원가입 폼 표시
- [ ] 로그인 폼 표시
- [ ] Supabase 연결 확인

---

## 🔄 GitHub Push 명령어 정리

```bash
# 1. 로컬 변경사항 확인
git status

# 2. 모든 파일 스테이징
git add .

# 3. 커밋
git commit -m "feat: Complete election warroom platform"

# 4. GitHub에 푸시
git push origin main

# 5. Vercel 자동 배포 (GitHub 연동 시)
# → Vercel이 자동으로 감지하고 배포
```

---

## 📊 Vercel 대시보드 활용

### 배포 모니터링
1. Vercel Dashboard → Deployments
2. 최신 배포 클릭
3. Status 확인 (✅ Success 또는 ❌ Failed)

### 실시간 로그
1. Deployments → 최신 배포
2. "Logs" 탭
3. 에러 디버깅

### 성능 분석
1. Analytics 탭
2. 로딩 시간, 트래픽 확인
3. Lighthouse 점수 확인

---

## 🆘 자주하는 실수

❌ **실수 1: 환경 변수 누락**
- GitHub에 API 키를 커밋하지 마세요
- Vercel Environment Variables에서 관리하세요

❌ **실수 2: GitHub 저장소 설정 오류**
```bash
# 잘못된 방법
git push origin main
# → fatal: repository not found

# 올바른 방법
git remote set-url origin https://github.com/YOUR_USERNAME/10-00-02-Election-Standard-Platform.git
git push -u origin main
```

❌ **실수 3: Vercel 캐싱 문제**
- 브라우저 캐시 삭제: Ctrl+Shift+Delete
- 또는 프라이빗 탭 사용

---

## 🎯 완료 체크리스트

- [ ] GitHub 저장소 생성
- [ ] 로컬 git remote 연결
- [ ] GitHub에 코드 푸시
- [ ] Vercel 계정 생성
- [ ] GitHub 저장소 Vercel에 연결
- [ ] 환경 변수 설정
- [ ] 배포 완료
- [ ] 랜딩페이지 접근 테스트
- [ ] Supabase 연결 테스트

---

다음: `VERCEL_DEPLOYMENT_GUIDE.md` 참조

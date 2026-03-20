# 🚀 배포 완전 체크리스트

> 선거 워룸 AI 플랫폼 — 완전 배포 가이드

---

## 📋 Phase 1: Supabase 설정 (필수)

- [ ] Supabase 프로젝트 생성: https://supabase.com
- [ ] API URL 복사: `https://xxxxx.supabase.co`
- [ ] anon key 복사: `eyJhbG...`
- [ ] SQL Editor에서 마이그레이션 실행 (database/migrations/005_signup_system.sql)
- [ ] RLS 정책 설정 (database/rls_policies.sql)
- [ ] Storage 버킷 생성: `campaign-assets`
- [ ] 브라우저에서 환경 변수 설정 테스트

---

## 📋 Phase 2: GitHub 연결 (필수)

- [ ] GitHub 로그인: https://github.com
- [ ] 새 저장소 생성: `10-00-02-Election-Standard-Platform`
- [ ] 로컬 저장소에 origin 추가
- [ ] 코드 GitHub에 푸시: `git push -u origin main`
- [ ] GitHub에서 파일 확인

---

## 📋 Phase 3: Vercel 배포 (필수)

- [ ] Vercel 계정 생성: https://vercel.com
- [ ] GitHub 계정으로 로그인
- [ ] 새 프로젝트 생성: "Import Git Repository"
- [ ] 저장소 선택: `10-00-02-Election-Standard-Platform`
- [ ] 환경 변수 설정: SUPABASE_URL, SUPABASE_KEY
- [ ] 배포 실행
- [ ] 배포 완료 URL 확인

---

## ✅ Phase 4: 배포 후 검증 (필수)

- [ ] Vercel URL로 랜딩페이지 접근
- [ ] Supabase 환경 변수 설정
- [ ] 회원가입 폼 입력 후 저장 확인
- [ ] 로그인 후 프로필 표시 확인
- [ ] 관리자 설정 페이지 접근 확인

---

## 🔒 Phase 5: 보안 확인 (필수)

- [ ] HTTPS 자동 설정 확인
- [ ] 환경 변수 코드 하드코딩 없음 확인
- [ ] service_role key는 없고 anon key만 사용 확인

---

## 📊 Phase 6: 성능 최적화 (선택)

- [ ] Vercel Analytics 확인
- [ ] Lighthouse 성능 점수 확인
- [ ] 캐싱 설정 확인 (vercel.json)

---

## 🎯 배포 완료!

모든 항목을 확인했다면 프로덕션 배포 완료입니다.

참고 자료:
- SUPABASE_SETUP_GUIDE.md
- VERCEL_DEPLOYMENT_GUIDE.md  
- GITHUB_SETUP.md
- ARCHITECTURE_DESIGN.md

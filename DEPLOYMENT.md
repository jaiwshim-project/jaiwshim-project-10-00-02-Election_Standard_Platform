# 선거 워룸 - 배포 및 운영 가이드

## 1. 프로젝트 구조 및 분대 편성 (42명)

### HQ (본부, 2명)
- **소대장 (Claude Opus)**: 전략 수립, 의사결정, 통합 감독
- **연락병 (AI Chatbot)**: 실시간 문의 처리, 플랫폼 가이드

### Alpha 분대: 백엔드 데이터 레이어 (12명)
**분대장**: Claude Sonnet | **역할**: 데이터 파이프라인, RAG, API 구축
- **정규병 11명 역할분담**:
  1. Supabase DB 관리 (테이블, 스키마, 인덱싱)
  2. pgvector 벡터 DB 운영
  3. PDF 문서 처리 및 청킹 (pdf_processor.py)
  4. 임베딩 생성 및 저장 (rag_engine.py)
  5. REST API 개발 및 배포 (api/)
  6. 뉴스 API 통합 (data-pipeline)
  7. 여론조사 데이터 수집
  8. 데이터 캐싱 및 최적화
  9. 보안 및 접근 제어
  10. 모니터링 및 로깅
  11. 백업 및 재해 복구

**핵심 파일**:
```
server/
├── api/
│   ├── routes.py          # REST API 엔드포인트
│   ├── auth.py            # 인증/인가
│   └── middleware.py      # 미들웨어
├── data-pipeline/
│   ├── etl.py             # ETL 파이프라인
│   ├── news-collector.py  # 뉴스 수집
│   └── survey-sync.py     # 여론조사 동기화
database/
├── migrations/
│   ├── schema.sql         # 초기 스키마
│   └── seed.sql           # 샘플 데이터
└── backups/               # DB 백업
```

---

### Bravo 분대: 프론트엔드 UI/UX (12명)
**분대장**: Claude Sonnet | **역할**: 사용자 인터페이스, 대시보드, UX
- **정규병 11명 역할분담**:
  1. 메인 대시보드 (dashboard.html)
  2. AI 챗봇 UI (ai-chat.html)
  3. 전략 수립 페이지 (strategy.html)
  4. 경쟁 분석 UI (competitors.html)
  5. 판세 인텔리전스 (intelligence.html)
  6. 워룸 실시간 모니터 (warroom.html)
  7. 보고서 생성 UI (reports.html)
  8. 설정 및 프로필 (settings.html)
  9. 반응형 CSS 최적화 (responsive.css)
  10. 테마 관리 (theme.css, party-theme.js)
  11. 성능 최적화 및 접근성

**핵심 파일**:
```
pages/
├── dashboard.html         # 메인 대시보드
├── ai-chat.html          # AI 챗봇
├── strategy.html         # 전략 수립
├── competitors.html      # 경쟁자 분석
├── intelligence.html     # 판세 인텔리전스
├── warroom.html          # 실시간 워룸
├── reports.html          # 보고서
└── settings.html         # 설정

css/
├── theme.css             # 색상, 변수
└── responsive.css        # 반응형 디자인

js/
├── api-client.js         # API 통신
├── file-store.js         # 로컬 저장소
├── ui.js                 # UI 유틸
└── party-theme.js        # 정당 테마
```

---

### Charlie 분대: AI 엔진 & 전략 로직 (12명)
**분대장**: Claude Sonnet | **역할**: AI 엔진, 분석, 전략 추천
- **정규병 11명 역할분담**:
  1. RAG 엔진 (rag_engine.py)
  2. 판세 감지 AI (election_radar.py)
  3. 경쟁자 분석 (competitor_analyzer.py)
  4. 캠프 코파일럿 (campaign_copilot.py)
  5. 콘텐츠 생성 (content_generator.py)
  6. 후보 코칭 (candidate_coach.py)
  7. 자동화 워크플로우
  8. 프롬프트 엔지니어링 및 최적화
  9. 성과 평가 및 피드백
  10. A/B 테스트 운영
  11. Gemini API 통합 및 성능 조정

**핵심 파일**:
```
server/ai-engine/
├── rag_engine.py         # RAG 기반 Q&A
├── election_radar.py     # 판세 분석
├── competitor_analyzer.py # 경쟁 분석
├── campaign_copilot.py   # 전략 추천
├── content_generator.py  # 콘텐츠 생성
├── candidate_coach.py    # 후보 코칭
└── orchestrator.py       # AI 워크플로우
```

---

### 용병 풀 (공유 자산, 4명)
- **Codex**: 코드 생성, 버그 픽스, 리팩토링
- **Gemini**: API 통합, 임베딩, 분석
- **Grok**: 복잡한 문제 해결, 아키텍처 설계
- **Perplexity**: 최신 정보 수집, 트렌드 분석

---

## 2. 배포 환경 설정

### 개발 환경 (Local)
```bash
# 1. 저장소 클론
git clone <repo-url>
cd election-war-room

# 2. 환경 설정
cp .env.example .env
# .env 파일 수정:
# - GEMINI_API_KEY
# - SUPABASE_URL
# - SUPABASE_ANON_KEY
# - DATABASE_URL

# 3. 백엔드 설정
pip install -r requirements.txt
python server/api/routes.py

# 4. 프론트엔드 테스트
npm install
npm start
```

### 프로덕션 배포 (Vercel)
```bash
# 1. Vercel 연결
vercel link

# 2. 환경 변수 설정
vercel env add GEMINI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY

# 3. 배포
vercel deploy --prod
```

### 데이터베이스 초기화 (Supabase)
```bash
# 1. 마이그레이션 실행
supabase migration up

# 2. 샘플 데이터 로드
psql $DATABASE_URL < database/seed.sql

# 3. 벡터 확장 활성화
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector"
```

---

## 3. 핵심 워크플로우

### 판세 분석 파이프라인
```
뉴스/여론조사 수집 → 데이터 전처리 → 감정 분석 → 판세 감지 AI → 대시보드 표시
```

### AI 챗봇 작동 흐름
```
사용자 질문 → RAG 검색 → Gemini 프롬프트 → 답변 생성 → 대시보드 표시
```

### 전략 추천 로직
```
현재 판세 분석 → 경쟁자 비교 → 캠프 코파일럿 실행 → 액션 플랜 생성 → 실시간 모니터링
```

---

## 4. 모니터링 및 성능 관리

### 주요 지표 (KPI)
- **플랫폼 가용성**: 99.9% 목표
- **API 응답 시간**: 평균 < 200ms
- **데이터 수집 지연**: < 5분
- **AI 모델 정확도**: > 85% (판세 분석)

### 모니터링 도구
- **Datadog**: 인프라, 성능 모니터링
- **Sentry**: 에러 트래킹
- **CloudWatch**: 로그 분석

### 정기 점검
- 일일: API 상태, 데이터 동기화
- 주간: 성능 리포트, 데이터 품질
- 월간: 보안 감사, 비용 분석

---

## 5. 팀 커뮤니케이션 및 협업

### 일일 스탠드업 (HQ)
- **시간**: 09:00 KST
- **참석**: HQ + 각 분대장
- **주제**: 진행률, 블로커, 우선순위 조정

### 분대별 워크숍
- **Alpha**: 월요일 14:00 - 데이터 성능 최적화
- **Bravo**: 화요일 14:00 - UI/UX 개선
- **Charlie**: 수요일 14:00 - AI 모델 성능 평가

### 통합 테스트 (목요일)
- 전체 팀이 참여하여 end-to-end 테스트 수행
- 버그 리포트 및 개선사항 협의

---

## 6. 배포 체크리스트

### Pre-Launch
- [ ] 모든 API 엔드포인트 테스트
- [ ] 데이터베이스 백업
- [ ] 보안 감사 완료
- [ ] 성능 테스트 통과 (TPS 1000+)
- [ ] 모든 페이지 반응형 테스트
- [ ] 악세스 권한 검증
- [ ] 외부 API 키 설정 확인

### Launch Day
- [ ] Supabase 마이그레이션 적용
- [ ] Vercel 배포
- [ ] DNS 확인
- [ ] SSL 인증서 검증
- [ ] 스모크 테스트 (주요 기능)
- [ ] 모니터링 활성화

### Post-Launch
- [ ] 사용자 피드백 수집
- [ ] 성능 모니터링
- [ ] 에러 로그 분석
- [ ] 데이터 동기화 확인
- [ ] 보안 로그 점검

---

## 7. 문제 해결 가이드

### API 연결 실패
```bash
# 1. 환경 변수 확인
echo $DATABASE_URL

# 2. Supabase 상태 확인
curl https://api.supabase.co/health

# 3. 네트워크 연결 테스트
ping api.supabase.co
```

### 데이터 수집 지연
```bash
# 1. 데이터 파이프라인 로그 확인
tail -f logs/data-pipeline.log

# 2. 뉴스 API 상태 확인
python server/data-pipeline/news-collector.py --test

# 3. 여론조사 동기화 상태
python server/data-pipeline/survey-sync.py --status
```

### AI 모델 성능 저하
```bash
# 1. Gemini API 할당량 확인
python -c "from google import generativeai; print(generativeai.GenerativeModel('gemini-pro').count_tokens('test'))"

# 2. RAG 벡터 검색 성능 확인
python server/ai-engine/rag_engine.py --benchmark

# 3. 임베딩 모델 재학습
python server/ai-engine/rag_engine.py --retrain
```

---

## 8. 향후 확장 계획 (Phase 2)

- [ ] 실시간 소셜 미디어 모니터링 (트위터, 페이스북)
- [ ] 디ープ러닝 기반 이미지 분석 (포스터, 광고)
- [ ] 음성 분석 AI (연설, 인터뷰)
- [ ] 예측 모델 고도화 (확률론적 판세 예측)
- [ ] 모바일 앱 출시 (iOS, Android)
- [ ] 국제화 (다국어 지원)

---

**마지막 업데이트**: 2026-03-20
**담당자**: Election War Room HQ (Claude Opus + Team)

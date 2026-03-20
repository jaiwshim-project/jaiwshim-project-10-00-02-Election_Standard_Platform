# 선거 워룸 (Election War Room)

**AI 기반 정치 전략 플랫폼** — 정치 캠프의 실시간 위기 대응 및 전략 지원 솔루션

## 📋 프로젝트 개요

선거 워룸은 Gemini API, Supabase, pgvector를 활용하여 정치 캠프의 **실시간 위기 대응**, **판세 분석**, **AI 전략 추천**을 제공하는 통합 워룸 플랫폼입니다.

### 주요 기능

#### 1. **RAG 기반 AI 챗봇** (`rag_engine.py`)
- Gemini API 활용한 의도 기반 질문 분류
- PDF 문서 의미론적 청킹 및 벡터 임베딩
- pgvector를 통한 의미 유사도 검색
- 정책/판세 분석 콘텍스트 기반 답변 생성

#### 2. **판세 감지 AI** (Election Radar, `election_radar.py`)
- 실시간 여론 추이 분석 (상승/하강/변동 감지)
- 이슈별 영향도 정량화
- 위험 신호 조기 경보 시스템
- 추세 예측 (1주일, 1개월)

#### 3. **경쟁자 분석 엔진** (`competitor_analyzer.py`)
- 경쟁 상대 강점/약점 자동 파악
- 지지율 추이 비교 분석
- 정책 차별성 분석
- 대응 전략 추천

#### 4. **AI 캠프 코파일럿** (`campaign_copilot.py`)
- 현재 판세 기반 최적화된 전략 자동 생성
- 주간/월간 액션 플랜 수립
- 우선순위 기반 실행 가이던스
- 성과 예측

#### 5. **콘텐츠 자동 생성** (`content_generator.py`)
- SNS 포스트 자동 작성 (트위터, 인스타, 페이스북)
- 정책 설명 콘텐츠 자동 생성
- 일일 뉴스레터 작성
- 보도자료 및 동영상 대본 생성

#### 6. **후보 개인 코칭 AI** (`candidate_coach.py`)
- 후보자 강점/약점 진단
- 언론 대면 및 연설 훈련
- 이슈별 대응 가이드
- 일일 성과 평가 및 피드백

#### 7. **데이터 파이프라인** (`data_pipeline.py`)
- 뉴스 API 통합 (뉴스 API, 구글 뉴스 등)
- 여론조사 데이터 자동 수집
- 감정 분석 및 분류
- 벡터 임베딩 및 저장

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Bravo)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Dashboard │ AI Chat │ Competitors │ Strategy │ Reports│  │
│  │ (Vue/React)      UI Components with Responsive CSS    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ (API)
┌─────────────────────────────────────────────────────────────┐
│                 Backend API (FastAPI)                       │
│  /api/chat  /api/candidates  /api/competitors  /api/analytics
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              AI Engine Layer (Charlie)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ RAG Engine │ Election Radar │ Competitor Analyzer     │ │
│  │ Campaign Copilot │ Content Generator │ Candidate Coach│ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│       Data & Vector Database (Supabase + pgvector)         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Candidates │ Policies │ News Feed │ Chat History      │ │
│  │ Reports │ Embeddings (1536-dim) │ Analytics          │ │
│  │ Polling Data │ Competitor Info                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         External AI APIs & Data Sources                    │
│  Gemini API │ News APIs │ Poll Data │ Social Media APIs  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 폴더 구조

```
선거 워룸/
├── README.md (이 파일)
├── package.json
├── config/
│   ├── config.json
│   └── .env.example
├── css/
│   ├── theme.css (디자인 시스템)
│   └── responsive.css (모바일 최적화)
├── js/
│   ├── ui.js (UI 유틸리티)
│   └── api-client.js (API 클라이언트)
├── pages/
│   ├── index.html (대시보드)
│   ├── ai-chat.html (AI 질문 인터페이스)
│   ├── competitors.html (경쟁자 분석)
│   ├── strategy.html (전략 추천)
│   └── reports.html (리포트 관리)
├── database/
│   └── migrations/
│       └── 001_initial_schema.sql (DB 스키마)
└── server/
    ├── api/
    │   └── main.py (FastAPI 백엔드)
    ├── ai-engine/
    │   ├── rag_engine.py (RAG 엔진)
    │   ├── pdf_processor.py (PDF 처리)
    │   ├── competitor_analyzer.py (경쟁자 분석)
    │   ├── election_radar.py (판세 감지)
    │   ├── campaign_copilot.py (전략 추천)
    │   ├── content_generator.py (콘텐츠 생성)
    │   └── candidate_coach.py (후보 코칭)
    └── data-pipeline/
        └── data_pipeline.py (데이터 ETL)
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# .env 파일 설정
cp config/.env.example .env

# 필수 환경 변수
SUPABASE_URL=...
SUPABASE_KEY=...
GEMINI_API_KEY=...
NEWS_API_KEY=...
```

### 2. 데이터베이스 초기화

```bash
psql -U postgres -d postgres < database/migrations/001_initial_schema.sql
```

### 3. 백엔드 실행

```bash
cd server/api
pip install -r requirements.txt
python main.py
# FastAPI 서버 실행: http://localhost:8000
```

### 4. 프론트엔드 실행

```bash
# 간단한 로컬 서버 (Python)
python -m http.server 3000
# 또는 npm/yarn으로 개발 서버 실행
```

## 🔑 핵심 API 엔드포인트

### Chat API
```javascript
POST /api/chat
{
  "question": "현재 지지율은?",
  "candidate_id": "candidate-1"
}
Response: {
  "answer": "...",
  "intent": "polling",
  "sources": [...],
  "confidence": 0.92
}
```

### Analytics API
```javascript
GET /api/analytics?candidate_id=...&metric_type=approval
Response: [{
  "date": "2026-03-18",
  "approval_rate": 45.2,
  "trend": "상승",
  "change": 2.1
}]
```

### Competitors API
```javascript
GET /api/competitors?candidate_id=...
Response: [{
  "competitor_id": "...",
  "name": "조은희",
  "approval_rate": 38.0,
  "strengths": [...],
  "weaknesses": [...],
  "risk_level": "high"
}]
```

## 🤖 AI 엔진 주요 클래스

### RAGEngine
```python
engine = RAGEngine(gemini_client, db_client)
result = await engine.query(
    question="청년 정책 설명해주세요",
    context_docs=None  # 자동 검색
)
```

### ElectionRadar
```python
radar = ElectionRadar(db_client, gemini_client)
trend = await radar.detect_trend(candidate_id, "1month")
warning = await radar.early_warning_check(candidate_id)
```

### CampaignCopilot
```python
copilot = CampaignCopilot(db_client, gemini_client, radar, competitor)
plan = await copilot.generate_strategy_plan(candidate_id, "1month")
brief = await copilot.get_daily_briefing(candidate_id)
```

## 📊 데이터 스키마 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `candidates` | 후보자 정보 |
| `policies` | 정책/공약 (벡터 임베딩) |
| `competitors` | 경쟁 상대 분석 |
| `news_feed` | 뉴스 피드 (감정 분석, 임베딩) |
| `chat_sessions` | 챗 세션 (대화 히스토리) |
| `analytics` | 지지율/선거 지표 |
| `reports` | 업로드된 분석 리포트 (벡터) |

## 🔒 보안

- **API 키 관리**: 환경 변수에서만 로드
- **인증**: JWT 토큰 기반 (향후 구현)
- **데이터 암호화**: pgcrypto 사용 (비밀번호)
- **CORS**: 허가된 도메인만 접근 가능

## 📈 성능 최적화

- **벡터 검색**: IVFFlat 인덱스 사용 (빠른 유사도 검색)
- **캐싱**: Redis 캐싱 (자주 조회되는 데이터)
- **비동기 처리**: FastAPI async/await + asyncio
- **배치 처리**: 대량 데이터 임베딩 병렬 처리

## 🧪 테스트

```bash
# API 테스트
pytest server/tests/

# 프론트엔드 테스트
npm test

# 통합 테스트
python -m pytest server/tests/integration/ -v
```

## 🌐 배포

### Vercel (프론트엔드)
```bash
vercel deploy
```

### Supabase Functions (API)
```bash
supabase functions deploy
```

## 📚 참고 자료

- [Gemini API 문서](https://ai.google.dev)
- [Supabase 가이드](https://supabase.com/docs)
- [pgvector 사용법](https://github.com/pgvector/pgvector)
- [FastAPI 문서](https://fastapi.tiangolo.com)

## 👨‍💼 팀 구성 (42명 소대)

### HQ (본부)
- **소대장**: 전략적 의사결정 및 오케스트레이션
- **연락병**: 사용자 ↔ 소대장 간 통신

### 3개 분대 (Alpha, Bravo, Charlie)
- **Alpha**: 백엔드 데이터 레이어 (RAG + DB + API 구축)
- **Bravo**: 프론트엔드 UI/UX 구현 (대시보드 + 전략 + 워룸 인터페이스)
- **Charlie**: AI 엔진 & 전략 로직 (경쟁자 분석, 판세 감지, 캠프 코파일럿, 콘텐츠 생성, 후보 코칭)

### 각 분대별 11명 정규병
설계, 개발, 테스트, 리뷰, 문서화 등 전문 역할 수행

### 용병 풀 (4명, 공유 자산)
Codex, Gemini, Grok, Perplexity — 특화 작업 투입

## 📞 연락처

**프로젝트 소대장**: 선거 워룸 개발팀
**이메일**: warroom@electionteam.kr

## 📄 라이선스

MIT License — 자유롭게 사용, 수정, 배포 가능

---

**마지막 업데이트**: 2026-03-19
**버전**: 1.0.0 (Alpha)

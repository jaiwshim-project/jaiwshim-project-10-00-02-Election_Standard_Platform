# 선거 워룸 (Election War Room) - 시스템 아키텍처

## 전체 시스템 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                     프론트엔드 (Bravo 분대)                        │
├─────────────────────────────────────────────────────────────────┤
│  dashboard.html    │  ai-chat.html     │  strategy.html       │
│  intelligence.html │  competitors.html │  warroom.html        │
│  reports.html      │  settings.html                           │
├─────────────────────────────────────────────────────────────────┤
│        js/ 및 css/ (UI 로직, 스타일, 반응형 디자인)                 │
└────────────────────────┬──────────────────────────────────────┘
                         │ REST API + WebSocket
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               백엔드 (Alpha 분대 + Charlie 분대)                   │
├──────────────────────────────────┬──────────────────────────────┤
│   API Layer (Alpha)              │  AI Engine (Charlie)          │
│  ├─ routes.py                    │  ├─ rag_engine.py            │
│  ├─ auth.py                      │  ├─ election_radar.py        │
│  ├─ middleware.py                │  ├─ competitor_analyzer.py   │
│  └─ api.json                     │  ├─ campaign_copilot.py      │
│                                  │  ├─ content_generator.py     │
│   Data Pipeline (Alpha)          │  ├─ candidate_coach.py       │
│  ├─ etl.py                       │  └─ orchestrator.py          │
│  ├─ news-collector.py            │                              │
│  └─ survey-sync.py               │  Gemini API Integration      │
└──────────────────────┬───────────┴──────────────────────────────┘
                       │ SQL + Vector Operations
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                  데이터베이스 (Alpha 분대)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Supabase (PostgreSQL)                                   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ - policies (정책 데이터)                                  │   │
│  │ - news (뉴스 피드)                                        │   │
│  │ - surveys (여론조사)                                      │   │
│  │ - candidates (후보자)                                    │   │
│  │ - competitors (경쟁자)                                   │   │
│  │ - documents (PDF 문서)                                   │   │
│  │ - embeddings (벡터 임베딩) - pgvector                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ↓                  ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ News APIs    │  │ Gemini API   │  │ External     │
│ (Naver,      │  │ (Embeddings, │  │ PDFs         │
│ Google,      │  │ Text Gen)    │  │ (Reports)    │
│ NewsAPI)     │  └──────────────┘  └──────────────┘
└──────────────┘
```

---

## 1. 프론트엔드 아키텍처 (Bravo 분대)

### 1.1 페이지 구조 및 역할

```
pages/
├── index.html (entry point)
├── dashboard.html
│   ├─ 실시간 판세 지도
│   ├─ 주요 지표 위젯
│   ├─ 최근 뉴스 피드
│   └─ AI 권장사항
├── ai-chat.html
│   ├─ RAG 기반 챗봇
│   ├─ 정책 Q&A
│   ├─ 판세 분석 문의
│   └─ 회담 기록
├── strategy.html
│   ├─ 장기 전략 수립
│   ├─ 월간 액션 플랜
│   ├─ 위험도 분석
│   └─ 성과 예측
├── competitors.html
│   ├─ 경쟁자 프로필
│   ├─ 강점/약점 비교
│   ├─ 지지율 추이
│   └─ 대응 전략
├── intelligence.html
│   ├─ 실시간 판세 트렌드
│   ├─ 이슈별 영향도
│   ├─ 위험 신호 경보
│   └─ 예측 모델
├── warroom.html
│   ├─ 실시간 모니터링
│   ├─ 긴급 대응 체계
│   ├─ 위기 상황판
│   └─ 팀 협업 도구
├── reports.html
│   ├─ 일일 보고서
│   ├─ 주간 분석
│   ├─ 월간 성과 평가
│   └─ PDF 내보내기
└── settings.html
    ├─ 사용자 프로필
    ├─ 권한 관리
    ├─ API 키 설정
    └─ 알림 설정
```

### 1.2 UI 컴포넌트 계층

```
CSS 변수 (theme.css)
  ↓
기본 컴포넌트 (cards, buttons, inputs)
  ↓
복합 컴포넌트 (charts, tables, modals)
  ↓
페이지별 컴포넌트 (dashboard, strategy, etc.)
  ↓
반응형 레이아웃 (responsive.css)
```

### 1.3 상태 관리 및 로컬 저장소

```javascript
// file-store.js
├─ userData (사용자 설정)
├─ chartData (차트 캐시)
├─ chatHistory (대화 기록)
├─ preferences (개인 설정)
└─ notifications (알림)
```

---

## 2. 백엔드 API 아키텍처 (Alpha 분대)

### 2.1 REST API 엔드포인트

#### 인증 (`/auth`)
```
POST   /auth/register        # 사용자 등록
POST   /auth/login           # 로그인
POST   /auth/logout          # 로그아웃
POST   /auth/refresh-token   # 토큰 갱신
GET    /auth/verify          # 토큰 검증
```

#### 판세 분석 (`/analytics`)
```
GET    /analytics/trends           # 판세 추이
GET    /analytics/issues           # 주요 이슈
GET    /analytics/sentiment        # 감정 분석
GET    /analytics/predictions      # 판세 예측
GET    /analytics/demographics     # 인구통계
```

#### 경쟁자 분석 (`/competitors`)
```
GET    /competitors                # 경쟁자 목록
GET    /competitors/:id            # 경쟁자 프로필
GET    /competitors/:id/compare    # 비교 분석
GET    /competitors/:id/weakness   # 약점 분석
GET    /competitors/:id/strategy   # 대응 전략
```

#### 전략 관리 (`/strategies`)
```
GET    /strategies                 # 전략 목록
POST   /strategies                 # 전략 생성
GET    /strategies/:id             # 전략 상세
PUT    /strategies/:id             # 전략 수정
DELETE /strategies/:id             # 전략 삭제
GET    /strategies/:id/plan        # 액션 플랜
```

#### 뉴스/데이터 (`/data`)
```
GET    /data/news                  # 최근 뉴스
GET    /data/surveys               # 여론조사
GET    /data/documents             # 정책 문서
GET    /data/policies              # 정책 목록
```

#### AI 챗봇 (`/chat`)
```
POST   /chat/message               # 메시지 전송
GET    /chat/history               # 대화 기록
POST   /chat/clear                 # 기록 삭제
```

### 2.2 데이터베이스 스키마

#### 주요 테이블

```sql
-- 사용자 및 인증
users (id, email, name, role, created_at)
  ├─ PK: id
  └─ FK: role_id

roles (id, name, permissions)
  └─ PK: id

-- 후보자 및 캠프
candidates (id, name, party, bio, created_at)
  ├─ PK: id
  └─ FK: user_id

campaigns (id, candidate_id, start_date, end_date)
  ├─ PK: id
  └─ FK: candidate_id

-- 판세 분석
news (id, title, content, source, published_at, sentiment)
  ├─ PK: id
  └─ INDEX: published_at, source

surveys (id, poll_name, data, timestamp)
  ├─ PK: id
  └─ INDEX: timestamp

trends (id, metric, value, date)
  ├─ PK: id
  └─ INDEX: date, metric

-- 경쟁자 분석
competitors (id, name, party, website, created_at)
  ├─ PK: id
  └─ INDEX: name

competitor_analysis (id, competitor_id, analyzed_at, report)
  ├─ PK: id
  └─ FK: competitor_id

-- 전략 및 액션 플랜
strategies (id, campaign_id, name, description, created_at)
  ├─ PK: id
  └─ FK: campaign_id

action_plans (id, strategy_id, task, priority, status)
  ├─ PK: id
  └─ FK: strategy_id, priority_id

-- 정책 및 문서
policies (id, title, content, category, created_at)
  ├─ PK: id
  └─ INDEX: category

documents (id, filename, file_type, upload_date, user_id)
  ├─ PK: id
  └─ FK: user_id

-- RAG 및 벡터 검색
documents_vectors (id, document_id, content_chunk, embedding)
  ├─ PK: id
  ├─ FK: document_id
  └─ INDEX: embedding (pgvector)
```

### 2.3 데이터 파이프라인

```
뉴스 수집 (news-collector.py)
  ├─ Naver 뉴스 API
  ├─ Google News API
  └─ NewsAPI
       ↓
    감정 분석 (sentiment analysis)
       ↓
    데이터 정규화
       ↓
    Supabase 저장
       ↓
    Gemini 처리 (선택적)
       ↓
    대시보드 표시
```

---

## 3. AI 엔진 아키텍처 (Charlie 분대)

### 3.1 AI 모듈 구성

```
┌─ RAG Engine (rag_engine.py)
│  ├─ PDF 문서 처리
│  ├─ 의미론적 청킹
│  ├─ 임베딩 생성 (Gemini)
│  └─ 벡터 검색 (pgvector)
│
├─ Election Radar (election_radar.py)
│  ├─ 뉴스 분석
│  ├─ 여론조사 처리
│  ├─ 감정 분석
│  ├─ 추세 감지
│  └─ 예측 모델
│
├─ Competitor Analyzer (competitor_analyzer.py)
│  ├─ 뉴스 수집
│  ├─ 정책 비교
│  ├─ 강점/약점 분석
│  └─ 대응 전략 추천
│
├─ Campaign Copilot (campaign_copilot.py)
│  ├─ 현재 판세 분석
│  ├─ 최적화 전략 생성
│  ├─ 액션 플랜 수립
│  └─ 성과 예측
│
├─ Content Generator (content_generator.py)
│  ├─ SNS 포스트 생성
│  ├─ 정책 설명글 작성
│  ├─ 뉴스레터 작성
│  └─ 보도자료 생성
│
├─ Candidate Coach (candidate_coach.py)
│  ├─ 강점/약점 진단
│  ├─ 언론 대면 훈련
│  ├─ 이슈 대응 가이드
│  └─ 성과 평가
│
└─ Orchestrator (orchestrator.py)
   ├─ AI 워크플로우 조정
   ├─ 모듈 간 데이터 흐름
   ├─ 우선순위 관리
   └─ 에러 핸들링
```

### 3.2 Gemini API 통합

```
프롬프트 → Gemini Model → 응답 생성
  ↓            ↓             ↓
특정 도메인  few-shot     구조화된
프롬프트    예제 포함      JSON/Text
```

#### 주요 프롬프트 템플릿

```python
# RAG 기반 정책 Q&A
def rag_prompt(question, context):
    return f"""
    다음 정책 문서를 바탕으로 질문에 답하세요.

    문서:
    {context}

    질문: {question}

    답변:
    """

# 판세 분석
def radar_prompt(news, surveys):
    return f"""
    최근 뉴스와 여론조사 데이터를 분석하여 판세 변화를 파악하세요.

    뉴스: {news}
    여론조사: {surveys}

    분석 결과 (JSON):
    {{
        "trend": "상승|하강|변동",
        "confidence": 0.0-1.0,
        "key_issues": [],
        "risk_factors": [],
        "opportunities": [],
        "forecast_7days": "",
        "forecast_30days": ""
    }}
    """

# 전략 추천
def copilot_prompt(current_state, target_state):
    return f"""
    현재 상황에서 목표 상태에 도달하기 위한 최적화된 전략을 수립하세요.

    현재 상황: {current_state}
    목표 상태: {target_state}

    전략 및 액션 플랜:
    """
```

### 3.3 AI 모델 성능 관리

```
프롬프트 → Gemini → 응답 → 평가 → 피드백 → 프롬프트 개선
(반복)
```

#### 평가 메트릭
- 정확도 (Accuracy): 모델 응답이 실제 데이터와 일치하는 정도
- 관련성 (Relevance): 응답이 질문과 관련있는 정도
- 응답 시간 (Latency): API 호출 응답 시간
- 비용 효율 (Cost): API 사용 비용 대비 성능

---

## 4. 실시간 통신 아키텍처

### 4.1 WebSocket 기반 실시간 업데이트

```
클라이언트 ↔ WebSocket ↔ 서버
   (js)      (ws://)   (Python)

- 판세 업데이트 (1분마다)
- 뉴스 피드 (실시간)
- 팀 협업 알림 (즉시)
- AI 분석 결과 (완료 시)
```

### 4.2 이벤트 기반 아키텍처

```
Event → Queue → Worker → Database → Broadcast

예시:
- news_updated → analyze → sentiment → store → update_ui
- survey_received → aggregate → predict → store → alert
```

---

## 5. 보안 아키텍처

### 5.1 인증 및 인가

```
사용자 로그인
  ↓
JWT 토큰 발급
  ↓
각 요청에 포함
  ↓
서버에서 검증
  ↓
권한 확인 (Role-Based Access Control)
  ↓
리소스 접근 허가/거부
```

### 5.2 데이터 보안

- **암호화**: TLS/SSL (전송), AES-256 (저장)
- **접근 제어**: Row-level security (RLS) 활성화
- **감사 로그**: 모든 민감한 작업 기록
- **백업**: 일일 자동 백업

---

## 6. 확장성 및 성능

### 6.1 수평 확장 (Horizontal Scaling)

```
로드 밸런서
  ├─ API 인스턴스 1
  ├─ API 인스턴스 2
  └─ API 인스턴스 N
     ↓
  공유 데이터베이스 (Supabase)
  공유 캐시 (Redis)
```

### 6.2 캐싱 전략

```
계층 1: 브라우저 캐시
  ├─ localStorage (설정, 조회)
  └─ sessionStorage (임시 데이터)

계층 2: CDN 캐시
  └─ 정적 자산 (HTML, CSS, JS)

계층 3: 서버 캐시 (Redis)
  └─ API 응답, 쿼리 결과

계층 4: 데이터베이스
  └─ 원본 데이터
```

### 6.3 성능 최적화

- **이미지 최적화**: WebP, 동적 크기 조정
- **번들 분할**: 페이지별 JavaScript 분할 로딩
- **지연 로딩**: 필요한 순간에만 리소스 로드
- **데이터베이스 인덱싱**: 자주 조회되는 컬럼

---

## 7. 모니터링 및 관찰성

### 7.1 로그 수집

```
애플리케이션 로그
  ↓
로그 수집기 (Datadog, CloudWatch)
  ↓
분석 및 알림
  ↓
대시보드 표시
```

### 7.2 메트릭 수집

```
- 요청/응답 시간
- 에러율
- 데이터베이스 쿼리 성능
- AI API 호출 비용
- 사용자 활동
```

### 7.3 분산 추적 (Distributed Tracing)

```
클라이언트 요청 → 서버 처리 → 데이터베이스 쿼리 → API 호출
      (trace ID로 추적)
```

---

## 8. 배포 파이프라인

```
Git Push
  ↓
GitHub Actions (CI)
  ├─ 코드 테스트
  ├─ 보안 스캔
  └─ 빌드
       ↓
   Staging 환경 배포
       ↓
   통합 테스트
       ↓
   수동 승인
       ↓
   Production 배포 (Vercel)
       ↓
   Smoke 테스트
```

---

## 9. 마이크로서비스 아키텍처 (Phase 2)

현재는 모놀리식 구조이지만, 향후 마이크로서비스로 전환 가능:

```
API Gateway
  ├─ Auth Service
  ├─ Analytics Service
  ├─ Content Service
  ├─ Strategy Service
  └─ AI Service
```

---

**마지막 업데이트**: 2026-03-20
**작성**: Election War Room Architecture Team

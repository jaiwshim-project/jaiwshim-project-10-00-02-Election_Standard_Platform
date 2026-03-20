"""
데이터 파이프라인 — 뉴스/여론 데이터 자동 수집 및 처리

주기능:
- 뉴스 API 통합 (뉴스 API, 구글 뉴스 등)
- 여론조사 데이터 수집
- 소셜 미디어 감정 분석
- 벡터 임베딩 및 저장
- 실시간 데이터 업데이트
"""

from typing import Dict, List
from datetime import datetime, timedelta
import asyncio


class DataPipeline:
    """데이터 파이프라인 엔진"""

    def __init__(self, db_client=None, gemini_client=None, external_apis=None):
        self.db = db_client
        self.gemini = gemini_client
        self.apis = external_apis or {}

    async def ingest_news(self, keywords: List[str], limit: int = 50) -> Dict:
        """
        뉴스 데이터 수집 및 처리

        Args:
            keywords: 검색 키워드 (예: ["경제", "선거", "서울시장"])
            limit: 최대 수집 건수

        Returns:
            {
                "total_ingested": int,
                "processed": int,
                "stored": int,
                "failed": List[Dict],
                "timestamp": str
            }
        """
        all_articles = []

        # 1. 뉴스 API에서 데이터 수집
        for keyword in keywords:
            articles = await self._fetch_news_from_api(keyword, limit=limit // len(keywords))
            all_articles.extend(articles)

        # 2. 중복 제거
        unique_articles = self._deduplicate_articles(all_articles)

        # 3. 감정 분석
        processed_articles = []
        for article in unique_articles:
            processed = await self._process_news_article(article)
            processed_articles.append(processed)

        # 4. 벡터 임베딩
        embedded_articles = []
        for article in processed_articles:
            embedded = await self._embed_article(article)
            embedded_articles.append(embedded)

        # 5. DB에 저장
        stored_count = 0
        failed = []
        for article in embedded_articles:
            try:
                await self.db.insert_news_item(article)
                stored_count += 1
            except Exception as e:
                failed.append({"article": article.get("title"), "error": str(e)})

        return {
            "total_ingested": len(all_articles),
            "deduplicated": len(unique_articles),
            "processed": len(processed_articles),
            "embedded": len(embedded_articles),
            "stored": stored_count,
            "failed": failed,
            "timestamp": datetime.now().isoformat(),
        }

    async def ingest_polls(self, sources: List[str] = None) -> Dict:
        """
        여론조사 데이터 수집 및 저장

        Args:
            sources: 조사 기관 (예: ["갤럽", "리얼미터", "한국리서치"])

        Returns:
            {
                "polls_collected": int,
                "candidates_updated": int,
                "timestamp": str
            }
        """
        if not sources:
            sources = ["갤럽", "리얼미터", "한국리서치"]

        all_polls = []

        # 1. 각 조사 기관에서 데이터 수집
        for source in sources:
            polls = await self._fetch_polls_from_source(source)
            all_polls.extend(polls)

        # 2. 데이터 정규화 및 검증
        validated_polls = self._validate_poll_data(all_polls)

        # 3. DB 저장
        updated_candidates = set()
        for poll in validated_polls:
            await self.db.insert_or_update_poll(poll)
            updated_candidates.update(poll.get("candidates", []))

        return {
            "polls_collected": len(all_polls),
            "polls_valid": len(validated_polls),
            "candidates_updated": len(updated_candidates),
            "timestamp": datetime.now().isoformat(),
        }

    async def analyze_sentiment(self, text_items: List[Dict]) -> List[Dict]:
        """
        텍스트 감정 분석

        Args:
            text_items: [{"text": str, "source": str}, ...]

        Returns:
            텍스트별 감정 점수 (-100 ~ 100)
        """
        analyzed = []

        for item in text_items:
            sentiment_prompt = f"""
다음 텍스트의 감정을 분석하세요.
(-100: 매우 부정, 0: 중립, 100: 매우 긍정)

텍스트: {item['text']}

JSON 형식으로 {{"sentiment": number, "reason": string}}을 반환하세요.
"""

            response = await self.gemini.generate_content(sentiment_prompt)
            sentiment = self._parse_sentiment_response(response.text)

            analyzed.append({
                **item,
                "sentiment_score": sentiment.get("score", 0),
                "sentiment_reason": sentiment.get("reason", ""),
                "analyzed_at": datetime.now().isoformat(),
            })

        return analyzed

    async def generate_daily_report(self, candidate_id: str) -> Dict:
        """
        일일 데이터 리포트 생성

        Returns:
            {
                "date": str,
                "news_count": int,
                "sentiment_average": float,
                "trending_topics": List[str],
                "key_insights": List[str],
                "data_quality": str
            }
        """
        today = datetime.now().date()
        news_items = await self.db.get_news_by_date(candidate_id, today)
        polls = await self.db.get_polls_by_date(candidate_id, today)

        # 감정 평균
        sentiment_scores = [item.get("sentiment_score", 0) for item in news_items]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        # 트렌드 토픽
        trending = self._extract_trending_topics(news_items)

        # 핵심 인사이트
        insights = await self._generate_insights(news_items, polls)

        return {
            "candidate_id": candidate_id,
            "date": today.isoformat(),
            "metrics": {
                "news_items": len(news_items),
                "sentiment_average": round(avg_sentiment, 2),
                "positive_items": len([i for i in news_items if i.get("sentiment_score", 0) > 30]),
                "negative_items": len([i for i in news_items if i.get("sentiment_score", 0) < -30]),
            },
            "trending_topics": trending[:5],
            "key_insights": insights,
            "data_quality": "높음" if len(news_items) > 10 else "중간",
            "generated_at": datetime.now().isoformat(),
        }

    # ==================== 내부 헬퍼 메서드 ====================

    async def _fetch_news_from_api(self, keyword: str, limit: int) -> List[Dict]:
        """뉴스 API에서 데이터 조회"""
        # 실제 환경에서는 NewsAPI, Google News API 등 사용
        return [
            {
                "title": f"{keyword} 관련 뉴스 {i}",
                "source": "뉴스 기관",
                "url": f"https://example.com/news/{i}",
                "published_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "content": f"{keyword}에 관한 기사 본문...",
            }
            for i in range(min(limit, 10))
        ]

    async def _fetch_polls_from_source(self, source: str) -> List[Dict]:
        """여론조사 데이터 수집"""
        return [
            {
                "source": source,
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "candidates": [
                    {"name": "오세훈", "approval": 45.2},
                    {"name": "조은희", "approval": 38.0},
                ],
                "sample_size": 1000,
                "margin_of_error": 3.1,
            }
        ]

    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """중복 기사 제거"""
        seen_titles = set()
        unique = []

        for article in articles:
            title = article.get("title", "")
            if title not in seen_titles:
                seen_titles.add(title)
                unique.append(article)

        return unique

    async def _process_news_article(self, article: Dict) -> Dict:
        """뉴스 기사 처리 및 메타데이터 추가"""
        return {
            **article,
            "processed_at": datetime.now().isoformat(),
            "language": "ko",
            "category": await self._classify_news_category(article.get("content", "")),
        }

    async def _classify_news_category(self, content: str) -> str:
        """뉴스 카테고리 분류"""
        categories = {
            "경제": ["경제", "금리", "주가", "실업"],
            "정책": ["정책", "공약", "법안", "규제"],
            "사회": ["사회", "복지", "환경", "교육"],
        }

        for category, keywords in categories.items():
            if any(kw in content for kw in keywords):
                return category

        return "기타"

    async def _embed_article(self, article: Dict) -> Dict:
        """기사 벡터 임베딩"""
        text_to_embed = f"{article.get('title', '')} {article.get('content', '')[:500]}"
        embedding = await self.gemini.embed_content(text_to_embed)

        return {
            **article,
            "embedding": embedding,
            "embedding_model": "text-embedding-004",
        }

    def _validate_poll_data(self, polls: List[Dict]) -> List[Dict]:
        """여론조사 데이터 검증"""
        validated = []

        for poll in polls:
            if self._is_valid_poll(poll):
                validated.append(poll)

        return validated

    def _is_valid_poll(self, poll: Dict) -> bool:
        """단일 여론조사 유효성 검증"""
        required_fields = ["source", "date", "candidates"]
        return all(field in poll for field in required_fields)

    def _parse_sentiment_response(self, response: str) -> Dict:
        """감정 분석 응답 파싱"""
        # 실제 환경에서는 JSON 파싱
        return {
            "score": 0,
            "reason": response[:100],
        }

    def _extract_trending_topics(self, news_items: List[Dict]) -> List[str]:
        """트렌드 토픽 추출"""
        topics = {}

        for item in news_items:
            category = item.get("category", "기타")
            topics[category] = topics.get(category, 0) + 1

        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return [topic[0] for topic in sorted_topics]

    async def _generate_insights(
        self, news_items: List[Dict], polls: List[Dict]
    ) -> List[str]:
        """핵심 인사이트 생성"""
        insights = []

        if not news_items:
            return ["수집된 뉴스가 없습니다."]

        positive_count = len([i for i in news_items if i.get("sentiment_score", 0) > 30])
        negative_count = len([i for i in news_items if i.get("sentiment_score", 0) < -30])

        if negative_count > positive_count:
            insights.append(f"⚠️ 부정 기사 {negative_count}건 > 긍정 기사 {positive_count}건")

        if polls:
            insights.append("📊 최신 여론조사 데이터 업데이트됨")

        insights.append(f"📰 총 {len(news_items)}건의 뉴스 수집")

        return insights

    async def schedule_daily_pipeline(self) -> None:
        """일일 파이프라인 자동 실행 스케줄"""
        while True:
            # 매일 자정에 실행
            await asyncio.sleep(86400)  # 24시간

            # 뉴스 수집
            await self.ingest_news(
                keywords=["정치", "서울시장", "선거", "경제"],
                limit=100
            )

            # 여론조사 수집
            await self.ingest_polls()

            # 일일 리포트 생성
            # await self.generate_daily_report(candidate_id)

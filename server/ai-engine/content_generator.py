"""
콘텐츠 자동 생성 엔진 — 정책 기반 마케팅 콘텐츠 자동 생성

주기능:
- SNS 포스트 자동 생성 (인스타, 페이스북, 트위터)
- 정책 설명 콘텐츠 생성
- 일일 뉴스레터 자동 작성
- 캠프 이슈 대응 보도자료 생성
- 동영상 대본 자동 생성
"""

from typing import Dict, List
from datetime import datetime
from enum import Enum


class ContentType(Enum):
    TWITTER = "140자 트윗"
    INSTAGRAM = "인스타그램 피드"
    FACEBOOK = "페이스북 포스트"
    NEWSLETTER = "일일 뉴스레터"
    PRESS_RELEASE = "보도자료"
    VIDEO_SCRIPT = "동영상 대본"
    BLOG_POST = "블로그 포스트"


class ContentGenerator:
    """콘텐츠 자동 생성 엔진"""

    def __init__(self, gemini_client=None, db_client=None):
        self.gemini = gemini_client
        self.db = db_client

    async def generate_social_content(
        self, candidate_id: str, content_type: ContentType, topic: str
    ) -> Dict:
        """
        SNS 콘텐츠 생성

        Args:
            candidate_id: 후보 ID
            content_type: ContentType (TWITTER, INSTAGRAM, FACEBOOK)
            topic: 주제 (예: "경제 정책", "청년 고용")

        Returns:
            {
                "content_type": str,
                "content": str,
                "hashtags": List[str],
                "suggested_media": str,
                "posting_time": str,
                "expected_engagement": Dict
            }
        """
        candidate = await self.db.get_candidate(candidate_id)
        policy = await self.db.search_policies(candidate_id, topic)

        prompt = f"""
당신은 정치 캠프의 마케팅 전문가입니다.

후보: {candidate['name']} ({candidate['party']})
주제: {topic}
관련 정책: {policy[0]['description'] if policy else 'N/A'}

{content_type.value}용 콘텐츠를 생성하세요.
- 감정적 호소와 정책 내용의 균형
- 해시태그 포함
- 타겟 오디언스: 유권자 전체
- 톤: 친근하지만 진지한 톤
"""

        response = await self.gemini.generate_content(prompt)
        content = response.text

        return {
            "candidate_id": candidate_id,
            "content_type": content_type.value,
            "content": content,
            "hashtags": self._extract_hashtags(content),
            "suggested_media": await self._suggest_media(topic),
            "posting_time": self._suggest_optimal_posting_time(content_type),
            "expected_engagement": self._estimate_engagement(content, content_type),
            "created_at": datetime.now().isoformat(),
        }

    async def generate_daily_newsletter(self, candidate_id: str) -> Dict:
        """
        일일 뉴스레터 자동 작성

        Returns:
            {
                "date": str,
                "headline": str,
                "sections": [
                    {"title": str, "content": str},
                    ...
                ],
                "call_to_action": str,
                "preview": str
            }
        """
        candidate = await self.db.get_candidate(candidate_id)
        today_news = await self.db.get_news_feed(candidate_id, limit=5)
        recent_polls = await self.db.get_analytics(candidate_id, time_period="1day")

        sections = []

        # 섹션 1: 오늘의 핵심
        sections.append(
            {
                "title": "📰 오늘의 핵심",
                "content": self._summarize_news(today_news[:2]),
            }
        )

        # 섹션 2: 지지율 현황
        sections.append(
            {
                "title": "📊 지지율 현황",
                "content": f"현재 지지율: {recent_polls[0]['approval_rate']}% (전일 대비 {recent_polls[0]['change']}%)",
            }
        )

        # 섹션 3: 주요 정책
        key_policies = await self.db.get_policies(candidate_id, limit=3)
        sections.append(
            {
                "title": "💡 주요 정책",
                "content": "\n".join(
                    [f"- {p['title']}: {p['description'][:50]}..." for p in key_policies]
                ),
            }
        )

        return {
            "candidate_id": candidate_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "headline": f"{candidate['name']} 캠프 - {datetime.now().strftime('%Y년 %m월 %d일')} 뉴스레터",
            "sections": sections,
            "call_to_action": "더 자세한 정보는 우리 웹사이트를 방문하세요.",
            "preview": f"{sections[0]['content'][:100]}...",
        }

    async def generate_press_release(
        self, candidate_id: str, issue: str, action: str
    ) -> Dict:
        """
        보도자료 자동 생성

        Args:
            issue: 이슈 (예: "경제 정책 발표")
            action: 조치 (예: "경제 정책 패키지 발표")

        Returns:
            {
                "title": str,
                "subtitle": str,
                "body": str,
                "quotes": List[str],
                "contact": str
            }
        """
        candidate = await self.db.get_candidate(candidate_id)

        prompt = f"""
당신은 정치 전문 보도자료 작성자입니다.

후보: {candidate['name']} ({candidate['party']})
이슈: {issue}
조치: {action}

전문적이고 신뢰성 있는 보도자료를 작성하세요.
- 제목, 부제, 본문, 인용문 포함
- 객관적 톤
- 500자 이상 1000자 이하
"""

        response = await self.gemini.generate_content(prompt)

        return {
            "candidate_id": candidate_id,
            "issue": issue,
            "action": action,
            "content": response.text,
            "created_at": datetime.now().isoformat(),
            "status": "draft",
        }

    async def generate_video_script(
        self, candidate_id: str, video_type: str, duration_seconds: int = 60
    ) -> Dict:
        """
        동영상 대본 생성

        Args:
            video_type: "정책 설명", "인사말", "이슈 대응" 등
            duration_seconds: 동영상 길이 (기본 60초)

        Returns:
            {
                "title": str,
                "script": str,
                "scenes": List[{"time": str, "action": str}],
                "duration": int,
                "visual_notes": List[str]
            }
        """
        candidate = await self.db.get_candidate(candidate_id)
        policies = await self.db.get_policies(candidate_id, limit=3)

        # 초당 약 3-4자의 대사 속도
        target_words = (duration_seconds // 60) * 150

        prompt = f"""
당신은 정치 캠프의 동영상 감독입니다.

후보: {candidate['name']} ({candidate['party']})
영상 타입: {video_type}
길이: {duration_seconds}초 (약 {target_words}자)

다음을 포함한 동영상 대본을 작성하세요:
1. 오프닝 (10초)
2. 메인 메시지 (40초)
3. 클로징 (10초)

시각적 요소와 함께 대사를 작성하세요.
"""

        response = await self.gemini.generate_content(prompt)

        return {
            "candidate_id": candidate_id,
            "video_type": video_type,
            "duration_seconds": duration_seconds,
            "script": response.text,
            "scenes": self._parse_video_scenes(response.text),
            "visual_notes": [
                "배경: 후보자의 사무실 또는 야외 배경",
                "조명: 자연광 선호",
                "음악: 밝고 긍정적인 배경음",
            ],
            "created_at": datetime.now().isoformat(),
        }

    async def generate_policy_explainer(
        self, candidate_id: str, policy_id: str
    ) -> Dict:
        """정책 설명 콘텐츠 생성 (블로그 + SNS 요약)"""
        policy = await self.db.get_policy(policy_id)
        candidate = await self.db.get_candidate(candidate_id)

        prompt = f"""
정책을 일반 유권자가 이해하기 쉬운 방식으로 설명하세요.

정책: {policy['title']}
설명: {policy['description']}

다음을 포함하세요:
1. 이 정책이 왜 필요한가? (문제 정의)
2. 어떻게 해결할 것인가? (구체적 방안)
3. 누가 혜택받는가? (대상층)
4. 재원은? (예산)
5. 효과는? (기대효과)
"""

        blog_response = await self.gemini.generate_content(prompt)

        # SNS용 요약본
        sns_response = await self.gemini.generate_content(
            f"{blog_response.text}\n\n위 내용을 트위터용 280자 이하로 요약하세요."
        )

        return {
            "policy_id": policy_id,
            "candidate_id": candidate_id,
            "blog_post": blog_response.text,
            "social_summary": sns_response.text,
            "difficulty_level": "쉬움",  # 일반인 기준
            "created_at": datetime.now().isoformat(),
        }

    # ==================== 내부 헬퍼 메서드 ====================

    def _extract_hashtags(self, content: str) -> List[str]:
        """콘텐츠에서 해시태그 추출"""
        import re

        hashtags = re.findall(r"#\w+", content)
        return hashtags or ["#정치", "#선거", "#투표"]

    async def _suggest_media(self, topic: str) -> str:
        """주제에 맞는 미디어 제안"""
        media_suggestions = {
            "경제 정책": "경제 그래프, 일자리 통계",
            "청년 정책": "청년 인터뷰, SNS 영상",
            "복지 정책": "노인 인터뷰, 복지시설 방문",
            "교육 정책": "학교 방문, 학생 인터뷰",
        }
        return media_suggestions.get(topic, "후보자 사진, 배경 영상")

    def _suggest_optimal_posting_time(self, content_type: ContentType) -> str:
        """최적 포스팅 시간 제안"""
        times = {
            ContentType.TWITTER: "평일 오전 9시 또는 저녁 6시",
            ContentType.INSTAGRAM: "평일 오전 10시 또는 저녁 7시",
            ContentType.FACEBOOK: "평일 오후 1-3시",
        }
        return times.get(content_type, "오전 10시")

    def _estimate_engagement(self, content: str, content_type: ContentType) -> Dict:
        """예상 인게이지먼트"""
        base_engagement = {
            ContentType.TWITTER: {"likes": 50, "retweets": 20},
            ContentType.INSTAGRAM: {"likes": 200, "comments": 30},
            ContentType.FACEBOOK: {"likes": 100, "shares": 15},
        }

        # 콘텐츠 길이에 따라 조정
        length_factor = len(content) / 500
        factor = min(length_factor, 1.5)  # 최대 1.5배

        base = base_engagement.get(content_type, {})
        return {
            k: int(v * factor) for k, v in base.items()
        }

    def _summarize_news(self, news_items: List[Dict]) -> str:
        """뉴스 요약"""
        if not news_items:
            return "오늘 발생한 주요 이슈가 없습니다."

        summary_parts = []
        for item in news_items[:2]:
            summary_parts.append(f"- {item.get('title', 'N/A')}: {item.get('summary', '')[:50]}...")

        return "\n".join(summary_parts)

    def _parse_video_scenes(self, script: str) -> List[Dict]:
        """동영상 대본에서 장면 파싱"""
        return [
            {
                "time": "0:00-0:10",
                "action": "오프닝 자막 및 배경음악",
            },
            {
                "time": "0:10-0:50",
                "action": "후보자 인터뷰 및 정책 설명",
            },
            {
                "time": "0:50-1:00",
                "action": "클로징 자막 및 웹사이트 주소",
            },
        ]

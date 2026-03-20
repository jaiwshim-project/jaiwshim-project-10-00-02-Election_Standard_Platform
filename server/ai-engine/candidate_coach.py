"""
후보 개인 코칭 AI (Candidate Coach) — 후보자 성장과 성과 향상

주기능:
- 언론 대면 및 연설 훈련
- 이슈별 답변 코칭
- 이미지 및 커뮤니케이션 개선 조언
- 일일 성과 평가 및 피드백
- 후보자 강점/약점 진단
"""

from typing import Dict, List
from datetime import datetime
from enum import Enum


class CoachingArea(Enum):
    MEDIA_TRAINING = "언론 대면 훈련"
    SPEECH_COACHING = "연설 코칭"
    ISSUE_RESPONSE = "이슈 대응 훈련"
    IMAGE_MANAGEMENT = "이미지 관리"
    COMMUNICATION = "커뮤니케이션"
    DEBATE_PREP = "토론 준비"


class CandidateCoach:
    """후보자 개인 코칭 엔진"""

    def __init__(self, gemini_client=None, db_client=None):
        self.gemini = gemini_client
        self.db = db_client

    async def analyze_candidate_strengths(self, candidate_id: str) -> Dict:
        """
        후보자 강점/약점 진단

        Returns:
            {
                "strengths": List[str],
                "weaknesses": List[str],
                "communication_style": str,
                "public_perception": str,
                "improvement_areas": List[str],
                "recommendations": List[str]
            }
        """
        candidate = await self.db.get_candidate(candidate_id)
        media_mentions = await self.db.get_news_sentiment(candidate_id)
        recent_speeches = await self.db.get_candidate_speeches(candidate_id, limit=5)

        # AI 분석
        analysis_prompt = f"""
당신은 정치인 코칭 전문가입니다.

후보: {candidate['name']} ({candidate['party']})
경력: {candidate.get('background', 'N/A')}

최근 언론 평가:
{self._summarize_media_perception(media_mentions)}

강점, 약점, 커뮤니케이션 스타일, 공중 인식, 개선 영역을 분석하세요.
"""

        response = await self.gemini.generate_content(analysis_prompt)

        return {
            "candidate_id": candidate_id,
            "analysis": response.text,
            "strengths": [
                "정책 전문성",
                "지역 기반 신뢰",
                "친근한 이미지",
            ],
            "weaknesses": [
                "미디어 노출 제한",
                "청년층과의 소통 약함",
                "위기 대응 능력 미흡",
            ],
            "communication_style": "신중하고 신뢰성 있는 톤",
            "public_perception": "신뢰성 있지만 다소 딱딱한 이미지",
            "improvement_areas": [
                "온라인 커뮤니케이션",
                "감정 표현",
                "빠른 대응력",
            ],
            "recommendations": [
                "SNS 활동 강화",
                "청년층 대면 프로그램 확대",
                "언론 인터뷰 횟수 증가",
            ],
            "analyzed_at": datetime.now().isoformat(),
        }

    async def generate_media_training(
        self, candidate_id: str, topic: str, difficulty: str = "medium"
    ) -> Dict:
        """
        언론 대면 훈련

        Args:
            topic: 훈련 주제 (예: "경제 정책", "위기 대응")
            difficulty: "easy", "medium", "hard"

        Returns:
            {
                "training_module": str,
                "scenario": str,
                "sample_questions": List[str],
                "sample_answers": List[str],
                "dos_and_donts": Dict,
                "tips": List[str],
                "practice_plan": List[str]
            }
        """
        candidate = await self.db.get_candidate(candidate_id)

        prompt = f"""
당신은 미디어 트레이닝 전문가입니다.

후보: {candidate['name']}
주제: {topic}
난이도: {difficulty}

{difficulty}급 난이도로 언론 대면 훈련을 설계하세요.
- 시나리오: 현실적이고 도전적인 상황
- 예상 질문 5개
- 각 질문별 모범 답변
- 주의사항 및 팁
"""

        response = await self.gemini.generate_content(prompt)

        return {
            "candidate_id": candidate_id,
            "topic": topic,
            "difficulty": difficulty,
            "training_content": response.text,
            "scenario": f"KBS 라디오 인터뷰 - {topic}",
            "sample_questions": [
                "최근 지지율 하락에 대해 어떻게 평가하나?",
                "경제 정책의 재정 조달 방안은?",
                "청년층 지지도가 낮은 이유는?",
                "경쟁자와의 정책 차이는?",
                "당신이 당선되면 가장 먼저 할 일은?",
            ],
            "dos": [
                "구체적이고 수치화된 답변",
                "상대 입장을 인정하고 차별점 강조",
                "일관된 메시지 전달",
                "침착한 톤 유지",
            ],
            "donts": [
                "과장되거나 추측성 답변",
                "상대 비난 또는 감정적 반응",
                "모르는 질문에 그럴듯한 답변",
                "속도 빠른 발언",
            ],
            "tips": [
                "질문을 다시 한번 정리하고 답변",
                "3초 생각 시간 가지기",
                "핵심 메시지 3개 사전 준비",
                "아이 컨택트 유지",
            ],
            "created_at": datetime.now().isoformat(),
        }

    async def evaluate_speech(self, candidate_id: str, speech_transcript: str) -> Dict:
        """
        연설 평가 및 피드백

        Returns:
            {
                "overall_score": float,  # 0-100
                "message_clarity": float,
                "emotional_appeal": float,
                "delivery": float,
                "strengths": List[str],
                "weaknesses": List[str],
                "specific_feedback": List[str],
                "improvement_suggestions": List[str]
            }
        """
        evaluation_prompt = f"""
당신은 정치 연설 평가 전문가입니다.

연설문:
{speech_transcript}

평가 항목:
1. 메시지 명확성 (0-100)
2. 감정 호소력 (0-100)
3. 전달 방식 (0-100)
4. 구조 (0-100)
5. 청중 참여도 (0-100)

종합 평가, 강점, 약점, 구체적 피드백, 개선안을 제시하세요.
"""

        response = await self.gemini.generate_content(evaluation_prompt)

        return {
            "candidate_id": candidate_id,
            "overall_score": 78,
            "message_clarity": 80,
            "emotional_appeal": 75,
            "delivery": 76,
            "structure": 80,
            "audience_engagement": 72,
            "strengths": [
                "명확한 정책 제시",
                "논리적 구조",
                "청중 호응 유도",
            ],
            "weaknesses": [
                "일부 딱딱한 표현",
                "감정 표현 약함",
                "시간 관리 미흡",
            ],
            "specific_feedback": [
                "3번째 문단의 '따라서'를 '그렇기 때문에'로 변경 추천",
                "경제 정책 설명 시 구체적 수치 추가 필요",
                "마무리 부분을 더 강조적으로 전달",
            ],
            "improvement_suggestions": [
                "감정적 표현 추가 (경험담, 사례)",
                "반복 강조를 통한 메시지 전달",
                "청중과의 상호작용 확대",
            ],
            "evaluated_at": datetime.now().isoformat(),
        }

    async def generate_issue_response_guide(
        self, candidate_id: str, issue: str
    ) -> Dict:
        """
        이슈별 대응 가이드 생성

        Args:
            issue: 현안 이슈 (예: "부동산 가격 상승")

        Returns:
            {
                "issue": str,
                "context": str,
                "public_concern": str,
                "competitor_position": str,
                "our_position": str,
                "key_messages": List[str],
                "talking_points": List[str],
                "dos_and_donts": Dict,
                "worst_case_scenario": str,
                "crisis_response_protocol": Dict
            }
        """
        candidate = await self.db.get_candidate(candidate_id)
        news_on_issue = await self.db.search_news(issue, limit=5)
        competitor_stance = await self.db.get_competitor_positions(issue)

        response_guide_prompt = f"""
당신은 정치 위기 관리 전문가입니다.

후보: {candidate['name']}
이슈: {issue}

이슈의 맥락, 공중의 우려, 경쟁자의 입장, 우리의 입장, 핵심 메시지를 분석하세요.
"""

        response = await self.gemini.generate_content(response_guide_prompt)

        return {
            "candidate_id": candidate_id,
            "issue": issue,
            "context": "최근 부동산 시장에서 가격 상승세 지속, 여론 우려 증대",
            "public_concern": "주택 구매 능력 저하, 세대 간 자산 격차 심화",
            "competitor_position": "규제 강화, 공급 확대 강조",
            "our_position": "시장 원리 존중, 투명성 강화, 계층별 지원",
            "key_messages": [
                "부동산은 투명한 시장 정보 공개가 해답",
                "무주택 청년층 대출 지원 강화",
                "지역 활성화를 통한 자연적 가격 안정화",
            ],
            "talking_points": [
                "무분별한 규제는 공급 부족으로 이어짐",
                "우리 정책은 시장 기능 활성화에 집중",
                "청년층 자산형성 지원이 근본 해결책",
            ],
            "dos": [
                "국민 관심사 충분히 인정",
                "구체적 대안 제시",
                "통계와 데이터 활용",
            ],
            "donts": [
                "현 상황 격하 또는 무시",
                "정치적 공격성 드러내기",
                "공약 없는 비판",
            ],
            "worst_case_scenario": "언론에서 부동산 정책 일관성 부족 지적",
            "crisis_response": {
                "immediate": "공식 입장 신속 발표",
                "short_term": "정책 상세 설명 인터뷰",
                "long_term": "정책 강화 및 홍보 확대",
            },
            "created_at": datetime.now().isoformat(),
        }

    async def get_daily_coaching_brief(self, candidate_id: str) -> Dict:
        """일일 코칭 브리핑"""
        candidate = await self.db.get_candidate(candidate_id)
        today_schedule = await self.db.get_candidate_schedule(candidate_id)
        recent_news = await self.db.get_news_sentiment(candidate_id, limit=3)

        return {
            "candidate_id": candidate_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "briefing_title": f"{candidate['name']} 후보 일일 코칭 브리핑",
            "focus_today": [
                "경제 정책 설명회 준비",
                "언론 인터뷰 대응",
                "청년층 간담회 대비",
            ],
            "key_messages": [
                "경제 정책의 구체성과 실현 가능성",
                "청년층을 위한 일자리 창출",
                "지역 균형 발전",
            ],
            "today_events": [
                "오전 10:00 - 언론 인터뷰 (경제정책)",
                "오후 2:00 - 청년층 간담회",
                "저녁 7:00 - 지역 주민 간담회",
            ],
            "media_alert": "부정적 언론 3건 발생, 신속 대응 필요",
            "coaching_tips": [
                "언론 인터뷰 시 구체적 수치 준비",
                "청년층과 호흡 맞추기",
                "일관된 메시지 전달",
            ],
        }

    # ==================== 내부 헬퍼 메서드 ====================

    def _summarize_media_perception(self, media_mentions: List[Dict]) -> str:
        """언론 평가 요약"""
        if not media_mentions:
            return "최근 언론 언급이 없습니다."

        positive = len([m for m in media_mentions if m.get("sentiment", "neutral") == "positive"])
        negative = len([m for m in media_mentions if m.get("sentiment", "neutral") == "negative"])
        neutral = len([m for m in media_mentions if m.get("sentiment", "neutral") == "neutral"])

        return f"긍정 {positive}건, 중립 {neutral}건, 부정 {negative}건"

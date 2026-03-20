"""
판세 감지 AI (Election Radar) — 실시간 여론 흐름 감지

주기능:
- 여론 변화 추이 실시간 감지
- 이슈별 영향도 분석
- 위험 신호 조기 경보
- 추세 예측
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum


class TrendDirection(Enum):
    RISING = "상승"
    FALLING = "하강"
    STABLE = "안정"
    VOLATILE = "변동"


class ElectionRadar:
    """판세 감지 AI 엔진"""

    def __init__(self, db_client=None, gemini_client=None):
        self.db = db_client
        self.gemini = gemini_client

        # 감지 임계값
        self.TREND_THRESHOLD = 2.0  # 2% 이상 변화
        self.WARNING_THRESHOLD = -5.0  # -5% 이상 하락
        self.VOLATILITY_THRESHOLD = 3.5  # 표준편차

    async def detect_trend(
        self, candidate_id: str, time_period: str = "1month"
    ) -> Dict:
        """
        여론 추세 감지

        Args:
            candidate_id: 후보 ID
            time_period: "1week", "1month", "3month"

        Returns:
            {
                "direction": TrendDirection,
                "magnitude": float,  # 변화량
                "velocity": float,  # 변화 속도
                "momentum": float,  # 추진력
                "signals": List[str],
                "forecast": Dict
            }
        """
        # 1. 기간별 지지율 데이터 조회
        analytics = await self.db.get_analytics(
            candidate_id=candidate_id, time_period=time_period
        )

        if len(analytics) < 2:
            return {"error": "불충분한 데이터"}

        # 2. 추세 분석
        trend_direction = self._calculate_trend_direction(analytics)
        magnitude = self._calculate_magnitude(analytics)
        velocity = self._calculate_velocity(analytics)
        momentum = self._calculate_momentum(analytics)

        # 3. 신호 감지
        signals = self._detect_signals(analytics, magnitude, velocity)

        # 4. 추세 예측
        forecast = await self._forecast_trend(analytics)

        return {
            "candidate_id": candidate_id,
            "period": time_period,
            "direction": trend_direction.value,
            "magnitude": magnitude,
            "velocity": velocity,
            "momentum": momentum,
            "signals": signals,
            "forecast": forecast,
            "updated_at": datetime.now().isoformat(),
        }

    async def detect_issue_impact(
        self, candidate_id: str, issue_category: str
    ) -> Dict:
        """
        이슈별 영향도 분석

        Args:
            candidate_id: 후보 ID
            issue_category: "경제", "복지", "교육", "안전" 등

        Returns:
            {
                "issue": str,
                "impact_score": float,  # -100 ~ 100
                "affected_demographics": List[str],
                "trend": str,
                "counterarguments": List[str]
            }
        """
        # 1. 해당 이슈 관련 뉴스/여론 조회
        news_items = await self.db.get_news_by_category(
            category=issue_category, limit=10
        )

        # 2. 감정 분석
        sentiment_score = self._analyze_sentiment(news_items)

        # 3. 우리 정책과의 연계도
        our_policy_relevance = await self._calculate_policy_relevance(
            candidate_id, issue_category
        )

        # 4. 인구통계학적 영향도
        affected_demographics = self._identify_affected_demographics(issue_category)

        # 5. 대응 필요성 판단
        impact_score = self._calculate_impact_score(
            sentiment_score, our_policy_relevance, len(affected_demographics)
        )

        return {
            "issue": issue_category,
            "impact_score": impact_score,
            "severity": self._classify_severity(impact_score),
            "affected_demographics": affected_demographics,
            "sentiment": sentiment_score,
            "policy_alignment": our_policy_relevance,
            "action_required": impact_score < -30,
            "recommended_response": await self._generate_response_strategy(
                issue_category, impact_score
            ),
        }

    async def early_warning_check(self, candidate_id: str) -> Dict:
        """
        위험 신호 조기 경보

        Returns:
            {
                "warnings": List[str],
                "critical_alerts": List[str],
                "risk_level": str  # "critical", "high", "medium", "low"
            }
        """
        warnings = []
        critical_alerts = []

        # 1. 지지율 급락 감지
        recent_trend = await self.detect_trend(candidate_id, "1week")
        if recent_trend.get("magnitude", 0) < self.WARNING_THRESHOLD:
            critical_alerts.append(
                f"⚠️ 주간 지지율 {abs(recent_trend['magnitude'])}% 급락 감지"
            )

        # 2. 주요 이슈 부정 영향 감지
        key_issues = ["경제", "복지", "교육", "안전"]
        for issue in key_issues:
            impact = await self.detect_issue_impact(candidate_id, issue)
            if impact.get("action_required"):
                warnings.append(f"⚠️ '{issue}' 이슈 부정 영향 증가 중")

        # 3. 경쟁자 지지율 상승 감지
        competitors = await self.db.get_competitors(candidate_id)
        for comp in competitors:
            if comp.get("approval_trend", 0) > 3.0:
                warnings.append(
                    f"📈 {comp['name']} 지지율 {comp['approval_trend']}% 상승"
                )

        # 4. 미디어 부정 언급 증가
        negative_mentions = await self.db.get_news_sentiment(
            candidate_id, sentiment="negative", limit=10
        )
        if len(negative_mentions) > 5:
            critical_alerts.append("🔴 부정 언론 언급 급증 (5건 이상)")

        risk_level = "critical" if critical_alerts else ("high" if warnings else "medium")

        return {
            "candidate_id": candidate_id,
            "risk_level": risk_level,
            "critical_alerts": critical_alerts,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat(),
        }

    # ==================== 내부 계산 메서드 ====================

    def _calculate_trend_direction(self, analytics: List[Dict]) -> TrendDirection:
        """추세 방향 계산"""
        if len(analytics) < 2:
            return TrendDirection.STABLE

        first_rate = analytics[0].get("approval_rate", 0)
        last_rate = analytics[-1].get("approval_rate", 0)
        change = last_rate - first_rate

        volatility = self._calculate_volatility(analytics)

        if volatility > self.VOLATILITY_THRESHOLD:
            return TrendDirection.VOLATILE
        elif change > self.TREND_THRESHOLD:
            return TrendDirection.RISING
        elif change < -self.TREND_THRESHOLD:
            return TrendDirection.FALLING
        else:
            return TrendDirection.STABLE

    def _calculate_magnitude(self, analytics: List[Dict]) -> float:
        """변화량 계산"""
        if len(analytics) < 2:
            return 0.0
        first = analytics[0].get("approval_rate", 0)
        last = analytics[-1].get("approval_rate", 0)
        return round(last - first, 2)

    def _calculate_velocity(self, analytics: List[Dict]) -> float:
        """변화 속도 계산 (일일 변화율)"""
        if len(analytics) < 2:
            return 0.0
        magnitude = self._calculate_magnitude(analytics)
        days = len(analytics) - 1
        return round(magnitude / max(days, 1), 3)

    def _calculate_momentum(self, analytics: List[Dict]) -> float:
        """추진력 계산 (최근 변화 속도)"""
        if len(analytics) < 3:
            return 0.0
        recent = analytics[-3:]
        changes = [recent[i + 1].get("approval_rate", 0) - recent[i].get("approval_rate", 0)
                   for i in range(len(recent) - 1)]
        return round(sum(changes) / len(changes), 3)

    def _calculate_volatility(self, analytics: List[Dict]) -> float:
        """변동성 계산 (표준편차)"""
        if len(analytics) < 2:
            return 0.0
        rates = [a.get("approval_rate", 0) for a in analytics]
        mean = sum(rates) / len(rates)
        variance = sum((r - mean) ** 2 for r in rates) / len(rates)
        return round(variance ** 0.5, 3)

    def _detect_signals(
        self, analytics: List[Dict], magnitude: float, velocity: float
    ) -> List[str]:
        """신호 감지"""
        signals = []

        if magnitude > 5:
            signals.append("📈 급상승 신호")
        elif magnitude < -5:
            signals.append("📉 급하강 신호")

        if velocity > 1.0:
            signals.append("🚀 가속 상승 중")
        elif velocity < -1.0:
            signals.append("⚡ 급속 하락 중")

        return signals

    async def _forecast_trend(self, analytics: List[Dict]) -> Dict:
        """추세 예측 (1주일, 1개월)"""
        # 간단한 선형 예측
        if len(analytics) < 2:
            return {}

        velocity = self._calculate_velocity(analytics)
        last_rate = analytics[-1].get("approval_rate", 0)

        return {
            "1week_forecast": round(last_rate + velocity * 7, 2),
            "1month_forecast": round(last_rate + velocity * 30, 2),
            "confidence": 0.75,
        }

    def _analyze_sentiment(self, news_items: List[Dict]) -> float:
        """감정 분석 (-100 ~ 100)"""
        if not news_items:
            return 0.0
        sentiment_sum = sum(item.get("sentiment_score", 0) for item in news_items)
        return round(sentiment_sum / len(news_items), 2)

    async def _calculate_policy_relevance(
        self, candidate_id: str, issue_category: str
    ) -> float:
        """정책 연계도 계산"""
        policies = await self.db.get_policies(
            candidate_id=candidate_id, category=issue_category
        )
        return len(policies) / max(await self.db.count_total_policies(candidate_id), 1)

    def _identify_affected_demographics(self, issue_category: str) -> List[str]:
        """영향받는 인구통계"""
        demographic_map = {
            "경제": ["20-30대", "40-50대"],
            "복지": ["60대 이상", "저소득층"],
            "교육": ["20-30대", "학부모"],
            "안전": ["전체"],
        }
        return demographic_map.get(issue_category, ["전체"])

    def _calculate_impact_score(
        self, sentiment: float, policy_relevance: float, demographic_count: int
    ) -> float:
        """영향도 점수 계산"""
        sentiment_weight = sentiment * 0.5
        relevance_weight = policy_relevance * 100 * 0.3
        demographic_weight = demographic_count * 10 * 0.2
        return round(sentiment_weight + relevance_weight + demographic_weight, 2)

    def _classify_severity(self, impact_score: float) -> str:
        """심각도 분류"""
        if impact_score < -50:
            return "위기"
        elif impact_score < -30:
            return "높음"
        elif impact_score < -10:
            return "중간"
        else:
            return "낮음"

    async def _generate_response_strategy(
        self, issue_category: str, impact_score: float
    ) -> List[str]:
        """대응 전략 생성"""
        if impact_score > -30:
            return []

        strategies = [
            f"'{issue_category}' 분야 정책 강조",
            "전문가 자문단 활동 강화",
            "언론 인터뷰 및 보도자료 배포",
            "유권자 접촉 활동 강화",
        ]

        return strategies

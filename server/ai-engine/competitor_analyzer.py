"""
경쟁자 분석 엔진 — 실시간 경쟁 상대 비교 분석

주기능:
- 경쟁 상대 강점/약점 자동 파악
- 지지율 추이 비교 분석
- 정책 차별성 분석
- 대응 전략 추천
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CompetitorAnalysis:
    competitor_id: str
    name: str
    party: str
    approval_rate: float
    approval_trend: float  # 추이 (증감 %)
    strengths: List[str]
    weaknesses: List[str]
    key_policies: List[str]
    counter_strategies: List[str]
    risk_level: str  # "high", "medium", "low"
    recommended_actions: List[str]


class CompetitorAnalyzer:
    """경쟁자 실시간 분석 엔진"""

    def __init__(self, gemini_client=None, db_client=None):
        self.gemini = gemini_client
        self.db = db_client

    async def analyze_competitor(
        self, competitor_id: str, our_candidate_id: str
    ) -> CompetitorAnalysis:
        """
        경쟁 상대 분석

        Args:
            competitor_id: 경쟁 상대 ID
            our_candidate_id: 우리 후보 ID

        Returns:
            경쟁자 분석 결과
        """
        # 1. 기본 정보 조회
        competitor = await self.db.get_competitor(competitor_id)
        our_candidate = await self.db.get_candidate(our_candidate_id)

        # 2. 지지율 추이 분석
        approval_trend = await self._analyze_approval_trend(competitor_id)

        # 3. 정책 비교 분석
        competitor_policies = await self._extract_key_policies(competitor_id)
        our_policies = await self._extract_key_policies(our_candidate_id)

        # 4. AI 기반 강점/약점 분석
        analysis = await self._generate_analysis(
            competitor, our_candidate, competitor_policies, our_policies
        )

        # 5. 대응 전략 생성
        counter_strategies = await self._generate_counter_strategies(analysis)

        return CompetitorAnalysis(
            competitor_id=competitor_id,
            name=competitor["name"],
            party=competitor["party"],
            approval_rate=competitor.get("approval_rate", 0),
            approval_trend=approval_trend,
            strengths=analysis.get("strengths", []),
            weaknesses=analysis.get("weaknesses", []),
            key_policies=competitor_policies,
            counter_strategies=counter_strategies,
            risk_level=analysis.get("risk_level", "medium"),
            recommended_actions=analysis.get("recommendations", []),
        )

    async def _analyze_approval_trend(self, competitor_id: str) -> float:
        """지지율 추이 분석 (주간 변화율)"""
        analytics = await self.db.get_analytics(
            candidate_id=competitor_id, time_period="1week"
        )

        if len(analytics) >= 2:
            latest = analytics[-1]["approval_rate"]
            previous = analytics[-2]["approval_rate"]
            return round((latest - previous) / previous * 100, 2)
        return 0.0

    async def _extract_key_policies(self, candidate_id: str) -> List[str]:
        """주요 정책 추출"""
        policies = await self.db.get_policies(candidate_id=candidate_id, limit=5)
        return [p["title"] for p in policies]

    async def _generate_analysis(
        self, competitor: Dict, our_candidate: Dict, comp_policies: List[str], our_policies: List[str]
    ) -> Dict:
        """AI 기반 강점/약점 분석"""
        prompt = f"""
당신은 정치 분석 전문가입니다.

경쟁 상대: {competitor['name']} ({competitor['party']})
- 현재 지지율: {competitor.get('approval_rate', 0)}%
- 주요 정책: {', '.join(comp_policies)}

우리 후보: {our_candidate['name']}
- 현재 지지율: {our_candidate.get('approval_rate', 0)}%
- 주요 정책: {', '.join(our_policies)}

경쟁 상대의 강점, 약점, 위험도, 권고사항을 JSON 형식으로 분석하세요.
"""

        response = await self.gemini.generate_content(prompt)
        return self._parse_analysis_response(response.text)

    def _parse_analysis_response(self, response: str) -> Dict:
        """분석 응답 파싱"""
        # 실제 환경에서는 JSON 파싱
        return {
            "strengths": ["정책 공약력", "지역 기반", "언론 호응도"],
            "weaknesses": ["젊은층 지지 약함", "경제 정책 논쟁"],
            "risk_level": "medium",
            "recommendations": ["정책 차별성 강화", "청년층 공략"],
        }

    async def _generate_counter_strategies(self, analysis: Dict) -> List[str]:
        """대응 전략 생성"""
        strategies = []

        # 경쟁자의 약점 공략
        for weakness in analysis.get("weaknesses", []):
            strategies.append(f"'{weakness}' 분야 강화 강조")

        # 차별화 전략
        strategies.append("우리의 강점 차별화 마케팅")
        strategies.append("미정층 공략 강화")

        return strategies

    async def compare_competitors(
        self, our_candidate_id: str, competitors_ids: List[str]
    ) -> Dict:
        """
        여러 경쟁 상대 비교 분석

        Returns:
            {
                "our_candidate": {...},
                "competitors": [CompetitorAnalysis, ...],
                "threat_assessment": {...},
                "opportunities": [...]
            }
        """
        analyses = []
        for comp_id in competitors_ids:
            analysis = await self.analyze_competitor(comp_id, our_candidate_id)
            analyses.append(analysis)

        # 위협도 평가
        threat_assessment = self._assess_overall_threat(analyses)

        # 기회 발굴
        opportunities = self._identify_opportunities(analyses)

        return {
            "our_candidate_id": our_candidate_id,
            "competitors": [a.__dict__ for a in analyses],
            "threat_assessment": threat_assessment,
            "opportunities": opportunities,
        }

    def _assess_overall_threat(self, analyses: List[CompetitorAnalysis]) -> Dict:
        """전체 위협도 평가"""
        high_risk = [a for a in analyses if a.risk_level == "high"]
        medium_risk = [a for a in analyses if a.risk_level == "medium"]

        return {
            "total_risk": "high" if high_risk else "medium" if medium_risk else "low",
            "high_risk_competitors": [a.name for a in high_risk],
            "threat_index": len(high_risk) * 3 + len(medium_risk),
        }

    def _identify_opportunities(self, analyses: List[CompetitorAnalysis]) -> List[str]:
        """기회 발굴"""
        opportunities = []

        # 경쟁자의 약점이 많은 분야
        weakness_freq = {}
        for analysis in analyses:
            for weakness in analysis.weaknesses:
                weakness_freq[weakness] = weakness_freq.get(weakness, 0) + 1

        # 가장 많은 경쟁자가 약한 분야
        if weakness_freq:
            top_weakness = max(weakness_freq, key=weakness_freq.get)
            opportunities.append(f"'{top_weakness}' 분야 집중 공략")

        # 미정층 규모 확인
        opportunities.append("미정층 적극 공략 추천")

        return opportunities

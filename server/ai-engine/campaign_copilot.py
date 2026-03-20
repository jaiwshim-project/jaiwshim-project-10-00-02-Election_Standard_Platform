"""
AI 캠프 코파일럿 (Campaign Copilot) — 전략 추천 엔진

주기능:
- 현재 판세 분석 기반 최적화된 캠프 전략 제시
- 주간/월간 액션 플랜 자동 생성
- 우선순위 기반 실행 가이던스
- 성과 예측
"""

from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class CampaignAction:
    """캠프 액션 항목"""

    def __init__(
        self,
        action_id: str,
        title: str,
        description: str,
        priority: Priority,
        target_demographic: str,
        expected_impact: float,
        effort_required: str,
        timeline: Dict[str, str],
    ):
        self.action_id = action_id
        self.title = title
        self.description = description
        self.priority = priority
        self.target_demographic = target_demographic
        self.expected_impact = expected_impact  # 지지율 영향도 (%)
        self.effort_required = effort_required  # "low", "medium", "high"
        self.timeline = timeline  # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}


class CampaignCopilot:
    """AI 캠프 코파일럿 엔진"""

    def __init__(self, db_client=None, gemini_client=None, radar_engine=None, competitor_analyzer=None):
        self.db = db_client
        self.gemini = gemini_client
        self.radar = radar_engine
        self.competitor = competitor_analyzer

    async def generate_strategy_plan(
        self, candidate_id: str, planning_horizon: str = "1month"
    ) -> Dict:
        """
        종합 전략 플랜 생성

        Args:
            candidate_id: 후보 ID
            planning_horizon: "1week", "1month", "3month"

        Returns:
            {
                "plan_id": str,
                "horizon": str,
                "current_situation": Dict,
                "strategic_objectives": List[str],
                "immediate_actions": List[CampaignAction],
                "weekly_plan": List[Dict],
                "monthly_plan": Dict,
                "expected_outcomes": Dict,
                "risk_mitigation": List[str],
                "success_metrics": Dict
            }
        """
        # 1. 현재 상황 분석
        current_situation = await self._analyze_current_situation(candidate_id)

        # 2. 전략적 목표 설정
        strategic_objectives = self._define_strategic_objectives(current_situation)

        # 3. 즉시 실행 액션 도출
        immediate_actions = await self._generate_immediate_actions(
            candidate_id, current_situation
        )

        # 4. 주간/월간 플랜 생성
        weekly_plan = self._generate_weekly_plan(immediate_actions, planning_horizon)
        monthly_plan = self._generate_monthly_plan(
            immediate_actions, strategic_objectives
        )

        # 5. 예상 성과 계산
        expected_outcomes = self._forecast_outcomes(
            current_situation, immediate_actions
        )

        # 6. 위험 완화 전략
        risk_mitigation = self._identify_risks_and_mitigations(
            current_situation, immediate_actions
        )

        # 7. 성공 지표
        success_metrics = self._define_success_metrics(
            strategic_objectives, expected_outcomes
        )

        return {
            "candidate_id": candidate_id,
            "planning_horizon": planning_horizon,
            "generated_at": datetime.now().isoformat(),
            "current_situation": current_situation,
            "strategic_objectives": strategic_objectives,
            "immediate_actions": [
                {
                    "id": a.action_id,
                    "title": a.title,
                    "description": a.description,
                    "priority": a.priority.name,
                    "target_demographic": a.target_demographic,
                    "expected_impact": a.expected_impact,
                    "effort": a.effort_required,
                    "timeline": a.timeline,
                }
                for a in immediate_actions
            ],
            "weekly_plan": weekly_plan,
            "monthly_plan": monthly_plan,
            "expected_outcomes": expected_outcomes,
            "risk_mitigation": risk_mitigation,
            "success_metrics": success_metrics,
        }

    async def _analyze_current_situation(self, candidate_id: str) -> Dict:
        """현재 상황 분석"""
        candidate = await self.db.get_candidate(candidate_id)
        trend = await self.radar.detect_trend(candidate_id, "1month")
        warning = await self.radar.early_warning_check(candidate_id)

        return {
            "candidate_name": candidate.get("name"),
            "party": candidate.get("party"),
            "approval_rate": candidate.get("approval_rate", 0),
            "trend": trend.get("direction"),
            "trend_magnitude": trend.get("magnitude"),
            "risk_level": warning.get("risk_level"),
            "critical_alerts": warning.get("critical_alerts", []),
            "opportunities": await self.competitor.identify_opportunities([]),
        }

    def _define_strategic_objectives(self, situation: Dict) -> List[str]:
        """전략적 목표 설정"""
        objectives = []

        approval_rate = situation.get("approval_rate", 0)

        if approval_rate < 40:
            objectives.append("지지율 40% 이상 확보 (지표: 4주 내 2% 상승)")
        elif approval_rate < 45:
            objectives.append("지지율 45% 이상 확보 (지표: 4주 내 5% 상승)")
        else:
            objectives.append("지지율 50% 이상 달성 (지표: 8주 내 5% 상승)")

        objectives.append("청년층(20-30대) 지지도 55% 달성")
        objectives.append("주요 이슈별 전문성 강화")
        objectives.append("미정층 30% 이상 공략")

        return objectives

    async def _generate_immediate_actions(
        self, candidate_id: str, situation: Dict
    ) -> List[CampaignAction]:
        """즉시 실행 액션 도출"""
        actions = []

        # 액션 1: 핵심 이슈 기반 전략
        if "critical_alerts" in situation and situation["critical_alerts"]:
            actions.append(
                CampaignAction(
                    action_id="action_001",
                    title="위기 이슈 즉시 대응",
                    description="현재 논점 중인 주요 이슈에 대한 명확한 입장 발표 및 대안 제시",
                    priority=Priority.CRITICAL,
                    target_demographic="전체 유권자",
                    expected_impact=2.5,
                    effort_required="high",
                    timeline={
                        "start": datetime.now().strftime("%Y-%m-%d"),
                        "end": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                    },
                )
            )

        # 액션 2: 청년층 집중 공략
        actions.append(
            CampaignAction(
                action_id="action_002",
                title="청년층 집중 공략",
                description="SNS 캠페인, 온라인 대담, 청년 정책 설명회 개최",
                priority=Priority.HIGH,
                target_demographic="20-30대",
                expected_impact=3.5,
                effort_required="high",
                timeline={
                    "start": datetime.now().strftime("%Y-%m-%d"),
                    "end": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                },
            )
        )

        # 액션 3: 경제 정책 강화
        actions.append(
            CampaignAction(
                action_id="action_003",
                title="경제 정책 구체화",
                description="경제 정책 패키지 발표 및 전문가 자문단 활동 강화",
                priority=Priority.HIGH,
                target_demographic="40-50대",
                expected_impact=2.0,
                effort_required="medium",
                timeline={
                    "start": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                },
            )
        )

        # 액션 4: 지역 기반 강화
        actions.append(
            CampaignAction(
                action_id="action_004",
                title="주요 지역 집중 방문",
                description="강남, 서초, 중구 등 지지기반 지역 및 미확보 지역 주민 간담회 확대",
                priority=Priority.MEDIUM,
                target_demographic="지역별 맞춤",
                expected_impact=1.5,
                effort_required="medium",
                timeline={
                    "start": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "end": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
                },
            )
        )

        return sorted(actions, key=lambda a: a.priority.value)

    def _generate_weekly_plan(
        self, actions: List[CampaignAction], horizon: str
    ) -> List[Dict]:
        """주간 플랜 생성"""
        weeks = []
        weeks_count = 4 if horizon == "1month" else 1

        for week_num in range(1, weeks_count + 1):
            week_start = datetime.now() + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=6)

            week_actions = [
                a
                for a in actions
                if week_start.date()
                <= datetime.strptime(a.timeline["start"], "%Y-%m-%d").date()
                <= week_end.date()
            ]

            weeks.append(
                {
                    "week": week_num,
                    "period": f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}",
                    "actions": [
                        {
                            "title": a.title,
                            "priority": a.priority.name,
                            "target": a.target_demographic,
                        }
                        for a in week_actions
                    ],
                }
            )

        return weeks

    def _generate_monthly_plan(
        self, actions: List[CampaignAction], objectives: List[str]
    ) -> Dict:
        """월간 플랜 생성"""
        return {
            "month": datetime.now().strftime("%Y-%m"),
            "strategic_focus": objectives,
            "total_actions": len(actions),
            "critical_actions": len([a for a in actions if a.priority == Priority.CRITICAL]),
            "expected_total_impact": sum(a.expected_impact for a in actions),
        }

    def _forecast_outcomes(
        self, situation: Dict, actions: List[CampaignAction]
    ) -> Dict:
        """예상 성과 계산"""
        current_approval = situation.get("approval_rate", 0)
        total_impact = sum(a.expected_impact for a in actions)

        return {
            "current_approval": current_approval,
            "expected_approval": round(current_approval + total_impact, 1),
            "approval_increase": round(total_impact, 1),
            "confidence_level": 0.75,
            "timeline": "4주",
        }

    def _identify_risks_and_mitigations(
        self, situation: Dict, actions: List[CampaignAction]
    ) -> List[str]:
        """위험 식별 및 완화 전략"""
        mitigations = []

        if situation.get("risk_level") == "critical":
            mitigations.append(
                "위기 대응 전담팀 구성 및 24시간 모니터링 체계 구축"
            )

        if any(a.priority == Priority.CRITICAL for a in actions):
            mitigations.append("긴급 회의 소집 및 신속한 대응 체계 마련")

        mitigations.append("주간 여론조사 실시 및 추이 모니터링")
        mitigations.append("부정 이슈 발생 시 신속 대응 매뉴얼 준비")

        return mitigations

    def _define_success_metrics(
        self, objectives: List[str], outcomes: Dict
    ) -> Dict:
        """성공 지표 정의"""
        return {
            "primary_metric": "지지율 목표 달성도",
            "primary_target": f"{outcomes.get('expected_approval')}%",
            "secondary_metrics": [
                "청년층 지지도 증가",
                "미디어 호응도",
                "미정층 공략 성공율",
            ],
            "measurement_frequency": "주간",
            "success_threshold": 0.85,  # 85% 이상 달성
        }

    async def get_daily_briefing(self, candidate_id: str) -> Dict:
        """일일 브리핑"""
        return {
            "candidate_id": candidate_id,
            "briefing_date": datetime.now().strftime("%Y-%m-%d"),
            "approval_rate": (await self.db.get_candidate(candidate_id)).get(
                "approval_rate"
            ),
            "trend": (await self.radar.detect_trend(candidate_id, "1week")).get(
                "direction"
            ),
            "warnings": (await self.radar.early_warning_check(candidate_id)).get(
                "warnings"
            ),
            "today_actions": "오늘의 주요 일정: 청년층 정책 설명회, 언론 인터뷰 2건",
            "focus_areas": ["경제 정책 강조", "청년층 공략", "지역 방문"],
        }

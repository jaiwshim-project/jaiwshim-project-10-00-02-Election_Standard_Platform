"""
RAG Engine for Election Moon Un Platform
Gemini-based Retrieval Augmented Generation
"""

import google.generativeai as genai
from typing import Optional, List, Dict
import json
import os

class RAGEngine:
    """Gemini 기반 RAG 엔진"""

    INTENT_MAP = {
        "polling": ["지지율", "여론조사", "설문", "퍼센트"],
        "policy": ["공약", "정책", "계획", "방안"],
        "competitor": ["경쟁자", "상대", "비교", "vs"],
        "news": ["뉴스", "기사", "보도", "언론"],
        "analytics": ["판세", "분석", "전망", "예측"],
        "biography": ["약력", "이력", "경력", "출신"],
    }

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.llm = genai.GenerativeModel("gemini-1.5-pro")
        self.embed_model = "models/text-embedding-004"

    def classify_intent(self, question: str) -> str:
        """질문 의도 분류"""
        q_lower = question.lower()
        for intent, keywords in self.INTENT_MAP.items():
            if any(kw in q_lower for kw in keywords):
                return intent
        return "general"

    def embed_text(self, text: str) -> List[float]:
        """텍스트 임베딩 생성 (Gemini)"""
        try:
            result = genai.embed_content(
                model=self.embed_model,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            print(f"임베딩 생성 오류: {e}")
            return []

    def build_prompt(self, question: str, context_docs: List[Dict], intent: str) -> str:
        """RAG 프롬프트 구성"""
        context_text = "\n\n".join([
            f"[출처: {doc.get('report_title', '알 수 없음')}]\n{doc.get('chunk_text', '')}"
            for doc in context_docs
        ])

        return f"""당신은 정치 분석 AI 어시스턴트입니다.
아래 컨텍스트 정보를 바탕으로 질문에 답변하세요.

[질문 유형: {intent}]

=== 참고 문서 ===
{context_text}
=================

질문: {question}

지침:
- 제공된 컨텍스트만 사용하세요.
- 수치는 정확하게 인용하세요.
- 불확실한 내용은 "확인이 필요합니다"라고 명시하세요.
- 답변은 간결하고 명확하게 작성하세요."""

    def query(self, question: str, context_docs: Optional[List[Dict]] = None,
              session_id: Optional[str] = None) -> Dict:
        """메인 쿼리 처리"""
        # Intent 분류
        intent = self.classify_intent(question)

        # 컨텍스트 기본값
        if context_docs is None:
            context_docs = []

        # 프롬프트 생성
        prompt = self.build_prompt(question, context_docs, intent)

        # LLM 생성
        try:
            response = self.llm.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )

            return {
                "answer": response.text,
                "intent": intent,
                "sources": [
                    {
                        "report_id": doc.get("report_id"),
                        "chunk_id": doc.get("id"),
                        "similarity": doc.get("similarity", 0)
                    }
                    for doc in context_docs
                ],
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"오류 발생: {str(e)}",
                "intent": intent,
                "sources": [],
                "success": False
            }

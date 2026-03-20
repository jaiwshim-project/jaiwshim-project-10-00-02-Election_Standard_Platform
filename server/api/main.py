"""
Election Moon Un Platform - REST API
FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid

from ..ai_engine.rag_engine import RAGEngine

# Initialize FastAPI app
app = FastAPI(
    title="선거월운 API",
    description="AI 기반 정치 분석 플랫폼",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 설정
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize RAG Engine
rag_engine = RAGEngine(gemini_api_key=os.getenv("GEMINI_API_KEY", ""))

# ========== Request/Response Models ==========

class ChatRequest(BaseModel):
    question: str
    candidate_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    intent: str
    sources: List[dict]
    session_id: str
    success: bool

# ========== Endpoints ==========

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """RAG 기반 AI 질문 처리"""
    if len(req.question) > 2000:
        raise HTTPException(400, "질문이 너무 깁니다 (최대 2000자)")

    session_id = req.session_id or str(uuid.uuid4())

    result = rag_engine.query(
        question=req.question,
        context_docs=[],  # 실제로는 Vector DB에서 검색
        session_id=session_id
    )

    return ChatResponse(
        session_id=session_id,
        answer=result.get("answer", ""),
        intent=result.get("intent", ""),
        sources=result.get("sources", []),
        success=result.get("success", True)
    )

@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """후보자 정보 조회"""
    return {
        "id": candidate_id,
        "name": "오세훈",
        "party": "국민의힘",
        "district": "서울시장",
        "region": "서울"
    }

@app.get("/api/competitors")
async def get_competitors(candidate_id: Optional[str] = None):
    """경쟁자 비교 데이터"""
    return {
        "competitors": [
            {
                "id": str(uuid.uuid4()),
                "name": "조은희",
                "party": "더불어민주당",
                "strength_score": 85.5
            }
        ],
        "count": 1
    }

@app.get("/api/analytics")
async def get_analytics(
    candidate_id: Optional[str] = None,
    metric_type: Optional[str] = None,
    limit: int = 50
):
    """판세 분석 데이터"""
    return {
        "analytics": [
            {
                "metric_type": "approval_rating",
                "metric_value": 45.2,
                "measured_at": "2024-03-19T00:00:00Z"
            }
        ],
        "count": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

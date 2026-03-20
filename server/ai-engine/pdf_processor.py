"""
PDF Processing Module
Text extraction, chunking, and vectorization
"""

import re
from typing import List, Dict, Generator, Optional
import google.generativeai as genai


class PDFProcessor:
    """PDF 처리: 추출 → 청킹 → 벡터화"""

    CHUNK_SIZE = 800  # 토큰 수
    CHUNK_OVERLAP = 100

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.embed_model = "models/text-embedding-004"

    def extract_text_from_content(self, content: str, filename: str = "document") -> List[Dict]:
        """텍스트 추출 (파일 내용 기반)"""
        pages = []
        text_lines = content.split('\n')

        current_page = {"page": 1, "text": ""}

        for line in text_lines:
            line = self._clean_text(line)
            if line.strip():
                current_page["text"] += " " + line

        if current_page["text"].strip():
            pages.append(current_page)

        return pages

    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0b-\x1f]', '', text)
        return text.strip()

    def chunk_text(self, pages: List[Dict]) -> Generator[Dict, None, None]:
        """시맨틱 청킹"""
        buffer = ""
        buf_page = 1
        chunk_idx = 0

        for page_data in pages:
            paragraphs = page_data["text"].split('\n')
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if len(buffer) + len(para) > self.CHUNK_SIZE * 4:
                    if buffer:
                        yield {
                            "chunk_index": chunk_idx,
                            "chunk_text": buffer.strip(),
                            "page_number": buf_page
                        }
                        buffer = buffer[-self.CHUNK_OVERLAP * 4:]
                        chunk_idx += 1

                buffer += " " + para
                buf_page = page_data["page"]

        if buffer.strip():
            yield {
                "chunk_index": chunk_idx,
                "chunk_text": buffer.strip(),
                "page_number": buf_page
            }

    def embed_chunk(self, text: str) -> List[float]:
        """청크 임베딩"""
        try:
            result = genai.embed_content(
                model=self.embed_model,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            print(f"임베딩 오류: {e}")
            return []

    def process(self, content: str, filename: str = "document") -> List[Dict]:
        """전체 파이프라인"""
        pages = self.extract_text_from_content(content, filename)
        chunks_data = []

        for chunk in self.chunk_text(pages):
            embedding = self.embed_chunk(chunk["chunk_text"])
            chunks_data.append({
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "page_number": chunk["page_number"],
                "embedding": embedding,
                "token_count": len(chunk["chunk_text"]) // 4
            })

        return chunks_data

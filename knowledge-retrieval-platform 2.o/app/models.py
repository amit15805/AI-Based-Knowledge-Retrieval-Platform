from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class QueryIntent(str, Enum):
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    AMBIGUOUS = "ambiguous"

class QueryAnalysis(BaseModel):
    original_query: str
    cleaned_query: str
    intent: QueryIntent
    keywords: List[str]

class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: int
    relevance_score: float
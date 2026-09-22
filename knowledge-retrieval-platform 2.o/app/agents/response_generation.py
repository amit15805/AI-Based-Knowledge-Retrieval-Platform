# import google.generativeai as genai
# from app.config import settings
# import numpy as np 

# class ResponseGenerationAgent:
#     def __init__(self):
#         if settings.GEMINI_API_KEY:
#             genai.configure(api_key=settings.GEMINI_API_KEY)
#             self.model = genai.GenerativeModel("gemini-1.5-flash")
#         else:
#             self.model = None

#     async def generate(self, query: str, chunks: list, intent: str) -> dict:
#         if not chunks:
#             return {
#                 "answer": "I could not find sufficiently confident verified sources matching your query. Please provide more specifics or rephrase.",
#                 "confidence": 0.20,
#                 "confidence_label": "Low",
#                 "citations": []
#             }

#         context = "\n".join([f"[{c['id']}] ({c['source']}): {c['content']}" for c in chunks])
#         avg_score = float(np.mean([c["score"] for c in chunks])) if 'np' in globals() else chunks[0]["score"]

#         prompt = f"""Synthesize a direct, grounded answer for the user query using ONLY the provided context.
# Cite sources using bracket notation (e.g. [DOC-101]).
# Intent Style: {intent}

# Context:
# {context}

# Query: {query}
# Answer:"""

#         if self.model:
#             try:
#                 res = self.model.generate_content(prompt)
#                 answer_text = res.text.strip()
#             except Exception:
#                 answer_text = f"Based on {chunks[0]['source']}: {chunks[0]['content']} [{chunks[0]['id']}]"
#         else:
#             answer_text = f"Based on {chunks[0]['source']}: {chunks[0]['content']} [{chunks[0]['id']}]"

#         confidence_label = "High" if avg_score >= 0.70 else "Medium" if avg_score >= 0.50 else "Low"

#         return {
#             "answer": answer_text,
#             "confidence": round(avg_score, 2),
#             "confidence_label": confidence_label,
#             "citations": [c["id"] for c in chunks]
#         }


import os
import time
from typing import List, Dict
from google import genai
from google.genai import types
from app.models import QueryAnalysis, RetrievedChunk

class ResponseGenerationAgent:
    def __init__(self, client: genai.Client = None, api_key: str = None):
        if client:
            self.client = client
        else:
            resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
            self.client = genai.Client(api_key=resolved_key)

    def generate_comparative_response(self, analysis: QueryAnalysis, chunks: List[RetrievedChunk]) -> Dict[str, str]:
        user_query = analysis.original_query

        # 1. Format Context with exact point citations
        if chunks:
            context_blocks = [
                f"[Source: {c.source} | Chunk #{c.chunk_index} | Relevance: {int(c.relevance_score * 100)}%]:\n\"{c.text.strip()}\""
                for c in chunks
            ]
            pdf_context_payload = "\n\n".join(context_blocks)
        else:
            pdf_context_payload = "No matching documents found in past or present uploads."

        # 2. PDF Grounded Prompt
        pdf_prompt = f"""You are an enterprise document verification agent.
Answer the user's query using ONLY the provided PDF excerpts below.

CRITICAL CITATION RULE:
Every point in your answer MUST cite its exact source and chunk number using format:
[Source: filename.pdf, Chunk #X]

PDF Excerpts:
{pdf_context_payload}

User Query: {user_query}
PDF-Grounded Answer:"""

        # 3. Standalone Gemini API Prompt
        gemini_prompt = f"""Answer the following question using your general AI knowledge base.
Provide a clear, detailed explanation without referencing external files.

User Query: {user_query}
General Knowledge Answer:"""

        pdf_answer = self._safe_generate(pdf_prompt)
        gemini_answer = self._safe_generate(gemini_prompt)

        # 4. Comparison Summary
        comparison_prompt = f"""Compare these two answers to the query: "{user_query}"

Answer A (From Uploaded Past/Present PDFs):
{pdf_answer}

Answer B (General AI Knowledge):
{gemini_answer}

Provide a concise 3-point comparison highlighting agreement, PDF-specific details, and general knowledge gaps."""

        comparison_summary = self._safe_generate(comparison_prompt)

        return {
            "pdf_grounded_answer": pdf_answer,
            "gemini_api_answer": gemini_answer,
            "comparison_summary": comparison_summary
        }

    def _safe_generate(self, prompt: str) -> str:
        for attempt in range(3):
            try:
                res = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                if res and res.text:
                    return res.text
            except Exception as e:
                if any(err in str(e) for err in ["503", "UNAVAILABLE", "429"]):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return f"Generation error: {str(e)}"
        return "Service currently busy. Please try again."
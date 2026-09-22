# import google.generativeai as genai
# from app.config import settings

# class QueryUnderstandingAgent:
#     def __init__(self):
#         if settings.GEMINI_API_KEY:
#             genai.configure(api_key=settings.GEMINI_API_KEY)
#             self.model = genai.GenerativeModel("gemini-1.5-flash")
#         else:
#             self.model = None

#     async def classify(self, query: str) -> dict:
#         prompt = f"""You are a Query Understanding Agent. Classify the user query into exactly ONE category:
# - 'factual' (asking for facts, definitions, specific details)
# - 'procedural' (asking how-to, setup steps, operational guidelines)
# - 'comparative' (comparing two or more methods, metrics, tools)
# - 'ambiguous' (vague, missing target context, incomplete)

# Query: "{query}"

# Output ONLY a JSON object:
# {{"intent": "factual"|"procedural"|"comparative"|"ambiguous", "reasoning": "brief explanation"}}"""

#         if self.model:
#             try:
#                 res = self.model.generate_content(prompt)
#                 import json, re
#                 cleaned = re.search(r"\{.*\}", res.text, re.DOTALL)
#                 if cleaned:
#                     return json.loads(cleaned.group(0))
#             except Exception:
#                 pass

#         # Robust heuristic fallback
#         q_lower = query.lower().strip()
#         if len(q_lower.split()) <= 2 or q_lower in ["how does it work", "help", "what", "tell me"]:
#             return {"intent": "ambiguous", "reasoning": "Query lacks specific entity or operational context."}
#         if any(w in q_lower for w in ["vs", "difference", "compare", "better", "versus"]):
#             return {"intent": "comparative", "reasoning": "User is contrasting entities."}
#         if any(w in q_lower for w in ["how to", "steps", "guide", "procedure", "setup"]):
#             return {"intent": "procedural", "reasoning": "Step-by-step resolution requested."}
#         return {"intent": "factual", "reasoning": "Direct query seeking domain knowledge."}



import os
import json
from google import genai
from google.genai import types
from app.models import QueryAnalysis, QueryIntent

class QueryUnderstandingAgent:
    def __init__(self, client: genai.Client = None, api_key: str = None):
        if client:
            self.client = client
        else:
            resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
            self.client = genai.Client(api_key=resolved_key)

    def analyze(self, query: str) -> QueryAnalysis:
        prompt = f"""Analyze the user query for an enterprise RAG knowledge retrieval system.
Classify the intent into one of these exact categories:
- factual: Asking for a definition, specific fact, or general concept explanation.
- procedural: Asking how to do something, steps, or instructions.
- comparative: Asking to compare two or more concepts, tools, or approaches.
- ambiguous: Unclear, vague, or lacking context.

Query: "{query}"

Respond in valid JSON format with keys: "intent", "cleaned_query", "keywords".
Example:
{{"intent": "factual", "cleaned_query": "what is python", "keywords": ["python"]}}
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            data = json.loads(response.text)
            intent_str = data.get("intent", "factual").upper()
            
            intent_map = {
                "FACTUAL": QueryIntent.FACTUAL,
                "PROCEDURAL": QueryIntent.PROCEDURAL,
                "COMPARATIVE": QueryIntent.COMPARATIVE,
                "AMBIGUOUS": QueryIntent.AMBIGUOUS
            }
            intent = intent_map.get(intent_str, QueryIntent.FACTUAL)

            return QueryAnalysis(
                original_query=query,
                cleaned_query=data.get("cleaned_query", query),
                intent=intent,
                keywords=data.get("keywords", [])
            )
        except Exception:
            return QueryAnalysis(
                original_query=query,
                cleaned_query=query,
                intent=QueryIntent.FACTUAL,
                keywords=query.split()
            )
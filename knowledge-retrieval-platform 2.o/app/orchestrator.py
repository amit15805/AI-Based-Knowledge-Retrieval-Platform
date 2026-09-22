# 
import os
from google import genai
from app.agents.query_understanding import QueryUnderstandingAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.generator import ResponseGenerationAgent

class MultiAgentOrchestrator:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.query_agent = QueryUnderstandingAgent(client=self.client)
        self.retrieval_agent = RetrievalAgent()
        self.generator_agent = ResponseGenerationAgent(client=self.client)

    def process_query(self, query: str):
        analysis = self.query_agent.analyze(query)
        chunks = self.retrieval_agent.retrieve(analysis.cleaned_query)
        response_dict = self.generator_agent.generate_comparative_response(analysis, chunks)
        
        return {
            "intent": analysis.intent,
            "confidence_level": "HIGH" if chunks else "LOW",
            "pdf_grounded_answer": response_dict["pdf_grounded_answer"],
            "gemini_api_answer": response_dict["gemini_api_answer"],
            "comparison_summary": response_dict["comparison_summary"]
        }

    def ingest_document(self, file_path: str, filename: str):
        return self.retrieval_agent.ingest_file(file_path, filename)

    def get_documents(self):
        return self.retrieval_agent.list_documents()
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = "AI Knowledge Retrieval & Query Resolution Platform"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6IaLc_uT7VzSKoCi8eWW2rLjRtJdHYS-wE8gmKGsxXjgA")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.45
    PORT: int = 8000

settings = Settings()
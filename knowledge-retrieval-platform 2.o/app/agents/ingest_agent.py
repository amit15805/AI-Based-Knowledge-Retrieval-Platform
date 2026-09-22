import io
import json
import os
import re
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from app.config import settings

class IngestAgent:
    def __init__(self, data_path: str = "app/data/knowledge_store.json"):
        self.data_path = data_path
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def parse_file(self, filename: str, content_bytes: bytes) -> str:
        if filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content_bytes))
            text = " ".join([page.extract_text() or "" for page in reader.pages])
        else:
            text = content_bytes.decode("utf-8", errors="ignore")
        return re.sub(r"\s+", " ", text).strip()

    def chunk_text(self, text: str, chunk_size: int = 60, overlap: int = 15) -> list[str]:
        words = text.split()
        if not words:
            return []
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def analyze_and_ingest(self, filename: str, content_bytes: bytes) -> dict:
        raw_text = self.parse_file(filename, content_bytes)
        if not raw_text:
            return {"status": "error", "message": "Uploaded document is empty."}

        raw_chunks = self.chunk_text(raw_text)
        total_words = len(raw_text.split())

        # Load existing store
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                store = json.load(f)
        else:
            store = []

        # Create structured entries
        new_records = []
        base_id = len(store) + 1
        for idx, chunk_text in enumerate(raw_chunks):
            record = {
                "id": f"DOC-{base_id + idx:03d}",
                "source": filename,
                "content": chunk_text
            }
            new_records.append(record)

        store.extend(new_records)
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(store, f, indent=2)

        # Build initial analysis summary
        key_topics = list(set([w.capitalize() for w in re.findall(r"\b[A-Za-z]{5,}\b", raw_text)[:6]]))

        analysis_report = {
            "file_name": filename,
            "total_words": total_words,
            "generated_chunks": len(raw_chunks),
            "key_topics_detected": key_topics,
            "readiness": "Ready for semantic search and multi-agent synthesis",
            "first_chunk_preview": raw_chunks[0] if raw_chunks else ""
        }

        return {
            "status": "success",
            "analysis": analysis_report,
            "new_records": new_records
        }
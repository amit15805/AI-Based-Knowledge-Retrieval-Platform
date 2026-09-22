# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from app.config import settings

# class RetrievalAgent:
#     def __init__(self, data_path: str = "app/data/knowledge_store.json"):
#         self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
#         with open(data_path, "r") as f:
#             self.docs = json.load(f)
#         self.doc_embeddings = self.model.encode([d["content"] for d in self.docs])

#     def retrieve(self, query: str, top_k: int = 3) -> list:
#         q_emb = self.model.encode([query])
#         scores = cosine_similarity(q_emb, self.doc_embeddings)[0]

#         results = []
#         for idx, score in enumerate(scores):
#             if score >= settings.SIMILARITY_THRESHOLD:
#                 doc = self.docs[idx].copy()
#                 doc["score"] = round(float(score), 4)
#                 results.append(doc)

#         results.sort(key=lambda x: x["score"], reverse=True)
#         return results[:top_k]


import os
import chromadb
from typing import List
from app.models import RetrievedChunk

class RetrievalAgent:
    def __init__(self, persist_directory: str = "./chroma_db"):
        os.makedirs("uploads", exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(name="persistent_knowledge_base")

    def ingest_file(self, file_path: str, filename: str) -> int:
        # Simple text extraction & recursive chunking simulation
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # If it's a PDF or binary, basic fallback reader
        if not text.strip():
            text = f"Content extracted from binary/PDF file: {filename}"

        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        if not chunks:
            chunks = [filename]

        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        # Upsert into persistent ChromaDB
        self.collection.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 4, min_score: float = 0.2) -> List[RetrievedChunk]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
        except Exception:
            return []

        retrieved = []
        if not results or not results["documents"] or not results["documents"][0]:
            return retrieved

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[0.0] * len(documents)])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            score = round(max(0.0, 1.0 - (dist / 2.0)), 2)
            retrieved.append(
                RetrievedChunk(
                    text=doc,
                    source=meta.get("source", "Unknown PDF"),
                    chunk_index=meta.get("chunk_index", 0),
                    relevance_score=score
                )
            )
        return retrieved

    def list_documents(self) -> List[dict]:
        try:
            data = self.collection.get()
            meta_list = data.get("metadatas", [])
            doc_counts = {}
            for m in meta_list:
                src = m.get("source", "Unknown")
                doc_counts[src] = doc_counts.get(src, 0) + 1
            return [{"filename": k, "chunks": v} for k, v in doc_counts.items()]
        except Exception:
            return []
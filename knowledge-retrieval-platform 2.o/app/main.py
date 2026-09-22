# import os
# from fastapi import FastAPI, UploadFile, File
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from app.orchestrator import MultiAgentOrchestrator
# import google.generativeai as genai

# app = FastAPI(title="AI-Based Knowledge Retrieval Platform")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# orchestrator = MultiAgentOrchestrator()

# class QueryRequest(BaseModel):
#     session_id: str
#     query: str

# @app.post("/api/upload")
# async def upload_document(file: UploadFile = File(...)):
#     content = await file.read()
#     return orchestrator.process_file_upload(file.filename, content)

# @app.post("/api/resolve")
# async def resolve_query(req: QueryRequest):
#     return await orchestrator.execute(req.session_id, req.query)

# # Resolve absolute path to static folder regardless of where uvicorn is launched
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# STATIC_DIR = os.path.join(BASE_DIR, "static")

# # Explicit root route to ensure index.html always serves
# @app.get("/")
# async def read_index():
#     index_path = os.path.join(STATIC_DIR, "index.html")
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     return {"status": "error", "message": f"index.html not found at {index_path}"}

# # Mount the static directory
# if os.path.exists(STATIC_DIR):
#     app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.orchestrator import MultiAgentOrchestrator

app = FastAPI(title="OmniRAG Studio")
orchestrator = MultiAgentOrchestrator()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_index():
    return FileResponse("templates/index.html")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        chunks_count = orchestrator.ingest_document(file_path, file.filename)
        return {"filename": file.filename, "chunks_count": chunks_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
def get_documents():
    return {"documents": orchestrator.get_documents()}

@app.post("/api/query")
def query_endpoint(req: QueryRequest):
    try:
        result = orchestrator.process_query(req.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
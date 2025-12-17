import os
import shutil
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.pdf_service import process_pdf
from app.services.chat_service import get_answer

app = FastAPI()

# --- Database Setup ---
DB_NAME = "rag_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE)''')
    conn.commit()
    conn.close()

init_db()  # Run on startup

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "PDF RAG Backend is Running!"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. Save file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Process it (Vectorize)
        result = process_pdf(temp_path)
        
        # 3. Save filename to DB (Ignore if already exists)
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO documents (filename) VALUES (?)", (file.filename,))
            conn.commit()
            conn.close()
        except Exception as db_e:
            print(f"Database error: {db_e}")

        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/documents")
def get_documents():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row # Return dict-like objects
        c = conn.cursor()
        c.execute("SELECT filename FROM documents ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return {"documents": [row["filename"] for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        answer = get_answer(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import os
import shutil
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from app.services.pdf_service import process_pdf
from app.services.chat_service import get_answer
from pinecone import Pinecone

# --- Database Setup ---
DB_NAME = "rag_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Documents Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Messages Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized (Documents + Messages).")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    init_db()
    yield
    # Shutdown: (Cleanup if needed)

app = FastAPI(lifespan=lifespan)

def save_message(role: str, content: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]

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
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = process_pdf(temp_path)
        
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
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT filename FROM documents ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return {"documents": [row["filename"] for row in rows]}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    question = request.question
    
    # 1. Save USER message immediately
    save_message("user", question)

    try:
        # 2. Get answer from chat service
        answer = get_answer(question)
        
        # 3. Save ASSISTANT message before returning
        save_message("assistant", answer)

        return {"answer": answer}
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: Reset Endpoint ---
@app.delete("/reset")
def reset_knowledge_base():
    try:
        # 1. Clear SQLite (File List + History)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM documents")
        c.execute("DELETE FROM messages")
        conn.commit()
        conn.close()

        # 2. Clear Pinecone (Vector Memory)
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        index.delete(delete_all=True)

        return {"message": "Knowledge base cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/history")
async def get_history():
    return get_all_messages()
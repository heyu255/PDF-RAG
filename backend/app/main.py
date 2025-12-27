import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from app.services.pdf_service import process_pdf
from app.services.chat_service import get_answer
from pinecone import Pinecone
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()

# --- Database Setup ---
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
def save_message(role: str, content: str):
    data = {
        "role": role,
        "content": content,
    }
    supabase.table("messages").insert(data).execute()

def get_all_messages():

    response =supabase.table("messages").select("*").order("timestamp", desc=False).execute()
    return response.data
def clear_messages():
    supabase.table("messages").delete().neq("id", -1).execute()
def clear_documents():
    supabase.table("documents").delete().neq("id", -1).execute()
def clear_all():
    clear_messages()
    clear_documents()
    return {"message": "All data cleared successfully"}


app = FastAPI()

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
            supabase.table("documents").insert({
                "filename": file.filename,
                "timestamp": datetime.now().isoformat(),
            }).execute()
 
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
    response = supabase.table("documents").select("*").order("timestamp", desc=False).execute()
    return response.data

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
        # 1. Clear Supabase (File List + History)
        clear_all()

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
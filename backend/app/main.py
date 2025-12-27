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

    response =supabase.table("messages").select("*").order("created_at", desc=False).execute()
    return response.data
def clear_messages():
    supabase.table("messages").delete().neq("id", -1).execute()
def clear_documents():
    supabase.table("document").delete().neq("id", -1).execute()
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
        
        if supabase:
            try:
                supabase.table("document").insert({
                    "filename": file.filename,
                }).execute()
            except Exception as db_e:
                print(f"Supabase error (upload_pdf): {db_e}")
                # Don't fail the upload if Supabase fails, just log it

        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/documents")
def get_documents():
    if not supabase: return {"documents": []}
    try:
        response = supabase.table("document").select("filename").order("timestamp", desc=True).execute()
        return {"documents": [row["filename"] for row in response.data]}
    except Exception as e:
        print(f"Supabase error (get_documents): {e}")
        return {"documents": []}

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
        if supabase:
            clear_all()
        else:
            print("⚠️ Supabase not initialized, skipping database clear")

        # 2. Clear Pinecone (Vector Memory)
        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
            
            # Get current stats to see what we're deleting
            stats_before = index.describe_index_stats()
            print(f"📊 Pinecone stats before delete: {stats_before}")
            
            # Delete all vectors - try both methods to be safe
            # Method 1: delete_all (works for most cases)
            try:
                delete_response = index.delete(delete_all=True)
                print(f"✅ Pinecone delete_all response: {delete_response}")
            except Exception as e1:
                print(f"⚠️ delete_all failed, trying namespace delete: {e1}")
                # Method 2: Delete by namespace (if using namespaces)
                # LangChain PineconeVectorStore uses empty string "" as default namespace
                try:
                    index.delete(delete_all=True, namespace="")
                    print(f"✅ Pinecone namespace delete successful")
                except Exception as e2:
                    print(f"⚠️ Namespace delete also failed: {e2}")
                    # Method 3: Delete all namespaces
                    if hasattr(stats_before, 'namespaces'):
                        for ns in stats_before.namespaces.keys():
                            index.delete(delete_all=True, namespace=ns)
                            print(f"✅ Deleted namespace: {ns}")
            
            # Wait a moment for deletion to propagate
            import time
            time.sleep(1)
            
            # Verify deletion by checking stats
            stats_after = index.describe_index_stats()
            print(f"📊 Pinecone stats after delete: {stats_after}")
            
        except Exception as pinecone_error:
            print(f"❌ Pinecone delete error: {pinecone_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to clear Pinecone: {str(pinecone_error)}")

        return {"message": "Knowledge base cleared successfully"}
    except Exception as e:
        print(f"❌ Reset error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/history")
async def get_history():
    return get_all_messages()
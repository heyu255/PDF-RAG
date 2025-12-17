import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()

def process_pdf(file_path: str):
    print(f"--- Processing: {file_path} ---")
    
    # 1. Load the PDF
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages.")
    except Exception as e:
        print(f"Error loading PDF: {e}")
        raise e

    # 2. Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} text chunks.")

    # 3. Embed and store in Pinecone
    print("Starting upload to Pinecone...")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # This sends the data to your cloud database
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=os.getenv("PINECONE_INDEX_NAME")
    )
    
    print("--- Upload Complete ---")
    return {"status": "success", "chunks_processed": len(chunks)}
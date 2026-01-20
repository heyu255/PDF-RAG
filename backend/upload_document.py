"""
Helper script to upload PDF documents to the RAG system.
This populates Pinecone with document chunks for benchmarking.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
UPLOAD_ENDPOINT = f"{API_URL}/upload"

def upload_pdf(file_path: str):
    """
    Upload a PDF file to the RAG system.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Response from the server
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    if not file_path.lower().endswith('.pdf'):
        print(f"❌ File must be a PDF: {file_path}")
        return None
    
    print(f"📄 Uploading: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Processed {result.get('chunks_processed', 'unknown')} chunks")
                return result
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {API_URL}")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

def upload_multiple_pdfs(directory: str):
    """
    Upload all PDF files from a directory.
    
    Args:
        directory: Directory containing PDF files
    """
    pdf_files = list(Path(directory).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {directory}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s)")
    
    for pdf_file in pdf_files:
        upload_pdf(str(pdf_file))
        print()  # Empty line between uploads

def main():
    """Main function with command-line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python upload_document.py <path_to_pdf>")
        print("  python upload_document.py --dir <directory_with_pdfs>")
        print()
        print("Examples:")
        print("  python upload_document.py document.pdf")
        print("  python upload_document.py --dir ./documents")
        return
    
    if sys.argv[1] == "--dir" and len(sys.argv) > 2:
        upload_multiple_pdfs(sys.argv[2])
    else:
        upload_pdf(sys.argv[1])

if __name__ == "__main__":
    main()


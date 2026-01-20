
# PDF-RAG AI: Enterprise Knowledge Retrieval System
https://pdf-rag-ruddy.vercel.app/

A full-stack **Retrieval-Augmented Generation (RAG)** application that transforms static PDF documents into a searchable, interactive knowledge base. Unlike standard LLM uploads, this system utilizes a vector database to handle unlimited document scale with enterprise-grade privacy.

## 🛠️ The "Hybrid" Tech Stack

* **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS.
* **AI Backend:** Python (FastAPI), LangChain.
* **Vector Database:** Pinecone (Semantic Search).
* **Metadata Database:** SQLite (Relational metadata tracking).
* **LLM:** OpenAI GPT-4o-mini via API.
* **Data Engineering:** PyPDF for extraction and Recursive Character Text Splitting for chunking.

---

## 🏗️ Technical Architecture

### **1. The RAG Pipeline (ETL)**

* **Ingestion:** Documents are parsed and broken into semantic "chunks" to maintain context.
* **Embedding:** Chunks are converted into 1536-dimensional vectors using OpenAI `text-embedding-3-small`.
* **Vector Storage:** Embeddings are indexed in **Pinecone** for sub-second similarity searches.

### **2. Hybrid Storage Design**

To optimize performance and cost, I implemented a split-storage strategy:

* **Vector Store (Pinecone):** Handles high-dimensional math for semantic "meaning" search.
* **Relational Store (SQLite):** Handles high-speed metadata retrieval (filenames, timestamps) for the UI sidebar, reducing Vector DB API overhead.

### **3. Stateless Processing**

The backend is designed to be lightweight and "stateless." Files are processed in-memory and transiently; the system extracts the "knowledge" into the vector space and discards the physical file to ensure data security and storage efficiency.

---

## 💡 Why this is superior to ChatGPT uploads:

| Feature | My RAG Application | Standard GPT Upload |
| --- | --- | --- |
| **Scale** | Unlimited (Library-scale) | Limited by Context Window (~10 files) |
| **Privacy** | Zero Data Training (API Policy) | Data potentially used for training |
| **Integrity** | Hallucination control via System Prompts | Prone to using outside knowledge |
| **Architecture** | Custom API Integration (White Label) | Closed Ecosystem (Web UI only) |

---

## 🚀 Getting Started

### **Prerequisites**

* Node.js 18+ & Python 3.9+
* OpenAI API Key
* Pinecone API Key & Environment

### **Installation**

1. **Clone the Repository**
```bash
[git clone https://github.com/your-username/pdf-rag-ai.git](https://github.com/heyu255/PDF-RAG.git)

```


2. **Setup FastAPI Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

```


3. **Setup Next.js Frontend**
```bash
cd frontend
npm install
npm run dev

```


4. **Environment Variables**
Configure `.env` files in both directories with your `OPENAI_API_KEY` and `PINECONE_API_KEY`.

---

## 🛡️ Key Challenges Solved

* **System-Level Debugging:** Diagnosed and resolved a critical 32-bit vs 64-bit Node.js architecture mismatch that caused SWC compiler crashes during deployment.
* **Cross-Origin Security:** Implemented secure CORS policies between the FastAPI AI service and the Next.js frontend.
* **Context Optimization:** Fine-tuned chunk sizes and "K-nearest neighbor" (Top-K) retrieval settings to balance answer accuracy with token cost.

---

## 📄 License

This project is open-source under the MIT License.

---



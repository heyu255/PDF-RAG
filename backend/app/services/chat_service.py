import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def get_answer(question: str):
    # 1. Connect to Pinecone
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vector_store = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embeddings
    )
    
    # 2. Connect to GPT
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # 3. Create the Search Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    
    # 4. Ask the question
    # IMPORTANT: This syntax {"query": ...} is required for this version
    response = qa_chain.invoke({"query": question})
    
    return response["result"]
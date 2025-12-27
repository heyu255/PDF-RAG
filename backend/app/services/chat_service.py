import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
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
    
    # 3. Create the prompt template
    prompt = ChatPromptTemplate.from_template(
        """Answer the following question based only on the provided context:

Context: {context}

Question: {input}"""
    )
    
    # 4. Create the document chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    
    # 5. Create the retrieval chain
    retriever = vector_store.as_retriever()
    qa_chain = create_retrieval_chain(retriever, document_chain)
    
    # 6. Ask the question
    response = qa_chain.invoke({"input": question})
    
    return response["answer"]
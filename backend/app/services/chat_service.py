import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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
    
    # 4. Create the retriever
    retriever = vector_store.as_retriever()
    
    # 5. Create the RAG chain using the new LCEL (LangChain Expression Language) pattern
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 6. Ask the question
    response = rag_chain.invoke(question)
    
    return response
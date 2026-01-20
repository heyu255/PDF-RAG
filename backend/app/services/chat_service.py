import os
import time
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv

load_dotenv()

class TokenUsageCallback(BaseCallbackHandler):
    """Callback to track token usage from OpenAI API"""
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
    
    def on_llm_end(self, response, **kwargs):
        """Capture token usage from LLM response"""
        # Try different ways to get token usage depending on LangChain version
        if hasattr(response, 'response_metadata'):
            token_usage = response.response_metadata.get('token_usage', {})
            if token_usage:
                self.input_tokens += token_usage.get('prompt_tokens', 0)
                self.output_tokens += token_usage.get('completion_tokens', 0)
        elif hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                self.input_tokens += token_usage.get('prompt_tokens', 0)
                self.output_tokens += token_usage.get('completion_tokens', 0)
    
    def get_usage(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens
        }

def get_answer(question: str, track_metrics: bool = False):
    """
    Get answer using RAG pipeline
    
    Args:
        question: User question
        track_metrics: If True, returns metrics along with answer
    
    Returns:
        answer (str) or tuple (answer, metrics_dict) if track_metrics=True
    """
    # Initialize callback for token tracking
    callback = TokenUsageCallback() if track_metrics else None
    callbacks = [callback] if callback else None
    
    # 1. Connect to Pinecone
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vector_store = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embeddings
    )
    
    # 2. Connect to GPT
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        callbacks=callbacks
    )
    
    # 3. Create the prompt template
    prompt = ChatPromptTemplate.from_template(
        """Answer the following question based only on the provided context:

Context: {context}

Question: {input}"""
    )
    
    # 4. Create the retriever with explicit k value
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}  # Retrieve top 4 most relevant chunks
    )
    
    # 5. Create the RAG chain using the new LCEL (LangChain Expression Language) pattern
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Time the retrieval
    retrieval_start = time.time()
    retrieved_docs = retriever.invoke(question)
    retrieval_time = time.time() - retrieval_start
    
    # Format context
    context = format_docs(retrieved_docs)
    
    # Time the LLM call
    llm_start = time.time()
    rag_chain = (
        {"context": RunnablePassthrough(), "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    response = rag_chain.invoke({"context": context, "input": question})
    llm_time = time.time() - llm_start
    
    if track_metrics:
        # Get token usage from callback if available
        if callback:
            token_usage = callback.get_usage()
            input_tokens = token_usage["input_tokens"]
            output_tokens = token_usage["output_tokens"]
        else:
            # Fallback: Estimate tokens (roughly 4 characters per token)
            # Input: context + question + prompt template
            input_text = context + question + "Answer the following question based only on the provided context:\n\nContext:\n\nQuestion:"
            input_tokens = len(input_text) // 4
            # Output: response
            output_tokens = len(response) // 4
        
        metrics = {
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "tokens_total": input_tokens + output_tokens,
            "retrieval_time_seconds": retrieval_time,
            "llm_time_seconds": llm_time,
            "total_time_seconds": retrieval_time + llm_time,
            "chunks_retrieved": len(retrieved_docs)
        }
        return response, metrics
    
    return response
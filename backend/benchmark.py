"""
Benchmark script to compare RAG vs non-RAG token usage and performance.

This script helps quantify the improvements:
1. Token consumption reduction
2. Response quality (context grounding)
3. Latency measurements
"""

import os
import time
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.chat_service import get_answer

load_dotenv()

# Sample questions for benchmarking
TEST_QUESTIONS = [
    "What is the main topic discussed in the documents?",
    "Summarize the key points from the uploaded documents.",
    "What are the most important details mentioned?",
    "Can you explain the concepts covered in the documents?",
    "What information is available about the subject matter?",
]

def benchmark_rag(questions: list):
    """Benchmark RAG approach (with retrieval)"""
    print("\n=== Benchmarking RAG Approach ===")
    results = []
    total_tokens = 0
    total_time = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Processing: {question[:50]}...")
        
        start = time.time()
        answer, metrics = get_answer(question, track_metrics=True)
        elapsed = time.time() - start
        
        result = {
            "question": question,
            "answer_length": len(answer),
            "tokens_input": metrics["tokens_input"],
            "tokens_output": metrics["tokens_output"],
            "tokens_total": metrics["tokens_total"],
            "retrieval_time_ms": metrics["retrieval_time_seconds"] * 1000,
            "llm_time_ms": metrics["llm_time_seconds"] * 1000,
            "total_time_ms": metrics["total_time_seconds"] * 1000,
            "chunks_retrieved": metrics["chunks_retrieved"]
        }
        
        results.append(result)
        total_tokens += metrics["tokens_total"]
        total_time += metrics["total_time_seconds"]
        
        print(f"  Tokens: {metrics['tokens_total']} (Input: {metrics['tokens_input']}, Output: {metrics['tokens_output']})")
        print(f"  Time: {metrics['total_time_seconds']*1000:.2f}ms (Retrieval: {metrics['retrieval_time_seconds']*1000:.2f}ms, LLM: {metrics['llm_time_seconds']*1000:.2f}ms)")
    
    avg_tokens = total_tokens / len(questions)
    avg_time = total_time / len(questions)
    
    return {
        "approach": "RAG",
        "results": results,
        "summary": {
            "total_queries": len(questions),
            "total_tokens": total_tokens,
            "avg_tokens_per_query": avg_tokens,
            "avg_time_ms": avg_time * 1000,
            "total_time_seconds": total_time
        }
    }

def benchmark_non_rag(questions: list, context_size_estimate: int = 50000):
    """
    Benchmark non-RAG approach (full context window).
    
    Note: This simulates what would happen if you sent entire documents
    to the LLM without RAG. We estimate token usage based on context size.
    """
    print("\n=== Benchmarking Non-RAG Approach (Simulated) ===")
    print("Note: This simulates sending full documents to LLM context window")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Estimate tokens: ~4 characters per token
    estimated_input_tokens = context_size_estimate // 4
    
    results = []
    total_tokens = 0
    total_time = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Processing: {question[:50]}...")
        
        # Simulate prompt with full context
        prompt = ChatPromptTemplate.from_template(
            """You have access to a large document. Answer the following question based on the document content.

Question: {input}

Note: In a real non-RAG system, the entire document would be in the context here."""
        )
        
        start = time.time()
        chain = prompt | llm
        response = chain.invoke({"input": question})
        elapsed = time.time() - start
        
        # Estimate output tokens (roughly 1 token per 4 characters)
        answer_text = response.content if hasattr(response, 'content') else str(response)
        estimated_output_tokens = len(answer_text) // 4
        
        # In reality, LLM would process full context, so input tokens would be much higher
        # We simulate this by using the estimated context size
        result = {
            "question": question,
            "answer_length": len(answer_text),
            "tokens_input": estimated_input_tokens,  # Full document context
            "tokens_output": estimated_output_tokens,
            "tokens_total": estimated_input_tokens + estimated_output_tokens,
            "llm_time_ms": elapsed * 1000,
            "total_time_ms": elapsed * 1000,
            "chunks_retrieved": 0  # No retrieval in non-RAG
        }
        
        results.append(result)
        total_tokens += result["tokens_total"]
        total_time += elapsed
        
        print(f"  Tokens: {result['tokens_total']} (Input: {result['tokens_input']}, Output: {result['tokens_output']})")
        print(f"  Time: {elapsed*1000:.2f}ms")
    
    avg_tokens = total_tokens / len(questions)
    avg_time = total_time / len(questions)
    
    return {
        "approach": "Non-RAG (Full Context)",
        "results": results,
        "summary": {
            "total_queries": len(questions),
            "total_tokens": total_tokens,
            "avg_tokens_per_query": avg_tokens,
            "avg_time_ms": avg_time * 1000,
            "total_time_seconds": total_time
        }
    }

def calculate_improvements(rag_results: dict, non_rag_results: dict):
    """Calculate improvement percentages"""
    rag_avg_tokens = rag_results["summary"]["avg_tokens_per_query"]
    non_rag_avg_tokens = non_rag_results["summary"]["avg_tokens_per_query"]
    
    token_reduction = ((non_rag_avg_tokens - rag_avg_tokens) / non_rag_avg_tokens) * 100
    
    rag_avg_time = rag_results["summary"]["avg_time_ms"]
    non_rag_avg_time = non_rag_results["summary"]["avg_time_ms"]
    
    time_comparison = {
        "rag_avg_ms": rag_avg_time,
        "non_rag_avg_ms": non_rag_avg_time,
        "difference_ms": non_rag_avg_time - rag_avg_time
    }
    
    return {
        "token_reduction_percent": round(token_reduction, 2),
        "tokens_saved_per_query": round(non_rag_avg_tokens - rag_avg_tokens, 2),
        "rag_avg_tokens": round(rag_avg_tokens, 2),
        "non_rag_avg_tokens": round(non_rag_avg_tokens, 2),
        "time_comparison": time_comparison
    }

def main():
    print("=" * 60)
    print("RAG vs Non-RAG Benchmark")
    print("=" * 60)
    
    # Run benchmarks
    rag_results = benchmark_rag(TEST_QUESTIONS)
    non_rag_results = benchmark_non_rag(TEST_QUESTIONS)
    
    # Calculate improvements
    improvements = calculate_improvements(rag_results, non_rag_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"\nToken Usage:")
    print(f"  RAG Average: {improvements['rag_avg_tokens']:.2f} tokens/query")
    print(f"  Non-RAG Average: {improvements['non_rag_avg_tokens']:.2f} tokens/query")
    print(f"  Reduction: {improvements['token_reduction_percent']:.2f}%")
    print(f"  Tokens Saved: {improvements['tokens_saved_per_query']:.2f} tokens/query")
    
    print(f"\nLatency:")
    print(f"  RAG Average: {improvements['time_comparison']['rag_avg_ms']:.2f}ms")
    print(f"  Non-RAG Average: {improvements['time_comparison']['non_rag_avg_ms']:.2f}ms")
    
    # Save results
    output = {
        "rag_results": rag_results,
        "non_rag_results": non_rag_results,
        "improvements": improvements,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to benchmark_results.json")
    print(f"\n📊 Key Metric: {improvements['token_reduction_percent']:.2f}% token reduction with RAG")

if __name__ == "__main__":
    main()


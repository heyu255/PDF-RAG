import time
from typing import Dict, Optional
from datetime import datetime
import json

class MetricsCollector:
    """Collects performance metrics for RAG operations"""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_retrieval_time": 0.0,
            "total_llm_time": 0.0,
            "total_metadata_time": 0.0,
            "queries": []
        }
    
    def record_query(
        self,
        question: str,
        tokens_input: int,
        tokens_output: int,
        retrieval_time: float,
        llm_time: float,
        metadata_time: Optional[float] = None,
        chunks_retrieved: Optional[int] = None
    ):
        """Record metrics for a single query"""
        self.metrics["total_queries"] += 1
        self.metrics["total_tokens_input"] += tokens_input
        self.metrics["total_tokens_output"] += tokens_output
        self.metrics["total_retrieval_time"] += retrieval_time
        self.metrics["total_llm_time"] += llm_time
        
        if metadata_time:
            self.metrics["total_metadata_time"] += metadata_time
        
        query_metric = {
            "timestamp": datetime.now().isoformat(),
            "question": question[:100],  # Truncate for storage
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "total_tokens": tokens_input + tokens_output,
            "retrieval_time_ms": round(retrieval_time * 1000, 2),
            "llm_time_ms": round(llm_time * 1000, 2),
            "total_time_ms": round((retrieval_time + llm_time) * 1000, 2),
            "chunks_retrieved": chunks_retrieved
        }
        
        if metadata_time:
            query_metric["metadata_time_ms"] = round(metadata_time * 1000, 2)
        
        self.metrics["queries"].append(query_metric)
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if self.metrics["total_queries"] == 0:
            return {"error": "No queries recorded"}
        
        avg_tokens_input = self.metrics["total_tokens_input"] / self.metrics["total_queries"]
        avg_tokens_output = self.metrics["total_tokens_output"] / self.metrics["total_queries"]
        avg_retrieval_time = self.metrics["total_retrieval_time"] / self.metrics["total_queries"]
        avg_llm_time = self.metrics["total_llm_time"] / self.metrics["total_queries"]
        
        summary = {
            "total_queries": self.metrics["total_queries"],
            "total_tokens_input": self.metrics["total_tokens_input"],
            "total_tokens_output": self.metrics["total_tokens_output"],
            "total_tokens": self.metrics["total_tokens_input"] + self.metrics["total_tokens_output"],
            "avg_tokens_per_query": round(avg_tokens_input + avg_tokens_output, 2),
            "avg_retrieval_time_ms": round(avg_retrieval_time * 1000, 2),
            "avg_llm_time_ms": round(avg_llm_time * 1000, 2),
            "avg_total_time_ms": round((avg_retrieval_time + avg_llm_time) * 1000, 2)
        }
        
        if self.metrics["total_metadata_time"] > 0:
            avg_metadata_time = self.metrics["total_metadata_time"] / self.metrics["total_queries"]
            summary["avg_metadata_time_ms"] = round(avg_metadata_time * 1000, 2)
        
        return summary
    
    def export_metrics(self, filepath: str = "metrics.json"):
        """Export metrics to JSON file"""
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)
        return filepath

# Global metrics collector instance
metrics_collector = MetricsCollector()


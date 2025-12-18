from typing import List, Dict, Any, Union
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RetrievalEvaluator:
    """
    Evaluates the performance of a QueryEngine against a Golden Dataset.
    Calculates Hit Rate and Mean Reciprocal Rank (MRR).
    """

    def __init__(self, query_engine):
        """
        Args:
            query_engine: An instance (or mock) of QueryEngine with a .query() method.
        """
        self.query_engine = query_engine

    def evaluate(self, dataset: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, float]:
        """
        Runs evaluation over the provided dataset.

        Args:
            dataset: A list of ground truth items. Each item must have:
                     - "question": str
                     - "ground_truth_context_files": List[str] filenames
            top_k: Number of results to retrieve per query.

        Returns:
            Dict with "hit_rate" and "mrr".
        """
        total_queries = len(dataset)
        if total_queries == 0:
            return {"hit_rate": 0.0, "mrr": 0.0}

        hits = 0
        reciprocal_ranks = 0.0

        for item in dataset:
            question = item["question"]
            gold_files = set(item.get("ground_truth_context_files", []))
            
            # Execute Query
            # Expecting response format: {"results": [Document, ...]}
            response = self.query_engine.query(question, top_k=top_k)
            retrieved_docs = response.get("results", [])

            # Check for matches
            is_hit = False
            rank = 0
            
            for i, doc in enumerate(retrieved_docs):
                # Rank is 1-indexed
                current_rank = i + 1
                
                # Extract filename from "source" metadata
                # Handle cases where source might be a full path
                metadata = doc.get("metadata", {})
                source_path = metadata.get("source", "")
                filename = Path(source_path).name
                
                # Check if this file is in our ground truth list
                if filename in gold_files:
                    is_hit = True
                    rank = current_rank
                    break # Found the first relevant doc (for MRR)
            
            if is_hit:
                hits += 1
                reciprocal_ranks += (1.0 / rank)
        
        hit_rate = hits / total_queries
        mrr = reciprocal_ranks / total_queries
        
        logger.info(f"Evaluation Complete. Processed {total_queries} queries.")
        logger.info(f"Hit Rate: {hit_rate:.4f} | MRR: {mrr:.4f}")

        return {
            "hit_rate": hit_rate,
            "mrr": mrr
        }

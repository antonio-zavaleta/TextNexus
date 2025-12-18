
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
from .judges import BaseJudge

class GenerationEvaluator:
    """
    Evaluates the generation quality of a RAG pipeline using LLM-as-a-judge.
    """
    
    def __init__(self, query_engine: Any, llm_judge: BaseJudge):
        """
        Args:
            query_engine: Object with a `query(question) -> (context, answer)` method.
            llm_judge: Instance of BaseJudge to evaluate answers.
        """
        self.query_engine = query_engine
        self.llm_judge = llm_judge

    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Run evaluation on the provided dataset.
        
        Args:
            dataset: List of dicts containing "question" and "ground_truth_answer".
            
        Returns:
            Dictionary with average "faithfulness" and "answer_correctness".
        """
        results = {
            "faithfulness": [],
            "answer_correctness": []
        }
        
        for item in tqdm(dataset, desc="Evaluating Generation"):
            question = item.get("question")
            ground_truth = item.get("ground_truth_answer")
            
            if not question or not ground_truth:
                continue
                
            # Query the engine
            # Expecting (context_str, answer_str)
            try:
                context, answer = self.query_engine.query(question)
            except Exception as e:
                print(f"Error querying engine for '{question}': {e}")
                continue
                
            # Evaluate
            faith_score = self.llm_judge.check_faithfulness(context, answer)
            correct_score = self.llm_judge.check_correctness(answer, ground_truth)
            
            results["faithfulness"].append(faith_score)
            results["answer_correctness"].append(correct_score)
            
        # Calculate averages
        avg_faith = sum(results["faithfulness"]) / len(results["faithfulness"]) if results["faithfulness"] else 0.0
        avg_correct = sum(results["answer_correctness"]) / len(results["answer_correctness"]) if results["answer_correctness"] else 0.0
        
        return {
            "faithfulness": avg_faith,
            "answer_correctness": avg_correct,
            "total_samples": len(results["faithfulness"])
        }


import sys
import os
import time
import argparse

# Add project root to path
sys.path.append(os.getcwd())

from textnexus.evaluation.generation import GenerationEvaluator
from textnexus.evaluation.judges import OllamaJudge, OpenAIJudge, GeminiJudge

# Mock Generator that acts like a RAG pipeline
class MockQueryEngine:
    def __init__(self):
        pass
        
    def query(self, question: str):
        # Return hardcoded (context, answer) based on question content
        # We'll use the questions from ground_truth.json
        
        question_lower = question.lower()
        
        if "transformer" in question_lower:
            # Correct answer
            return (
                "The Transformer is based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                "The Transformer is a model architecture based solely on attention mechanisms, dispensing with recurrence and convolutions."
            )
        elif "attention" in question_lower:
            # Vague/Partial answer
            return (
                "Attention mechanisms have become an integral part of compelling sequence modeling.",
                "Attention is important."
            )
        elif "figure 1" in question_lower:
             # Hallucinated answer
            return (
                "Figure 1 shows the model architecture.",
                "Figure 1 shows a picture of a cat."
            )
        else:
            # Default generic
            return (
                "This is some generic context.",
                "This is a generic answer."
            )

def main():
    parser = argparse.ArgumentParser(description="Verify Generation Evaluator")
    parser.add_argument("--judge", type=str, default="ollama", choices=["ollama", "openai", "gemini"], help="LLM Judge to use")
    parser.add_argument("--model", type=str, help="Specific model name (optional)")
    args = parser.parse_args()

    print(f">>> Verifying C.3: Generation Evaluator with {args.judge.title()} Judge")
    
    judge = None
    
    # 1. Setup Judge
    if args.judge == "ollama":
        # Check if Ollama is reachable
        try:
            import ollama
            client = ollama.Client()
            client.list()
            print(">>> Ollama connection successful.")
        except Exception as e:
            print(f">>> WARNING: Ollama not reachable ({e}). Evaluation might fail or return 0s.")
            print(">>> Ensure `ollama serve` is running and `llama3` module is pulled.")
            
        model = args.model or "llama3"
        print(f">>> Initializing OllamaJudge with model='{model}'...")
        judge = OllamaJudge(model_name=model)
        
    elif args.judge == "openai":
        if "OPENAI_API_KEY" not in os.environ:
            print(">>> ERROR: OPENAI_API_KEY environment variable not set.")
            return
        model = args.model or "gpt-4o"
        print(f">>> Initializing OpenAIJudge with model='{model}'...")
        judge = OpenAIJudge(model_name=model)
        
    elif args.judge == "gemini":
        print(">>> WARNING: Gemini Judge is temporarily disabled due to API 404 errors.")
        print(">>> TODO: Fix 'NotFound: 404 models/gemini-pro is not found for API version v1beta'")
        return
        
        # Support GEMINI_API_KEY as alias due to user preference/env
        # if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
        #     os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
        #
        # if "GOOGLE_API_KEY" not in os.environ:
        #     print(">>> ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable not set.")
        #     return
        # model = args.model or "gemini-pro"
        # print(f">>> Initializing GeminiJudge with model='{model}'...")
        # judge = GeminiJudge(model_name=model)
        
    if not judge:
        print(">>> ERROR: Could not initialize judge.")
        return
    
    # 2. Setup Mock Query Engine
    print(">>> Initializing MockQueryEngine...")
    query_engine = MockQueryEngine()
    
    # 3. Create Evaluator
    evaluator = GenerationEvaluator(query_engine, judge)
    
    # 4. Create a small manual dataset for verification
    # We use questions that trigger our MockQueryEngine logic
    dataset = [
        {
            "question": "What is the Transformer based on?",
            "ground_truth_answer": "The Transformer is based solely on attention mechanisms."
        },
        {
            "question": "What does Figure 1 show?",
            "ground_truth_answer": "Figure 1 shows the Transformer model architecture."
        }
    ]
    
    print(f">>> Starting evaluation on {len(dataset)} items...")
    
    results = evaluator.evaluate(dataset)
    
    print("\n>>> Evaluation Results:")
    print(f"Faithfulness: {results['faithfulness']:.2f}")
    print(f"Answer Correctness: {results['answer_correctness']:.2f}")
    print(f"Total Samples: {results['total_samples']}")
    
    print("\n>>> Interpretation:")
    print("1. Transformer Question: Should be High Faithfulness, High Correctness.")
    print("2. Figure 1 Question: Should be Low Faithfulness (Hallucinated 'cat'), Low Correctness.")
    
if __name__ == "__main__":
    main()

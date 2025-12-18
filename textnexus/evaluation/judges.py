
from abc import ABC, abstractmethod
import re
from typing import Optional

class BaseJudge(ABC):
    """Abstract base class for LLM judges."""
    
    @abstractmethod
    def check_faithfulness(self, context: str, answer: str) -> float:
        pass

    @abstractmethod
    def check_correctness(self, answer: str, ground_truth: str) -> float:
        pass

    def _parse_score(self, response: str) -> float:
        """Extract a score (0-1) from the LLM response."""
        match = re.search(r"(\d+(\.\d+)?)", response)
        if match:
            try:
                score = float(match.group(1))
                if score > 1.0:
                    score = score / 10.0
                return min(max(score, 0.0), 1.0)
            except ValueError:
                return 0.0
        return 0.0

    def _get_faithfulness_prompt(self, context: str, answer: str) -> str:
        return f"""
        You are an impartial judge evaluating the faithfulness of an answer to a given context.
        
        CONTEXT:
        {context}
        
        ANSWER:
        {answer}
        
        Task: rate whether the provided answer is logically derived from the context. 
        It does not need to be the full content, but it cannot contain information NOT in the context (hallucinations).
        
        Respond ONLY with a score between 0.0 (Hallucinated) and 1.0 (Reflected in context).
        Do not add explanation.
        """

    def _get_correctness_prompt(self, answer: str, ground_truth: str) -> str:
        return f"""
        You are an impartial judge evaluating the correctness of an answer compared to a ground truth.
        
        GROUND TRUTH:
        {ground_truth}
        
        ANSWER:
        {answer}
        
        Task: rate whether the answer conveys the same meaning and facts as the ground truth.
        
        Respond ONLY with a score between 0.0 (Wrong) and 1.0 (Correct).
        Do not add explanation.
        """

class OllamaJudge(BaseJudge):
    def __init__(self, model_name: str = "llama3", host: str = None):
        self.model_name = model_name
        try:
            from ollama import Client
            self.client = Client(host=host)
        except ImportError:
            raise ImportError("Ollama package not found. Please install with `poetry add ollama`.")

    def check_faithfulness(self, context: str, answer: str) -> float:
        prompt = self._get_faithfulness_prompt(context, answer)
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return self._parse_score(response['message']['content'])
        except Exception as e:
            print(f"Error in faithfulness check: {e}")
            return 0.0

    def check_correctness(self, answer: str, ground_truth: str) -> float:
        prompt = self._get_correctness_prompt(answer, ground_truth)
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return self._parse_score(response['message']['content'])
        except Exception as e:
            print(f"Error in correctness check: {e}")
            return 0.0

class OpenAIJudge(BaseJudge):
    """Judge using OpenAI API (requires langchain-openai)."""
    def __init__(self, model_name: str = "gpt-4o"):
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        except ImportError:
            raise ImportError("langchain-openai not found.")

    def check_faithfulness(self, context: str, answer: str) -> float:
        prompt = self._get_faithfulness_prompt(context, answer)
        try:
            response = self.llm.invoke(prompt)
            # Response is typically AIMessage
            return self._parse_score(response.content)
        except Exception as e:
            print(f"Error in faithfulness check (OpenAI): {e}")
            return 0.0

    def check_correctness(self, answer: str, ground_truth: str) -> float:
        prompt = self._get_correctness_prompt(answer, ground_truth)
        try:
            response = self.llm.invoke(prompt)
            return self._parse_score(response.content)
        except Exception as e:
            print(f"Error in correctness check (OpenAI): {e}")
            return 0.0

class GeminiJudge(BaseJudge):
    """Judge using Google Gemini API (requires langchain-google-genai)."""
    def __init__(self, model_name: str = "gemini-pro"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0)
        except ImportError:
            raise ImportError("langchain-google-genai not found.")

    def check_faithfulness(self, context: str, answer: str) -> float:
        prompt = self._get_faithfulness_prompt(context, answer)
        try:
            response = self.llm.invoke(prompt)
            return self._parse_score(response.content)
        except Exception as e:
            print(f"Error in faithfulness check (Gemini): {e}")
            return 0.0

    def check_correctness(self, answer: str, ground_truth: str) -> float:
        prompt = self._get_correctness_prompt(answer, ground_truth)
        try:
            response = self.llm.invoke(prompt)
            return self._parse_score(response.content)
        except Exception as e:
            print(f"Error in correctness check (Gemini): {e}")
            return 0.0

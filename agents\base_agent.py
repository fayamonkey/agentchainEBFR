from abc import ABC, abstractmethod
import os
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the base agent with the specified model."""
        self.model_name = model_name
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Abstract method that each agent must implement."""
        pass
    
    def _get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from OpenAI API."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return "" 
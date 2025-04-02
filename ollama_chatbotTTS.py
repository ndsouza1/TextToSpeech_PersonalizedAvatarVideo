import ollama
import json

from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str

class OllamaChat:
    response: str

    def __init__(self):
        """Initialize the Ollama model."""
        self.model = "deepseek-r1:7b"
        self.system_prompt="You are a concise and natural-sounding assistant.Answer questions briefly, in one or two sentences at most, as if responding for text-to-speech (TTS). Keep it natural and conversational"

    def get_response(self, user_input):
        """Processes the input text using Ollama and returns only the response string."""
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}],
            format=ChatResponse.model_json_schema()
        )
        
        response = json.loads(response["message"]["content"])["response"]
        return response


# Usage Example
""" if __name__ == "__main__":
    ollama_chat = OllamaChat()
    
    user_text = input("Enter your question: ")  # Take user input
    output_text = ollama_chat.get_response(user_text)

    print("\nOllama Response:\n", output_text)
 """
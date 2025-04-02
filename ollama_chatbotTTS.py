import ollama

class OllamaChat:
    def __init__(self, model="deepseek-r1:7b"):
        """Initialize the Ollama model."""
        self.model = model

    def get_response(self, user_input):
        """Processes the input text using Ollama and returns only the response string."""
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": user_input}]
        )
        
        return response["message"]["content"]


# Usage Example
""" if __name__ == "__main__":
    ollama_chat = OllamaChat()
    
    user_text = input("Enter your question: ")  # Take user input
    output_text = ollama_chat.get_response(user_text)

    print("\nOllama Response:\n", output_text)
 """
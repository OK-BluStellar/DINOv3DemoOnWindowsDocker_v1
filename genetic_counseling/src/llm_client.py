import ollama
from typing import List, Dict, Any, Optional


class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.client = ollama.Client(host=base_url)
        self.conversation_history: List[Dict[str, str]] = []
    
    def chat(self, user_message: str, system_prompt: str, 
             model_name: str, temperature: float = 0.7, 
             max_tokens: int = 2048, top_p: float = 0.9) -> str:
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_history
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": top_p
                }
            )
            
            assistant_message = response['message']['content']
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            return error_msg
    
    def reset_conversation(self):
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history
    
    def list_available_models(self) -> List[str]:
        try:
            models = self.client.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

"""
Open WebUI AI Client
Connects to your Open WebUI instance to get AI responses.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIClient:
    """Client for Open WebUI API using OpenAI-compatible interface."""
    
    def __init__(self, model: str = None):
        self.api_key = os.environ.get("OPENWEBUI_API_KEY")
        self.base_url = os.environ.get("OPENWEBUI_BASE_URL", "http://localhost:3002/api")
        self.model = model or os.environ.get("AI_MODEL", "haiku-4.5")
        
        if not self.api_key:
            raise ValueError("OPENWEBUI_API_KEY environment variable not set")
        
        # Initialize OpenAI client pointing to Open WebUI
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        
        # Conversation history per room (room_id -> messages list)
        self.conversations = {}
    
    def chat(self, message: str, room_id: str = None, system_prompt: str = None) -> str:
        """
        Send a message and get an AI response.
        
        Args:
            message: The user's message
            room_id: Optional room ID to maintain conversation history
            system_prompt: Optional system prompt to set AI behavior
            
        Returns:
            The AI's response text
        """
        # Build messages list
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if we're tracking a room
        if room_id and room_id in self.conversations:
            messages.extend(self.conversations[room_id])
        
        # Add the new user message
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
            )
            
            assistant_message = response.choices[0].message.content
            
            # Store in conversation history if tracking
            if room_id:
                if room_id not in self.conversations:
                    self.conversations[room_id] = []
                self.conversations[room_id].append({"role": "user", "content": message})
                self.conversations[room_id].append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 20 messages to avoid token limits
                if len(self.conversations[room_id]) > 20:
                    self.conversations[room_id] = self.conversations[room_id][-20:]
            
            return assistant_message
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def clear_history(self, room_id: str):
        """Clear conversation history for a room."""
        if room_id in self.conversations:
            del self.conversations[room_id]
    
    def list_models(self):
        """List available models from Open WebUI."""
        try:
            models = self.client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            return [f"Error listing models: {e}"]


if __name__ == "__main__":
    # Quick test
    client = AIClient()
    print("Available models:", client.list_models())
    print("\nTest response:")
    response = client.chat("Hello! What's 2+2?")
    print(response)

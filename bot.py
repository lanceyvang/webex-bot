"""
Webex Bot - AI-Powered Chat Bot
Connects to Open WebUI for AI responses.
"""
import os
from dotenv import load_dotenv
from webexteamssdk import WebexTeamsAPI
from ai_client import AIClient

load_dotenv()

# Initialize APIs
webex = WebexTeamsAPI(access_token=os.environ.get("WEBEX_BOT_TOKEN"))
ai = AIClient()

# Get bot's own identity to avoid responding to itself
BOT_ID = os.environ.get("WEBEX_BOT_ID")
bot_info = webex.people.me()
BOT_EMAIL = bot_info.emails[0] if bot_info.emails else None

# System prompt for the AI
SYSTEM_PROMPT = """You are a helpful AI assistant in a Webex chat. 
Be concise but friendly. Format responses nicely for chat - use short paragraphs.
If you don't know something, say so honestly."""


def process_message(message_id: str):
    """Process an incoming message and generate AI response."""
    try:
        # Get the message details
        message = webex.messages.get(message_id)
        
        # Don't respond to our own messages
        if message.personEmail == BOT_EMAIL:
            return
        
        # Get AI response with conversation history per room
        response = ai.chat(
            message=message.text,
            room_id=message.roomId,
            system_prompt=SYSTEM_PROMPT
        )
        
        # Handle special commands
        text = message.text.strip()
        text_lower = text.lower()
        
        if text_lower == "/clear":
            ai.clear_history(message.roomId)
            response = "✓ Conversation history cleared!"
        elif text_lower == "/help":
            response = """**Available Commands:**
• Just type your message to chat with the AI
• `/search <query>` - 🔍 Web search for real-time info
• `/clear` - Clear conversation history
• `/help` - Show this help message
• `/models` - List available AI models"""
        elif text_lower.startswith("/search"):
            # Extract search query
            query = text[7:].strip()  # Remove "/search" prefix
            if not query:
                response = "❌ Please provide a search query. Example: `/search latest AI news`"
            else:
                response = "🔍 Searching the web...\n\n"
                search_result = ai.search(query, room_id=message.roomId)
                response += search_result
        elif text_lower == "/models":
            models = ai.list_models()
            response = f"**Available Models:**\n" + "\n".join(f"• {m}" for m in models)
        
        # Send the response with markdown formatting
        webex.messages.create(
            roomId=message.roomId,
            markdown=response
        )
        
        print(f"Responded to {message.personEmail}: {response[:100]}...")
        
    except Exception as e:
        print(f"Error processing message: {e}")


def poll_messages():
    """Poll for new messages (simple approach without webhooks)."""
    import time
    
    print("=" * 50)
    print("🤖 Webex Bot Started!")
    print(f"   Bot Email: {BOT_EMAIL}")
    print(f"   AI Model: {ai.model}")
    print("=" * 50)
    print("\nListening for messages... (Ctrl+C to stop)\n")
    
    # Track processed messages
    processed = set()
    
    # Get initial messages to avoid processing old ones
    try:
        rooms = webex.rooms.list(max=10)
        for room in rooms:
            messages = webex.messages.list(roomId=room.id, max=5)
            for msg in messages:
                processed.add(msg.id)
    except Exception as e:
        print(f"Warning: Could not fetch initial messages: {e}")
    
    # Poll loop
    while True:
        try:
            # Check all rooms the bot is in
            rooms = list(webex.rooms.list(max=50))
            
            for room in rooms:
                # Get recent messages
                messages = list(webex.messages.list(roomId=room.id, max=5))
                
                for msg in messages:
                    # Skip already processed
                    if msg.id in processed:
                        continue
                    
                    # Skip bot's own messages
                    if msg.personEmail == BOT_EMAIL:
                        processed.add(msg.id)
                        continue
                    
                    # Process the message
                    print(f"\n📩 New message from {msg.personEmail}")
                    processed.add(msg.id)
                    process_message(msg.id)
            
            # Wait before next poll
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped.")
            break
        except Exception as e:
            print(f"Error in poll loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    poll_messages()

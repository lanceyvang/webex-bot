"""
Webex Bot - AI-Powered Chat Bot
Connects to Open WebUI for AI responses with smart web search.
"""
import os
import re
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

# System prompt for the AI with web search awareness
SYSTEM_PROMPT = """You are a helpful AI assistant in a Webex chat with web search capabilities.
Be concise but friendly. Format responses nicely for chat - use short paragraphs.
If you don't know something or need current/real-time information, say so honestly.
When you need up-to-date info, the system will automatically search the web for you."""

# Keywords that suggest needing real-time/current information
SEARCH_KEYWORDS = [
    # Time-sensitive
    'latest', 'current', 'today', 'now', 'recent', 'new', 'update',
    'this week', 'this month', 'this year', '2024', '2025', '2026',
    # News & events  
    'news', 'headline', 'breaking', 'announced', 'release', 'launched',
    # Real-time data
    'weather', 'forecast', 'temperature', 'stock', 'price', 'score',
    'status', 'outage', 'down', 'working',
    # Research/lookup
    'how to', 'what is', 'who is', 'when did', 'where is',
    'documentation', 'docs', 'guide', 'tutorial', 'article',
    # Tech support specific
    'error', 'fix', 'solve', 'troubleshoot', 'issue', 'problem',
    'not working', 'broken', 'failed', 'help me',
]

# Patterns suggesting user is struggling/confused
STRUGGLE_PATTERNS = [
    r'\?\s*\?+',              # Multiple question marks
    r'still (not|doesn\'t|won\'t|can\'t)',  # Still having issues
    r'tried (everything|that|already)',      # Tried things
    r'nothing (works|worked)',               # Nothing works
    r'i (don\'t|cant|cannot) (understand|figure|get)',  # Confusion
    r'(please|plz) help',                    # Asking for help
    r'what (else|now)',                      # What else to try
    r'any (other|idea|suggestion)',          # Looking for alternatives
]


def should_use_web_search(text: str, room_id: str = None) -> bool:
    """
    Determine if the message should trigger automatic web search.
    
    Checks for:
    1. Keywords suggesting need for current/real-time info
    2. Patterns suggesting user is struggling
    3. Questions that likely need external lookup
    """
    text_lower = text.lower()
    
    # Check for search keywords
    for keyword in SEARCH_KEYWORDS:
        if keyword in text_lower:
            print(f"  🔍 Auto-search triggered by keyword: '{keyword}'")
            return True
    
    # Check for struggle patterns
    for pattern in STRUGGLE_PATTERNS:
        if re.search(pattern, text_lower):
            print(f"  🔍 Auto-search triggered by struggle pattern")
            return True
    
    # Check if it's a question about something specific
    if '?' in text and len(text) > 20:
        # Questions with specific proper nouns or tech terms
        if re.search(r'(how|what|why|when|where|can|does|is|are)\s+(the|a|my|this|it)', text_lower):
            print(f"  🔍 Auto-search triggered by detailed question")
            return True
    
    return False


def process_message(message_id: str):
    """Process an incoming message and generate AI response."""
    try:
        # Get the message details
        message = webex.messages.get(message_id)
        
        # Don't respond to our own messages
        if message.personEmail == BOT_EMAIL:
            return
        
        # Handle special commands first
        text = message.text.strip()
        text_lower = text.lower()
        
        if text_lower == "/clear":
            ai.clear_history(message.roomId)
            response = "✓ Conversation history cleared!"
        elif text_lower == "/help":
            response = """**Available Commands:**
• Just type your message - AI auto-searches when needed 🔍
• `/search <query>` - Force a web search
• `/clear` - Clear conversation history
• `/help` - Show this help message
• `/models` - List available AI models

💡 *Web search activates automatically for current events, troubleshooting, and when you need real-time info!*"""
        elif text_lower.startswith("/search"):
            # Explicit search command
            query = text[7:].strip()
            if not query:
                response = "❌ Please provide a search query. Example: `/search latest AI news`"
            else:
                response = "🔍 Searching the web...\n\n"
                search_result = ai.search(query, room_id=message.roomId)
                response += search_result
        elif text_lower == "/models":
            models = ai.list_models()
            response = f"**Available Models:**\n" + "\n".join(f"• {m}" for m in models)
        else:
            # Regular message - check if we should auto-search
            if should_use_web_search(text, message.roomId):
                response = "🔍 *Searching for current info...*\n\n"
                search_result = ai.search(text, room_id=message.roomId)
                response += search_result
            else:
                # Standard AI response
                response = ai.chat(
                    message=text,
                    room_id=message.roomId,
                    system_prompt=SYSTEM_PROMPT
                )
        
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

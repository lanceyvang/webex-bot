# Webex AI Bot

A Webex Teams bot powered by Open WebUI for AI responses.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`** (already set up with your credentials)

3. **Run the bot:**
   ```bash
   python bot.py
   ```

4. **Chat with your bot in Webex!**

## Commands

| Command | Description |
|---------|-------------|
| *(any message)* | Chat with AI |
| `/help` | Show help |
| `/clear` | Clear conversation history |
| `/models` | List available AI models |

## Files

- `bot.py` - Main bot (run this)
- `ai_client.py` - Open WebUI integration
- `.env` - Your credentials (do not share!)

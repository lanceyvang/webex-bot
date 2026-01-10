# Webex AI Bot

A Webex Teams bot powered by Open WebUI for AI responses.

## Quick Start (Local)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`** with your credentials

3. **Run the bot:**
   ```bash
   python bot.py
   ```

## Docker Deployment

1. **Clone and configure:**
   ```bash
   git clone https://github.com/lanceyvang/webex-bot.git
   cd webex-bot
   # Create .env with your credentials
   ```

2. **Start with Docker Compose:**
   ```bash
   docker compose up -d
   ```

3. **Auto-updates:** Watchtower will automatically update when you push changes.

## Commands

| Command | Description |
|---------|-------------|
| *(any message)* | Chat with AI |
| `/help` | Show help |
| `/clear` | Clear conversation history |
| `/models` | List available AI models |

## Files

- `bot.py` - Main bot
- `ai_client.py` - Open WebUI integration
- `.env` - Your credentials (do not share!)
- `docker-compose.yml` - Docker configuration

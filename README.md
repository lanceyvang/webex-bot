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

## Develop from Anywhere (Home/Work)

Bot runs on your **work PC only**. From any other computer:

```bash
# One-time setup
git clone https://github.com/lanceyvang/webex-bot.git
cd webex-bot

# Make changes, then push
git add .
git commit -m "Your changes"
git push

# Watchtower on work PC auto-deploys!
```

**No Docker needed** - just Git.

## Docker Deployment (Work PC Only)

```bash
# Initial setup
git clone https://github.com/lanceyvang/webex-bot.git
cd webex-bot
# Create .env with your credentials
docker compose up -d
```

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

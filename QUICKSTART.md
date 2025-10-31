# Quick Start - Slack AI Agent

## Run the Bot

```bash
source venv/bin/activate
python slack_agent.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Slack Bot with Agno + Playwright MCP Integration                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

✅ All environment variables found

⚡️ Starting Slack bot...
💡 Mention the bot in any channel to trigger the agent
======================================================================
⚡️ Bot is running!
```

## Use the Bot in Slack

1. **Go to your Slack workspace**
2. **Mention the bot** in any channel: `@YourBotName your task`
3. **Bot responds** with results

## Example Commands

```
@bot search Google for "best pizza near me"
@bot go to wikipedia and find info about AI
@bot navigate to example.com and take a screenshot
```

## What Happens

1. Bot receives mention
2. Sends: "🤖 Got it! Working on..."
3. AI agent executes task with browser
4. Bot posts results back to Slack

## Stop the Bot

Press `Ctrl+C` in terminal

## Troubleshooting

**Bot not responding?**
- Check bot is running
- Ensure bot invited to channel
- Verify .env has all tokens

**Need help?**
- See README.md for full docs
- Check Slack app permissions

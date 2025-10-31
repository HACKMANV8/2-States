# Slack AI Agent with Web Automation

AI-powered Slack bot that performs web automation tasks using Playwright. Mention the bot in Slack and it will complete web-based tasks for you.

## Features

- **AI-Powered**: Uses Claude Sonnet 4 for intelligent task understanding
- **Web Automation**: 19 Playwright tools for browser control
- **Slack Integration**: Responds to mentions in any channel
- **Persistent Session**: Maintains browser state across tasks

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env with your tokens
cp .env.example .env
# Edit .env with your API keys

# Run the bot
python slack_agent.py
```

## Usage

Mention the bot in Slack:
```
@bot search Google for "best restaurants near me"
@bot go to wikipedia and find info about Python
@bot take a screenshot of example.com
```

## What It Can Do

- Navigate websites
- Search Google, Wikipedia, etc.
- Fill out forms
- Take screenshots
- Extract data from pages
- Click buttons and links
- Type and interact with elements

## Configuration

Required environment variables in `.env`:
- `ANTHROPIC_API_KEY` - Get from console.anthropic.com
- `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN` - Your Slack app token (xapp-...)

## Architecture

```
Slack → Agno Agent → Playwright MCP → Web Automation → Results
```

## Tech Stack

- Slack Bolt - Slack integration
- Agno - AI agent framework
- Claude Sonnet 4 - AI model
- Playwright MCP - Web automation
- Model Context Protocol - Tool integration


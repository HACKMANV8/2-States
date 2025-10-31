from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mention(event, say):
    channel = event["channel"]
    
    print("🚀 Starting testing...")
    say(text="🚀 Starting testing...", channel=channel)
    
    time.sleep(10)
    
    print("✅ Testing complete!")
    say(text="✅ Testing complete!", channel=channel)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("⚡️ Bot is running!")
    handler.start()
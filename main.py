import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
from llm import chat

load_dotenv()

app_token = os.environ.get("SLACK_APP_TOKEN")
bot_token = os.environ.get("SLACK_BOT_TOKEN")

app = App(token=bot_token)

def format_response(text):
    # Convert markdown headers (### Header) to Slack bold format
    text = re.sub(r'^###\s+(.*?)$', r'*\1*', text, flags=re.MULTILINE)
    
    # Convert markdown bold (**text**) to Slack bold (*text*)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    
    # Format primary level numbered lists (1.)
    text = re.sub(r'^\s*(\d+)\.\s+(.*?)$', r'\1. \2', text, flags=re.MULTILINE)
    
    # Format secondary level with letters (a.)
    text = re.sub(r'^\s*[-*]\s+(.*?)$', r'    a. \1', text, flags=re.MULTILINE)
    
    # Format tertiary level with roman numerals (i.)
    text = re.sub(r'^\s{4,}[-*]\s+(.*?)$', r'        i. \1', text, flags=re.MULTILINE)
    
    # Handle mentions (@username)
    text = re.sub(r'@(\w+)', r'@\1', text)
    
    # Ensure proper spacing between sections
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip()

@app.event("app_mention")
def handle_mention(event, client, say):
    client.reactions_add(
        channel=event["channel"],
        name="eyes",
        timestamp=event["ts"]
    )
    
    response = chat(event["text"])
    formatted_response = format_response(response)
    
    client.chat_postMessage(
        channel=event["channel"],
        timestamp=event["ts"],
        thread_ts=event["ts"],
        text=formatted_response
    )

    client.reactions_remove(
        channel=event["channel"],
        name="eyes",
        timestamp=event["ts"]
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
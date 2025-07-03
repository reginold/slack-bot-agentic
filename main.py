import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root directory
root_dir = Path(__file__).parent
env_path = root_dir / '.env'
load_dotenv(env_path)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.handlers.slack_handlers import register_handlers

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Register all handlers
register_handlers(app)

if __name__ == "__main__":
    # Start the app
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
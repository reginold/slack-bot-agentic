from slack_bolt import App
from ..api.llm import chat
from ..utils.formatting import format_slack_message
from ..utils.model_validator import ModelNotAvailableError, APIError

def register_handlers(app: App):
    """Register all Slack event handlers"""
    
    @app.event("app_mention")
    def handle_mention(event, client, say):
        """Handle when the bot is mentioned in a channel"""
        client.reactions_add(
            channel=event["channel"],
            name="eyes",
            timestamp=event["ts"]
        )
        
        try:
            response = chat(event["text"])
            formatted_response = format_slack_message(response)
            
            client.chat_postMessage(
                channel=event["channel"],
                timestamp=event["ts"],
                thread_ts=event["ts"],
                text=formatted_response
            )
        except (ModelNotAvailableError, APIError) as e:
            # Send the user-friendly error message
            client.chat_postMessage(
                channel=event["channel"],
                thread_ts=event["ts"],
                text=e.user_message
            )
        finally:
            client.reactions_remove(
                channel=event["channel"],
                name="eyes",
                timestamp=event["ts"]
            ) 
from slack_bolt import App
from ..api.llm import chat
from ..api.web_search import web_search, WebSearchError
from ..utils.formatting import format_slack_message
from ..utils.model_validator import ModelNotAvailableError, APIError

def simple_router(query: str) -> str:
    """
    Simple router to determine the appropriate handler for the query
    """
    if any(keyword in query.lower() for keyword in ["web", "search", "find", "look up", "google", "bing", "duckduckgo", "yahoo", "ask"]):
        return "web_search"
    return "agent1"


def register_handlers(app: App):
    """Register all Slack event handlers"""
    
    @app.event("message")
    def handle_message_events(body, logger):
        """Handle generic message events"""
        logger.info(f"Received message event: {body}")
        # Add any general message handling logic here
        return
    
    @app.event("app_mention")
    def handle_mention(event, client, say):
        """Handle when the bot is mentioned in a channel"""
        query = event["text"]
        channel = event["channel"]
        ts = event["ts"]  # Thread timestamp
        
        # Step 1: Show routing status
        response = say(
            thread_ts=ts,
            text=f"Processing your query about: {query}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Your Query:*\n{query}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":hourglass_flowing_sand: *Routing to appropriate tool...*"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "I'll show you which tool I'm using once determined"
                        }
                    ]
                }
            ]
        )

        # Determine destination tool
        destination = simple_router(query)
        tool_name = destination.replace('_', ' ').title()
        
        try:
            # Step 2: Update with tool being used
            client.chat_update(
                channel=channel,
                ts=response["ts"],
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Your Query:*\n{query}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":mag_right: *Using {tool_name} Tool*"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Processing your request with {tool_name}"
                            }
                        ]
                    }
                ]
            )

            # Step 3: Process query and show results
            if destination == "web_search":
                search_results = web_search(query)
                result_text = f"*{tool_name} Results for '{query}':*\n{search_results}"
            else:
                result_text = format_slack_message(chat(query))

            # Step 4: Show final results
            client.chat_postMessage(
                channel=channel,
                thread_ts=ts,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":white_check_mark: *{tool_name} Results*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": result_text
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Used {tool_name} to answer your query"
                            }
                        ]
                    }
                ]
            )
            
        except (ModelNotAvailableError, APIError, WebSearchError) as e:
            client.chat_postMessage(
                channel=event["channel"],
                thread_ts=event["ts"],
                text=e.user_message  # Text is already included here
            )
        finally:
            client.reactions_remove(
                channel=event["channel"],
                name="eyes",
                timestamp=event["ts"]
            ) 
import os
import sys
import asyncio
import logging
from slack_sdk import WebClient
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import event bus components
from app.core.events.event_bus import EventBus
from app.core.events.enums import EventType, PlatformType
from app.core.events.base import BaseEvent
from app.core.handler.handler_registry import HandlerRegistry

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Environment Variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not SLACK_BOT_TOKEN:
    logging.error("SLACK_BOT_TOKEN is missing! Set it in environment variables.")
    sys.exit(1)

# Initialize Slack Client
client = WebClient(token=SLACK_BOT_TOKEN)

# Initialize Event Bus and Handler Registry
handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

class SlackEventHandler:
    def __init__(self, slack_client):
        self.slack_client = slack_client

    async def handle_app_mention(self, event: BaseEvent):
        """Handle app mention events from Slack"""
        try:
            channel_id = event.raw_data.get('channel')
            user_question = event.raw_data.get('cleaned_text', '')
            
            response_text = await self.generate_response(channel_id, user_question)

            self.slack_client.chat_postMessage(channel=channel_id, text=response_text)
            logging.info(f"Responded to mention in channel {channel_id}")
        except Exception as e:
            logging.error(f"Error handling app mention: {e}")

    async def handle_message_received(self, event: BaseEvent):
        """Handle message received events from Slack"""
        try:
            channel_id = event.raw_data.get('channel')
            message_text = event.raw_data.get('text', '')
            logging.info(f"Message received in channel {channel_id}: {message_text}")
        except Exception as e:
            logging.error(f"Error handling message received: {e}")

    async def generate_response(self, channel_id: str, user_question: str) -> str:
        """Generate a response based on the channel context and user question"""
        try:
            return f"Responding to: '{user_question}' in channel {channel_id}"
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "Sorry, I couldn't process your request."

def clean_mention_text(text: str, bot_user_id: str) -> str:
    """Remove bot mention from the message text"""
    mention_pattern = f"<@{bot_user_id}>"
    return text.replace(mention_pattern, "").strip()

# Flask App for Slack Events
app = Flask(__name__)

# Initialize Slack Event Handler
slack_event_handler = SlackEventHandler(client)

def register_slack_event_handlers():
    """Register Slack-specific event handlers with the event bus"""
    event_bus.register_handler(EventType.USER_MENTIONED, slack_event_handler.handle_app_mention, PlatformType.SLACK)
    event_bus.register_handler(EventType.MESSAGE_RECEIVED, slack_event_handler.handle_message_received, PlatformType.SLACK)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Slack Events API webhook endpoint"""
    try:
        data = request.json
        logging.info(f"Received Slack event: {data}")

        # Handle Slack Events API challenge
        if "challenge" in data:
            return jsonify({"challenge": data["challenge"]})

        if "event" in data:
            event = data["event"]

            if event.get("type") == "app_mention" and "text" in event:
                bot_info = client.auth_test()
                bot_user_id = bot_info.get("user_id", "")

                cleaned_text = clean_mention_text(event["text"], bot_user_id)

                mention_event = BaseEvent(
                    id=event.get("event_ts"),
                    actor_id=event.get("user"),
                    event_type=EventType.USER_MENTIONED,
                    platform=PlatformType.SLACK,
                    raw_data={'channel': event["channel"], 'text': event["text"], 'cleaned_text': cleaned_text}
                )

                asyncio.run(event_bus.dispatch(mention_event))
                return jsonify({"status": "ok"})

            elif event.get("type") == "message" and "bot_id" not in event and "text" in event:
                message_event = BaseEvent(
                    id=event.get("event_ts"),
                    actor_id=event.get("user", "unknown"),
                    event_type=EventType.MESSAGE_RECEIVED,
                    platform=PlatformType.SLACK,
                    raw_data={'channel': event["channel"], 'text': event["text"]}
                )

                asyncio.run(event_bus.dispatch(message_event))
                return jsonify({"status": "ok"})

        return jsonify({"status": "ok"})

    except Exception as e:
        logging.error(f"Error in slack_events: {e}")
        return jsonify({"status": "error", "message": str(e)})

def main():
    """Main function to set up and run the Slack bot"""
    register_slack_event_handlers()
    app.run(host="0.0.0.0", port=3000, debug=True)

if __name__ == "__main__":
    main()

from slack_bolt import App
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

class SlackService:
    def __init__(self, app: App):
        self.app = app

    async def send_message(self, channel_id: str, text: str) -> None:
        """
        Send a message to a specific channel.
        """
        try:
            await self.app.client.chat_postMessage(
                channel=channel_id,
                text=text
            )
        except SlackApiError as e:
            logger.error(f"Error sending message: {e}")
            raise e

    async def send_dm(self, user_id: str, text: str) -> None:
        """
        Send a Direct Message to a user.
        In Slack API, passing the user_id as channel sends a DM.
        """
        await self.send_message(channel_id=user_id, text=text)

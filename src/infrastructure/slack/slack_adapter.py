"""Slack Adapter - slack_sdk AsyncWebClient 기반 구현"""
from typing import Optional, Dict, Any, List
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from src.domain.ports.messenger_port import MessengerPort


class SlackAdapter(MessengerPort):
    """Slack API를 사용한 MessengerPort 구현체"""
    
    def __init__(self, bot_token: str):
        """
        SlackAdapter 초기화
        
        Args:
            bot_token: Slack Bot Token (xoxb-...)
        """
        self.client = AsyncWebClient(token=bot_token)

    async def send_message(
        self, 
        user_id: str, 
        text: str
    ) -> bool:
        """사용자에게 텍스트 메시지를 전송합니다."""
        try:
            response = await self.client.chat_postMessage(
                channel=user_id,  # DM의 경우 user_id가 channel
                text=text
            )
            return response.get('ok', False)
        except SlackApiError as e:
            # 로깅 추가 가능
            print(f"Slack API Error: {e.response['error']}")
            return False

    async def send_block_message(
        self, 
        user_id: str, 
        blocks: List[Dict[str, Any]],
        text: Optional[str] = None
    ) -> bool:
        """사용자에게 리치 메시지(Block Kit)를 전송합니다."""
        try:
            response = await self.client.chat_postMessage(
                channel=user_id,
                blocks=blocks,
                text=text or "New message"  # 폴백 텍스트 필수
            )
            return response.get('ok', False)
        except SlackApiError as e:
            print(f"Slack API Error: {e.response['error']}")
            return False

    async def get_user_info(
        self, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """사용자 정보를 조회합니다."""
        try:
            response = await self.client.users_info(user=user_id)
            if response.get('ok'):
                return response.get('user')
            return None
        except SlackApiError:
            return None

    async def open_dm_channel(self, user_id: str) -> Optional[str]:
        """
        사용자와의 DM 채널을 엽니다.
        
        Args:
            user_id: Slack 사용자 ID
            
        Returns:
            DM 채널 ID 또는 None
        """
        try:
            response = await self.client.conversations_open(users=[user_id])
            if response.get('ok'):
                return response.get('channel', {}).get('id')
            return None
        except SlackApiError:
            return None

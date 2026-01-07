"""Messenger 서비스 추상 인터페이스 (Port)"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class MessengerPort(ABC):
    """메신저 서비스와의 상호작용을 정의하는 Port"""
    
    @abstractmethod
    async def send_message(
        self, 
        user_id: str, 
        text: str
    ) -> bool:
        """
        사용자에게 텍스트 메시지를 전송합니다.
        
        Args:
            user_id: 사용자 식별자 (slack_id 등)
            text: 전송할 메시지 내용
            
        Returns:
            전송 성공 여부
        """
        pass

    @abstractmethod
    async def send_block_message(
        self, 
        user_id: str, 
        blocks: List[Dict[str, Any]],
        text: Optional[str] = None
    ) -> bool:
        """
        사용자에게 리치 메시지(Block Kit 등)를 전송합니다.
        
        Args:
            user_id: 사용자 식별자
            blocks: 블록 형식의 메시지 구조
            text: 폴백 텍스트 (알림 표시용)
            
        Returns:
            전송 성공 여부
        """
        pass

    @abstractmethod
    async def get_user_info(
        self, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        사용자 정보를 조회합니다.
        
        Args:
            user_id: 사용자 식별자
            
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        pass

"""User Authentication Service Application Service Logic"""

from src.domain.models.user import User
from src.domain.ports.user_repo import UserRepository
from src.infrastructure.google.auth import GoogleAuthManager


class UserAuthService:
    """사용자 인증 및 계정 관리 서비스"""
    
    def __init__(
        self, 
        user_repo: UserRepository,
        auth_manager: GoogleAuthManager
    ):
        self.user_repo = user_repo
        self.auth_manager = auth_manager
    
    def generate_auth_url(self, slack_id: str) -> str:
        """
        Google OAuth 인증 URL을 생성합니다.
        
        Args:
            slack_id: Slack 사용자 ID (state로 전달하여 콜백 식별)
            
        Returns:
            인증 URL
        """
        # state에 slack_id를 포함시켜 콜백 시 사용자를 식별
        return self.auth_manager.get_authorization_url(state=slack_id)
    
    async def handle_google_callback(
        self, 
        code: str, 
        slack_id: str
    ) -> bool:
        """
        Google OAuth 인증 콜백을 처리합니다.
        
        Args:
            code: 인증(authorization) 코드
            slack_id: Slack 사용자 ID (state에서 복원)
            
        Returns:
            처리 성공 여부
        """
        # 1. 코드를 토큰으로 교환
        token_data = await self.auth_manager.exchange_code(code)
        if not token_data:
            return False
        
        # 2. 토큰 저장
        await self.auth_manager.save_token_from_auth_response(slack_id, token_data)
        
        # 3. 사용자 정보 업데이트 (없으면 생성)
        user = await self.user_repo.get_by_slack_id(slack_id)
        if not user:
            user = User(
                slack_id=slack_id,
                name="New User",  # 나중에 Google Profile API로 가져올 수 있음
                is_active=True
            )
            await self.user_repo.save(user)
        else:
            # reactivate if needed
            if not user.is_active:
                user.is_active = True
                await self.user_repo.save(user)
                
        return True

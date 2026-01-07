"""Slack Block Kit 메시지 빌더"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class BlockBuilder:
    """Slack Block Kit 메시지 빌더"""
    
    def __init__(self):
        self.blocks: List[Dict[str, Any]] = []
    
    def add_header(self, text: str) -> 'BlockBuilder':
        """헤더 블록 추가"""
        self.blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": text,
                "emoji": True
            }
        })
        return self
    
    def add_section(
        self, 
        text: str, 
        markdown: bool = True,
        accessory: Optional[Dict[str, Any]] = None
    ) -> 'BlockBuilder':
        """섹션 블록 추가"""
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn" if markdown else "plain_text",
                "text": text
            }
        }
        if accessory:
            block["accessory"] = accessory
        self.blocks.append(block)
        return self
    
    def add_divider(self) -> 'BlockBuilder':
        """구분선 추가"""
        self.blocks.append({"type": "divider"})
        return self
    
    def add_context(self, elements: List[str]) -> 'BlockBuilder':
        """컨텍스트 블록 추가 (작은 텍스트)"""
        self.blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": text}
                for text in elements
            ]
        })
        return self
    
    def add_actions(self, buttons: List[Dict[str, Any]]) -> 'BlockBuilder':
        """액션 블록 추가 (버튼 등)"""
        self.blocks.append({
            "type": "actions",
            "elements": buttons
        })
        return self
    
    def add_image(
        self, 
        image_url: str, 
        alt_text: str,
        title: Optional[str] = None
    ) -> 'BlockBuilder':
        """이미지 블록 추가"""
        block = {
            "type": "image",
            "image_url": image_url,
            "alt_text": alt_text
        }
        if title:
            block["title"] = {
                "type": "plain_text",
                "text": title
            }
        self.blocks.append(block)
        return self
    
    def build(self) -> List[Dict[str, Any]]:
        """블록 리스트 반환"""
        return self.blocks
    
    def clear(self) -> 'BlockBuilder':
        """블록 초기화"""
        self.blocks = []
        return self


# 미리 정의된 버튼 생성 헬퍼
def create_button(
    text: str,
    action_id: str,
    value: str = "",
    style: Optional[str] = None,  # "primary" or "danger"
    url: Optional[str] = None
) -> Dict[str, Any]:
    """버튼 엘리먼트 생성"""
    button = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        },
        "action_id": action_id,
        "value": value
    }
    if style:
        button["style"] = style
    if url:
        button["url"] = url
    return button


# 일정 관련 메시지 템플릿
class EventMessageTemplates:
    """일정 관련 메시지 템플릿"""
    
    @staticmethod
    def event_reminder(
        event_title: str,
        start_time: datetime,
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """일정 리마인더 메시지"""
        builder = BlockBuilder()
        
        builder.add_header(f"📅 일정 알림: {event_title}")
        builder.add_divider()
        
        time_str = start_time.strftime("%Y년 %m월 %d일 %H:%M")
        builder.add_section(f"*시간:* {time_str}")
        
        if location:
            builder.add_section(f"*장소:* {location}")
        
        if description:
            builder.add_section(f"*설명:* {description}")
        
        builder.add_divider()
        builder.add_actions([
            create_button("확인", "event_ack", style="primary"),
            create_button("10분 후 다시 알림", "event_snooze", value="10")
        ])
        
        return builder.build()
    
    @staticmethod
    def event_question(
        event_title: str,
        question: str
    ) -> List[Dict[str, Any]]:
        """일정 관련 질문 메시지"""
        builder = BlockBuilder()
        
        builder.add_header(f"❓ 질문: {event_title}")
        builder.add_divider()
        builder.add_section(question)
        builder.add_context(["AI가 일정을 분석하여 질문을 생성했습니다."])
        
        return builder.build()
    
    @staticmethod
    def event_created(
        event_title: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """일정 생성 확인 메시지"""
        builder = BlockBuilder()
        
        builder.add_header("✅ 일정이 생성되었습니다")
        builder.add_section(f"*제목:* {event_title}")
        builder.add_section(
            f"*시간:* {start_time.strftime('%m/%d %H:%M')} - {end_time.strftime('%H:%M')}"
        )
        
        return builder.build()

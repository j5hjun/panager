"""
PatternAnalyzer - 사용자 패턴 분석기

대화/일정에서 사용자 패턴을 추출합니다.
"""

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    사용자 패턴 분석기

    일정, 대화, 알림 피드백에서 사용자 패턴을 추출합니다.
    """

    # 관심사 키워드
    INTEREST_KEYWORDS = {
        "날씨": ["날씨", "비", "우산", "기온", "눈", "맑", "흐림"],
        "일정": ["일정", "약속", "미팅", "회의", "모임", "스케줄"],
        "교통": ["길찾기", "출근", "퇴근", "지하철", "버스", "택시"],
        "뉴스": ["뉴스", "소식", "기사"],
    }

    # 출근 관련 키워드
    COMMUTE_KEYWORDS = ["출근", "출발", "회사", "사무실", "업무"]

    def extract_patterns_from_schedules(self, schedules: list[dict]) -> dict[str, Any]:
        """
        일정에서 패턴 추출

        Args:
            schedules: 일정 목록 [{"title": str, "start_time": str}, ...]

        Returns:
            패턴 dict
        """
        patterns: dict[str, Any] = {}

        commute_times = []

        for schedule in schedules:
            title = schedule.get("title", "").lower()
            start_time_str = schedule.get("start_time", "")

            # 출근 시간 수집
            for keyword in self.COMMUTE_KEYWORDS:
                if keyword in title:
                    try:
                        start_time = datetime.fromisoformat(start_time_str)
                        commute_times.append(start_time.strftime("%H:%M"))
                    except ValueError:
                        pass
                    break

        # 가장 빈번한 출근 시간
        if commute_times:
            from collections import Counter

            most_common = Counter(commute_times).most_common(1)
            if most_common:
                patterns["commute_time"] = most_common[0][0]

                # 출근 1시간 전 기상 추정
                try:
                    commute_hour = int(patterns["commute_time"].split(":")[0])
                    wake_hour = max(commute_hour - 1, 6)
                    patterns["wake_up_time"] = f"{wake_hour:02d}:00"
                except ValueError:
                    pass

        return patterns

    def extract_preferences_from_messages(self, messages: list[str]) -> dict[str, Any]:
        """
        대화에서 선호도 추출

        Args:
            messages: 메시지 목록

        Returns:
            선호도 dict
        """
        preferences: dict[str, Any] = {"interests": []}

        for message in messages:
            message_lower = message.lower()

            for interest, keywords in self.INTEREST_KEYWORDS.items():
                if any(keyword in message_lower for keyword in keywords):
                    if interest not in preferences["interests"]:
                        preferences["interests"].append(interest)

        return preferences

    def extract_quiet_hours(self, messages: list[dict]) -> dict[str, Any]:
        """
        방해 금지 시간 추출

        Args:
            messages: [{"text": str, "timestamp": str}, ...]

        Returns:
            방해 금지 시간 dict
        """
        preferences: dict[str, Any] = {"quiet_hours": {"start": None, "end": None}}

        quiet_keywords = ["그만", "금지", "알림 끄", "조용", "방해"]

        for msg in messages:
            text = msg.get("text", "").lower()
            timestamp_str = msg.get("timestamp", "")

            if any(keyword in text for keyword in quiet_keywords):
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    hour = timestamp.hour

                    # 22시~07시 사이면 방해 금지 설정
                    if hour >= 22 or hour < 7:
                        preferences["quiet_hours"]["start"] = "22:00"
                        preferences["quiet_hours"]["end"] = "08:00"
                        break
                except ValueError:
                    pass

        return preferences

    def analyze_notification_feedback(self, notifications: list[dict]) -> dict[str, Any]:
        """
        알림 피드백 분석

        Args:
            notifications: [{"sent_at": str, "user_reaction": str}, ...]

        Returns:
            선호 알림 시간 dict
        """
        preferences: dict[str, Any] = {"preferred_notification_times": []}

        positive_times = []
        negative_times = []

        for notification in notifications:
            sent_at = notification.get("sent_at", "")
            reaction = notification.get("user_reaction", "")

            # 시간만 추출 (HH:MM)
            time_match = re.match(r"(\d{2}:\d{2})", sent_at)
            if not time_match:
                # ISO 형식에서 시간 추출
                try:
                    dt = datetime.fromisoformat(sent_at)
                    time_str = dt.strftime("%H:%M")
                except ValueError:
                    time_str = sent_at

            else:
                time_str = time_match.group(1)

            if reaction == "positive":
                positive_times.append(time_str)
            elif reaction == "negative":
                negative_times.append(time_str)

        # 긍정 반응 시간을 선호 시간으로
        preferences["preferred_notification_times"] = list(set(positive_times))

        return preferences

    def merge_patterns(self, existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
        """
        패턴 병합

        Args:
            existing: 기존 패턴
            new: 새 패턴

        Returns:
            병합된 패턴
        """
        merged = existing.copy()

        for key, value in new.items():
            if key == "interests" and "interests" in merged:
                # 관심사 병합 (중복 제거)
                merged["interests"] = list(set(merged["interests"]) | set(value))
            elif key == "preferred_notification_times" and key in merged:
                # 선호 시간 병합 (중복 제거)
                merged[key] = list(set(merged[key]) | set(value))
            else:
                # 새 값으로 덮어쓰기
                merged[key] = value

        return merged

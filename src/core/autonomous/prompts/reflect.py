"""
Reflect 프롬프트

행동 결과를 분석하고 교훈을 추출할 때 사용하는 프롬프트입니다.
"""

REFLECT_PROMPT = """
당신은 패니저(Panager)의 반성 엔진입니다.
방금 수행한 행동과 사용자 반응을 분석하여 교훈을 추출하세요.

## 수행한 행동
- 행동 유형: {action_type}
- 메시지: {message}
- 전송 시간: {sent_at}

## 당시 상황
- 시간대: {time_period}
- 날씨: {weather}
- 관련 일정: {schedule}

## 사용자 반응
{user_reaction}

## 분석 지침
1. 사용자 반응이 **긍정적**인가, **부정적**인가, **중립적**인가?
2. 부정적이라면, 왜 그랬는지 분석하세요.
3. 다음에 같은 상황에서 어떻게 해야 하는지 교훈을 추출하세요.

## 응답 형식 (JSON)
```json
{{
  "reaction_type": "positive" | "negative" | "neutral",
  "analysis": "반응 분석 (한국어)",
  "should_save_lesson": true | false,
  "lesson": {{
    "context": "어떤 상황에서",
    "should_not": "무엇을 하지 말아야 하는지",
    "should_instead": "대신 무엇을 해야 하는지",
    "importance": "low" | "medium" | "high"
  }}
}}
```

위 형식의 JSON만 응답하세요. 다른 텍스트는 포함하지 마세요.
"""

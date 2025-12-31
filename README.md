# 🤵 패니저 (Panizer) - 능동적 AI 비서

> 사용자가 요청하기 전에 먼저 필요한 정보를 알려주는 **통합형 AI 비서**

## ✨ 주요 기능

- 🌤️ **날씨 알림**: 외출 일정에 맞춰 우산 필요 여부 알림
- 📅 **일정 관리**: 일정 등록, 조회, 리마인더
- 💬 **자연스러운 대화**: Slack에서 양방향 대화
- ⏰ **능동적 알림**: 아침 브리핑, 일정 전 준비 알림

## 🚀 시작하기

### 사전 요구사항

- Python 3.11+
- Poetry
- Slack Workspace (Bot 생성 필요)
- API Keys:
  - Slack Bot Token
  - Groq 또는 OpenAI API Key
  - OpenWeatherMap API Key

### 설치 (개발 환경)

```bash
# 1. 저장소 클론
cd proactive_manager

# 2. 의존성 설치
poetry install

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API 키 입력

# 4. 실행
poetry run python -m src.main
```

### 🐳 Docker 배포 (프로덕션)

```bash
# 1. 저장소 클론
git clone https://github.com/j5hjun/panager.git
cd panager

# 2. 환경 변수 설정
cp .env.example .env
nano .env  # API 키 입력

# 3. Docker로 실행
docker compose pull
docker compose up -d

# 4. 상태 확인
docker compose ps
docker compose logs -f

# 선택: 이전 이미지 정리
# docker image prune -f
```

**상세 배포 가이드**: [📚 배포 문서](./docs/DEPLOYMENT.md)

## 🔑 API 키 발급 가이드

### Slack Bot Token

1. [Slack API](https://api.slack.com/apps)에서 앱 생성
2. **Socket Mode** 활성화
3. **Bot Token Scopes** 추가:
   - `chat:write`
   - `app_mentions:read`
   - `im:history`
   - `im:read`
   - `im:write`
4. **App Token** 생성 (connections:write scope)
5. 워크스페이스에 앱 설치

### Groq API Key (무료)

1. [Groq Console](https://console.groq.com/)에서 계정 생성
2. API Keys 메뉴에서 키 생성

### OpenWeatherMap API Key (무료)

1. [OpenWeatherMap](https://home.openweathermap.org/)에서 계정 생성
2. API Keys 메뉴에서 키 생성

## 📁 프로젝트 구조

```
proactive_manager/
├── src/
│   ├── core/                 # 💎 핵심 도메인
│   │   ├── entities/         # 데이터 모델
│   │   ├── prompts/          # AI 시스템 프롬프트
│   │   ├── logic/            # 비즈니스 로직
│   │   └── tools/            # LLM 도구 정의
│   │
│   ├── services/             # 🔌 외부 서비스 연동
│   │   ├── llm/              # LLM API
│   │   ├── weather/          # 날씨 API
│   │   ├── calendar/         # 캘린더
│   │   └── scheduler/        # 스케줄링
│   │
│   ├── adapters/             # 📱 입출력 어댑터
│   │   └── slack/            # Slack Bot
│   │
│   ├── config/               # ⚙️ 설정
│   │   └── settings.py
│   │
│   └── main.py               # 앱 진입점
│
├── tests/                    # 테스트
├── docs/plans/               # 구현 계획서
└── data/                     # 로컬 데이터
```

## 🧪 테스트 실행

```bash
# 전체 테스트
poetry run pytest

# 커버리지 포함
poetry run pytest --cov=src --cov-report=html

# 특정 테스트
poetry run pytest tests/unit/test_config.py -v
```

## 🛠️ 개발

### 코드 품질 도구

```bash
# 코드 포맷팅
poetry run black .

# 린트 체크
poetry run ruff check .

# 린트 자동 수정
poetry run ruff check . --fix

# 타입 체크
poetry run mypy src/
```

### Git 워크플로우

이 프로젝트는 **Feature Branch + Pull Request 기반 워크플로우**를 사용합니다.
main 브랜치에 직접 푸시는 금지되어 있으며, 모든 변경사항은 PR을 통해 머지됩니다.

상세한 워크플로우는 다음 문서를 참고하세요:
- [Git 워크플로우 가이드](.agent/workflows/git-workflow.md)
- [기여 가이드 (CONTRIBUTING.md)](CONTRIBUTING.md)

## 📋 개발 현황

- [x] Phase 1: 프로젝트 기반 구축
- [x] Phase 2: Slack Bot 기본 연동
- [x] Phase 3: LLM 통합 및 자연스러운 대화
- [x] Phase 4: 날씨 도구 구현
- [x] Phase 5: 스케줄러 및 능동적 알림
- [x] Phase 6: 일정 연동 및 맥락 인식
- [x] Phase 7: 안정화 및 문서화

**진행률**: 58% (7/12 phases)

## 💬 사용 예시

### 날씨 조회
```
사용자: 오늘 서울 날씨 어때?
패니저: ☀️ **Seoul** 현재 날씨
       🌤️ 기온: 5.5°C (체감 3.2°C)
       💨 풍속: 2.5m/s
       💧 습도: 60%
       📝 상태: 맑음
```

### 일정 관리
```
사용자: 내일 오후 2시 강남역 미팅 등록해줘
패니저: ✅ 일정이 추가되었습니다: 강남역 미팅 (01월 15일 14:00)

사용자: 내일 일정 뭐야?
패니저: 📅 내일 일정:
       14:00 강남역 미팅 @ 강남역
```

### 리마인더
```
사용자: 5분 후에 회의 알려줘
패니저: 알림이 설정되었습니다. 5분 후(15:45)에 알려드릴게요!

(5분 후)
패니저: ⏰ 리마인더: 회의
```

### 능동적 아침 브리핑 (매일 08:00)
```
패니저: 좋은 아침이에요! ☀️
       
       오늘 서울은 맑음이고, 기온은 5.5°C예요.
       
       오늘의 일정:
       10:00 팀 미팅 @ 회의실 A
       14:00 강남역 미팅 @ 강남역
       
       좋은 하루 보내세요! 😊
```

## 🔧 설정 옵션

### .env 파일 설정

```bash
# Slack 설정 (필수)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_CHANNEL_ID=C0000000000  # 아침 브리핑을 받을 채널

# LLM 설정 (필수)
OPENAI_API_KEY=your-api-key
LLM_PROVIDER=groq  # groq 또는 openai
LLM_MODEL=llama-3.3-70b-versatile

# 날씨 API (필수)
OPENWEATHERMAP_API_KEY=your-weather-api-key

# 선택 설정
DEFAULT_CITY=Seoul
ASSISTANT_NAME=패니저
LOG_LEVEL=INFO
TIMEZONE=Asia/Seoul
```

## 🐛 문제 해결

### Slack Bot이 응답하지 않을 때
1. Slack App Token이 올바른지 확인
2. Socket Mode가 활성화되었는지 확인
3. Bot Token Scopes가 모두 추가되었는지 확인

### 날씨 정보를 가져오지 못할 때
1. OpenWeatherMap API 키가 유효한지 확인
2. 도시명을 영문으로 입력했는지 확인 (Seoul, Busan 등)
3. API 요청 제한을 초과하지 않았는지 확인

### LLM이 응답하지 않을 때
1. Groq/OpenAI API 키가 유효한지 확인
2. 인터넷 연결 상태 확인
3. API 요청 제한 확인

## 📚 문서

- [배포 가이드](./docs/DEPLOYMENT.md) - Docker 배포, CI/CD, 트러블슈팅
- [운영 가이드](./docs/OPERATIONS.md) - 모니터링, 로그, 백업, 긴급 대응
- [Git 워크플로우](.agent/workflows/git-workflow.md) - 브랜치 전략, PR 가이드
- [기여 가이드](./CONTRIBUTING.md) - 코드 기여 방법

## 📄 라이선스

MIT License

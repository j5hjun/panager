# 🚀 배포 가이드

패니저 AI 비서를 배포하는 방법을 안내합니다.

---

## 📋 사전 요구사항

- Docker 24.0+
- Docker Compose v2.20+
- Git
- 4GB RAM 이상 (권장)

---

## 🔐 환경 변수 설정

### 필수 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `SLACK_BOT_TOKEN` | Slack Bot Token | `xoxb-...` |
| `SLACK_APP_TOKEN` | Slack App Token | `xapp-...` |
| `GROQ_API_KEY` | Groq LLM API Key | `gsk_...` |
| `OPENWEATHERMAP_API_KEY` | 날씨 API Key | `abc123...` |

### 선택 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `LLM_MODEL` | `llama-3.3-70b-versatile` | 사용할 LLM 모델 |
| `DEFAULT_CITY` | `Seoul` | 기본 날씨 조회 도시 |
| `KAKAO_REST_API_KEY` | - | 길찾기 API (선택) |

### .env 파일 생성

```bash
cp .env.example .env
nano .env  # 필수 값 입력
```

---

## 🐳 Docker 배포

### 1. 저장소 클론

```bash
git clone https://github.com/j5hjun/panager.git
cd panager
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
nano .env  # API 키 입력
```

### 3. Docker 이미지 빌드 및 실행

```bash
docker compose up -d --build
```

### 4. 상태 확인

```bash
docker compose ps
docker compose logs -f
```

### 5. Slack에서 테스트

패니저에게 DM으로 "안녕" 메시지 전송

---

## 🔄 GitHub Actions 자동 배포 (CI/CD)

### 사전 설정

1. **GitHub Secrets 설정**
   - `ENV_FILE`: .env 파일 전체 내용

2. **셀프호스팅 러너 등록**
   - 서버에서 GitHub Actions Runner 설치
   - `j5hjun/panager` 레포에 등록

### 배포 프로세스

```
main 브랜치 푸시
    ↓
CI 워크플로우 (테스트)
    ↓
Deploy 워크플로우 (셀프호스팅 러너)
    ↓
docker compose up -d --build --wait
```

---

## 🔧 트러블슈팅

### Docker 빌드 실패

```bash
# 캐시 없이 재빌드
docker compose build --no-cache
```

### 컨테이너 시작 안 됨

```bash
# 로그 확인
docker compose logs panager

# 환경 변수 확인
docker compose config
```

### Slack 연결 안 됨

1. `.env`에서 `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` 확인
2. Slack App 설정에서 Socket Mode 활성화 확인
3. Bot Token Scopes 확인: `chat:write`, `im:history`, `im:read`

### 날씨 API 오류

1. `OPENWEATHERMAP_API_KEY` 유효성 확인
2. API 요청 제한 확인 (무료: 60회/분)

---

## 📦 Docker 이미지 직접 Pull

GitHub Container Registry에서 빌드된 이미지 사용:

```bash
docker pull ghcr.io/j5hjun/panager:latest
```

`docker-compose.yml` 수정:

```yaml
services:
  panager:
    image: ghcr.io/j5hjun/panager:latest
    # build: 섹션 제거
```

---

## 🔗 관련 문서

- [운영 가이드](./OPERATIONS.md)
- [README](../README.md)

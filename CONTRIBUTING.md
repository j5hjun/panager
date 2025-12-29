# 기여 가이드 (Contributing Guide)

이 프로젝트에 기여해주셔서 감사합니다! 🎉

이 문서는 **패니저(Panizer)** 프로젝트에 기여하는 방법을 안내합니다.

---

## 📋 목차

- [행동 강령](#-행동-강령)
- [시작하기](#-시작하기)
- [개발 워크플로우](#-개발-워크플로우)
- [브랜치 전략](#-브랜치-전략)
- [커밋 규칙](#-커밋-규칙)
- [Pull Request 가이드](#-pull-request-가이드)
- [코드 스타일](#-코드-스타일)
- [테스트](#-테스트)

---

## 🤝 행동 강령

- **존중**: 모든 기여자를 존중하고 건설적인 피드백을 제공합니다
- **포용성**: 다양한 배경과 경험을 환영합니다
- **협업**: 열린 마음으로 의견을 공유하고 함께 문제를 해결합니다

---

## 🚀 시작하기

### 1. 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/proactive_manager.git
cd proactive_manager

# 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키 입력

# 개발 서버 실행
poetry run python -m src.main
```

### 2. 코드 품질 도구 설치 확인

```bash
# 린트 및 포맷팅 도구
poetry run ruff --version
poetry run black --version

# 타입 체크
poetry run mypy --version

# 테스트
poetry run pytest --version
```

---

## 🔄 개발 워크플로우

### 전체 프로세스

```
1. 이슈 확인/생성
   ↓
2. Feature 브랜치 생성
   ↓
3. 코드 작성 및 커밋
   ↓
4. 로컬 테스트 실행
   ↓
5. 원격에 푸시
   ↓
6. Pull Request 생성
   ↓
7. CI 통과 확인
   ↓
8. 코드 리뷰
   ↓
9. 머지
```

### 상세 단계

#### 1. 작업 시작

```bash
# main 브랜치 최신화
git checkout main
git pull origin main

# Feature 브랜치 생성
git checkout -b feature/your-feature-name
```

#### 2. 개발

- 작은 단위로 자주 커밋
- 각 커밋은 논리적으로 독립적인 변경사항
- 커밋 메시지는 Conventional Commits 규칙 준수

#### 3. 로컬 검증

```bash
# 코드 포맷팅
poetry run black .

# 린트 체크
poetry run ruff check .

# 타입 체크
poetry run mypy src/

# 테스트 실행
poetry run pytest
```

#### 4. 푸시 및 PR 생성

```bash
# 원격에 푸시
git push -u origin feature/your-feature-name

# GitHub에서 PR 생성
```

---

## 🌿 브랜치 전략

### 브랜치 네이밍 규칙

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `feature/` | 새 기능 추가 | `feature/slack-integration` |
| `fix/` | 버그 수정 | `fix/weather-api-timeout` |
| `refactor/` | 코드 리팩토링 | `refactor/tool-registry` |
| `docs/` | 문서 작업 | `docs/update-readme` |
| `test/` | 테스트 추가/수정 | `test/add-unit-tests` |
| `chore/` | 빌드, 설정 등 | `chore/update-dependencies` |
| `hotfix/` | 긴급 수정 | `hotfix/critical-bug` |

### 브랜치 규칙

- **main**: 항상 배포 가능한 안정적인 상태
  - 직접 푸시 금지 (Branch Protection 설정됨)
  - PR을 통해서만 머지 가능
  - CI 통과 필수

- **Feature 브랜치**: 작업 단위
  - main에서 분기
  - 작업 완료 후 PR 생성
  - 머지 후 자동 삭제

---

## 💬 커밋 규칙

### Conventional Commits 형식

```
<타입>(<스코프>): <제목>

<본문>

<푸터>
```

### 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 | `feat: add calendar integration` |
| `fix` | 버그 수정 | `fix: resolve API timeout issue` |
| `docs` | 문서 변경 | `docs: update installation guide` |
| `style` | 코드 포맷팅 | `style: apply black formatting` |
| `refactor` | 리팩토링 | `refactor: simplify tool registry` |
| `test` | 테스트 추가/수정 | `test: add unit tests for scheduler` |
| `chore` | 빌드, 설정 등 | `chore: update dependencies` |
| `perf` | 성능 개선 | `perf: optimize weather API calls` |

### 스코프 (선택사항)

변경 범위를 명시합니다:

- `core`: 핵심 도메인
- `services`: 외부 서비스 연동
- `adapters`: 입출력 어댑터
- `config`: 설정
- `ci`: CI/CD

### 예시

```bash
# 기본
git commit -m "feat: add weather notification feature"

# 스코프 포함
git commit -m "fix(services): resolve OpenWeatherMap API timeout"

# 본문 포함
git commit -m "feat: add calendar integration

- Implement CalendarService
- Add event CRUD operations
- Integrate with Slack bot
"

# Breaking Change
git commit -m "feat!: change LLM API interface

BREAKING CHANGE: LLMService.generate() now returns dict instead of str
"
```

### 커밋 메시지 작성 팁

- **제목**: 50자 이하, 명령형 동사, 마침표 없음
- **본문**: 72자 단위로 줄바꿈, 변경 이유와 방법 설명
- **푸터**: Breaking changes, 이슈 링크 등

---

## 📝 Pull Request 가이드

### PR 생성 전 체크리스트

- [ ] 로컬에서 모든 테스트 통과
- [ ] 린트 및 포맷팅 적용
- [ ] 타입 체크 통과
- [ ] 커밋 메시지 규칙 준수
- [ ] 관련 문서 업데이트

### PR 템플릿

PR을 생성하면 자동으로 템플릿이 로드됩니다. 다음 항목을 작성해주세요:

```markdown
## 📋 변경 사항

이 PR이 무엇을 변경하는지 요약해주세요.

## 🔗 관련 이슈

Closes #이슈번호

## 📸 스크린샷 (선택사항)

UI 변경이 있다면 스크린샷을 첨부해주세요.

## ✅ 체크리스트

- [ ] 로컬에서 모든 테스트 통과
- [ ] 린트 및 포맷팅 적용
- [ ] 타입 체크 통과
- [ ] 문서 업데이트 (필요 시)
- [ ] Breaking changes 없음 (또는 명시함)
```

### PR 리뷰 과정

1. **자동 CI 실행**: PR 생성 시 자동으로 CI 워크플로우 실행
2. **CI 통과 확인**: 모든 검사가 ✅ 상태인지 확인
3. **코드 리뷰**: 리뷰어가 코드 검토 및 피드백 제공
4. **수정 반영**: 피드백에 따라 코드 수정 및 푸시
5. **최종 승인**: 리뷰어의 승인 후 머지 가능

### 머지 방법

- **Squash and merge** (권장): 모든 커밋을 하나로 합쳐 깔끔한 히스토리 유지
- 머지 후 브랜치는 자동으로 삭제됨

---

## 🎨 코드 스타일

### Python 스타일 가이드

이 프로젝트는 다음 도구를 사용합니다:

- **Black**: 코드 포맷팅
- **Ruff**: 린팅 (Flake8, isort 등을 대체)
- **mypy**: 타입 체크

### 포맷팅

```bash
# 자동 포맷팅
poetry run black .

# 포맷팅 확인 (CI에서 사용)
poetry run black . --check
```

### 린팅

```bash
# 린트 체크
poetry run ruff check .

# 자동 수정 가능한 문제 수정
poetry run ruff check . --fix
```

### 타입 힌트

모든 함수와 메서드에 타입 힌트를 추가해주세요:

```python
# Good ✅
def get_weather(city: str) -> WeatherData:
    ...

# Bad ❌
def get_weather(city):
    ...
```

### 네이밍 규칙

- **변수/함수**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **Private 멤버**: `_leading_underscore`

### 문서화

- 모든 public 함수/클래스에 docstring 추가
- Google 스타일 docstring 사용

```python
def add_event(title: str, start_time: datetime) -> Event:
    """캘린더에 이벤트를 추가합니다.

    Args:
        title: 이벤트 제목
        start_time: 시작 시간

    Returns:
        생성된 Event 객체

    Raises:
        ValueError: 제목이 비어있을 경우
    """
    ...
```

---

## 🧪 테스트

### 테스트 작성

- 모든 새 기능에 대해 테스트 작성
- 단위 테스트와 통합 테스트 구분
- 테스트 파일: `tests/unit/`, `tests/integration/`

### 테스트 실행

```bash
# 전체 테스트
poetry run pytest

# 특정 파일
poetry run pytest tests/unit/test_config.py

# 커버리지 포함
poetry run pytest --cov=src --cov-report=html

# Verbose 모드
poetry run pytest -v
```

### 테스트 작성 예시

```python
import pytest
from src.services.weather import WeatherService

def test_get_weather_success():
    """날씨 조회가 성공적으로 동작하는지 테스트"""
    service = WeatherService(api_key="test_key")
    result = service.get_weather("Seoul")
    
    assert result.city == "Seoul"
    assert result.temperature is not None

def test_get_weather_invalid_city():
    """잘못된 도시명에 대한 예외 처리 테스트"""
    service = WeatherService(api_key="test_key")
    
    with pytest.raises(ValueError):
        service.get_weather("")
```

---

## 🐛 버그 리포트

버그를 발견하셨나요? GitHub Issues에 다음 정보를 포함하여 제출해주세요:

- **환경**: OS, Python 버전, 패키지 버전
- **재현 단계**: 버그를 재현하는 단계
- **예상 동작**: 기대했던 결과
- **실제 동작**: 실제로 일어난 결과
- **로그**: 에러 메시지, 스택 트레이스 등

---

## 💡 기능 제안

새로운 기능을 제안하고 싶으신가요? GitHub Issues에 다음 정보를 포함하여 제출해주세요:

- **기능 설명**: 어떤 기능인지 명확히 설명
- **사용 사례**: 언제, 왜 이 기능이 필요한지
- **대안**: 고려한 다른 방법들
- **추가 정보**: 참고 자료, 스크린샷 등

---

## 📚 추가 리소스

- [Git 워크플로우 가이드](.agent/workflows/git-workflow.md)
- [프로젝트 계획서](docs/plans/)
- [README.md](README.md)

---

## ❓ 질문이 있으신가요?

- GitHub Issues에 질문 남기기
- [Discussions](https://github.com/your-username/proactive_manager/discussions)에서 토론하기

---

**감사합니다!** 🙏

여러분의 기여가 패니저를 더 나은 프로젝트로 만듭니다.

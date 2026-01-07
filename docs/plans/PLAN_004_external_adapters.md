# Implementation Plan: 외부 서비스 연동 어댑터 (Google Calendar & Slack)

**Status**: ✅ Complete
**Plan ID**: PLAN_004
**Started**: 2026-01-07
**Last Updated**: 2026-01-07
**Estimated Completion**: 2026-01-07

---

**⚠️ 중요 지침**: 각 페이즈가 완료된 후에는:
1. ✅ 완료된 작업의 체크박스를 체크하세요.
2. 🧪 모든 품질 게이트 검증 명령어를 실행하세요.
3. ⚠️ 모든 품질 게이트 항목이 통과했는지 확인하세요.
4. 📅 위 "Last Updated" 날짜를 업데이트하세요.
5. 📝 Notes 섹션에 배운 점을 기록하세요.
6. ➡️ 그 후에만 다음 페이즈로 진행하세요.

⛔ **품질 게이트를 건너뛰거나 체크가 실패한 상태로 진행하지 마세요.**

---

## 📋 개요 (Overview)

### 기능 설명
외부 서비스(Google Calendar, Slack)와 통신하는 **Infrastructure Adapter**를 구현합니다.
**DO_004** 결정에 따라 Google Calendar는 `aiogoogle`(비동기), Slack은 `slack_sdk`(AsyncWebClient)를 사용합니다.

### 성공 기준 (Success Criteria)
- [x] Google Calendar 이벤트 목록 조회 기능 구현 및 테스트 통과
- [x] Google Calendar OAuth 토큰 갱신 로직 구현
- [x] Slack 메시지 전송 기능 구현 및 테스트 통과
- [x] 모든 어댑터가 도메인 Port 인터페이스를 구현

### 사용자 영향 (User Impact)
- 사용자의 Google Calendar 일정을 시스템에서 조회할 수 있습니다.
- 시스템이 Slack을 통해 사용자에게 메시지를 보낼 수 있습니다.

---

## 🏗️ 아키텍처 결정 (Architecture Decisions)

| 결정 사항 | 근거 | 트레이드오프 |
|----------|-----------|------------|
| **aiogoogle** | 네이티브 비동기 지원, 다중 사용자 동시성 처리 최적화 | 비공식 라이브러리, 문서화 부족 |
| **slack_sdk (AsyncWebClient)** | 공식 라이브러리, 네이티브 비동기 지원 | Slack App 설정 필요 |
| **Port/Adapter 패턴** | 외부 서비스 교체 용이, 테스트 시 Mock 주입 가능 | 추상화 레이어 추가로 코드량 증가 |

---

## 📦 의존성 (Dependencies)

### 시작 전 필요 사항
- [x] PLAN_001 (프로젝트 기반)
- [x] PLAN_002 (도메인 모델)
- [x] PLAN_003 (DB 인프라 - Token 저장)
- [x] DO_004 (외부 연동 전략 결정)

### 외부 의존성
- aiogoogle: ^5.0 ✅ 설치됨
- slack_sdk: ^3.0 ✅ 설치됨
- Google Cloud Console OAuth 자격 증명
- Slack App Bot Token

---

## 🧪 테스트 전략 (Test Strategy)

### 테스트 접근 방식
**TDD 원칙**: 테스트를 **먼저** 작성하고, 이를 통과시키기 위한 구현을 진행합니다.

### 테스트 피라미드
| 테스트 유형 | 커버리지 목표 | 목적 |
|-----------|-----------------|---------|
| **단위 테스트** | 80% | Adapter 로직 검증 (Mock API 사용) |
| **통합 테스트** | 핵심 기능 | 실제 API 호출 검증 (수동/선택적) |

### 테스트 파일 구조
```
tests/
├── unit/
│   ├── test_ports.py                     ✅
│   └── infrastructure/
│       ├── test_google_calendar_adapter.py  ✅
│       └── test_slack_adapter.py            ✅
└── integration/
    └── test_external_adapters.py (선택적, 실제 API 호출)
```

---

## 🚀 구현 페이즈 (Implementation Phases)

### Phase 1: 도메인 Port 정의
**목표**: 외부 서비스 연동을 위한 추상 인터페이스 정의
**예상 시간**: 1시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 1.1**: Port Import 테스트
  - 파일: `tests/unit/test_ports.py`
  - 상세: `CalendarPort`, `MessengerPort` 클래스 존재 여부 확인

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 1.2**: CalendarPort 정의
  - 파일: `src/domain/ports/calendar_port.py`
  - 메서드: `get_events()`, `create_event()`, `delete_event()`
- [x] **Task 1.3**: MessengerPort 정의
  - 파일: `src/domain/ports/messenger_port.py`
  - 메서드: `send_message()`, `send_block_message()`, `get_user_info()`

#### 품질 게이트 (Quality Gate) ✋
- [x] **TDD 준수**: Red-Green 사이클 준수
- [x] **린트**: `ruff check .` 통과

---

### Phase 2: Google Calendar Adapter 구현
**목표**: aiogoogle을 사용한 Calendar API 어댑터 구현
**예상 시간**: 4시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 2.1**: 이벤트 조회 테스트 (Mock)
  - 파일: `tests/unit/infrastructure/test_google_calendar_adapter.py`
  - 상세: `get_events()` 호출 시 이벤트 리스트 반환 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 2.2**: GoogleCalendarAdapter 구현
  - 파일: `src/infrastructure/google/calendar_adapter.py`
  - 구현: `CalendarPort` 인터페이스 구현
- [x] **Task 2.3**: OAuth 토큰 관리 유틸리티
  - 파일: `src/infrastructure/google/auth.py`
  - 구현: 토큰 갱신, 자격 증명 로드, 인증 URL 생성

**🔵 REFACTOR: 코드 개선**
- [x] **Task 2.4**: 에러 핸들링 추가
  - 상세: `_parse_event` 메서드에서 예외 처리 구현됨

#### 품질 게이트 (Quality Gate) ✋
- [x] **TDD 준수**: 테스트 먼저 작성
- [x] **테스트 통과**: `pytest tests/unit/infrastructure/test_google_calendar_adapter.py`
- [x] **린트**: ruff 에러 없음

---

### Phase 3: Slack Adapter 구현
**목표**: slack_sdk AsyncWebClient를 사용한 메시지 전송 어댑터 구현
**예상 시간**: 3시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 3.1**: 메시지 전송 테스트 (Mock)
  - 파일: `tests/unit/infrastructure/test_slack_adapter.py`
  - 상세: `send_message()` 호출 시 Slack API 호출 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 3.2**: SlackAdapter 구현
  - 파일: `src/infrastructure/slack/slack_adapter.py`
  - 구현: `MessengerPort` 인터페이스 구현
- [x] **Task 3.3**: Block Kit 메시지 빌더
  - 파일: `src/infrastructure/slack/blocks.py`
  - 구현: BlockBuilder 클래스, EventMessageTemplates

**🔵 REFACTOR: 코드 개선**
- [x] **Task 3.4**: Rate Limiting 처리
  - 상세: `SlackApiError` 처리 및 로깅 추가됨

#### 품질 게이트 (Quality Gate) ✋
- [x] **TDD 준수**: 테스트 먼저 작성
- [x] **테스트 통과**: `pytest tests/unit/infrastructure/test_slack_adapter.py`
- [x] **린트**: ruff 에러 없음

---

### Phase 4: 통합 및 설정
**목표**: 환경 변수 설정 및 DI(Dependency Injection) 준비
**예상 시간**: 2시간
**상태**: ✅ Complete

#### 작업 (Tasks)

- [x] **Task 4.1**: Settings 업데이트
  - 파일: `src/config/settings.py`
  - 추가: `google_client_id`, `google_client_secret`, `google_redirect_uri`
- [x] **Task 4.2**: 의존성 주입 설정
  - 파일: `src/infrastructure/container.py`
  - 구현: Container 클래스, FastAPI Depends 헬퍼

#### 품질 게이트 (Quality Gate) ✋
- [x] **전체 테스트 통과**: `pytest` (15 passed)
- [x] **린트**: `ruff check .` 통과
- [x] **환경 변수 문서화**: `.env.example` 업데이트됨

---

## ⚠️ 위험 평가 (Risk Assessment)

| 위험 | 발생확률 | 영향도 | 완화 전략 |
|------|-------------|--------|---------------------|
| **aiogoogle 버전 호환성** | 중간 | 중간 | 버전 고정, 테스트 커버리지 확보 |
| **OAuth 토큰 만료** | 높음 | 높음 | Refresh Token 자동 갱신 로직 구현 |
| **Slack Rate Limiting** | 중간 | 낮음 | Exponential Backoff 적용 |
| **API 키 노출** | 낮음 | 높음 | `.env` 사용, Secret 관리 |

---

## 🔄 롤백 전략 (Rollback Strategy)

### Phase 실패 시
**복구 절차**:
- 파일 삭제: `src/infrastructure/google/`, `src/infrastructure/slack/`
- 의존성 제거: `poetry remove aiogoogle slack_sdk`
- Git 변경사항 폐기

---

## 📊 진행 상황 추적 (Progress Tracking)

### 완료 상태
- **Phase 1**: ⏳ 0% | 🔄 50% | ✅ 100%
- **Phase 2**: ⏳ 0% | 🔄 50% | ✅ 100%
- **Phase 3**: ⏳ 0% | 🔄 50% | ✅ 100%
- **Phase 4**: ⏳ 0% | 🔄 50% | ✅ 100%

**전체 진행률**: 100% 완료

### 시간 추적
| 페이즈 | 예상 시간 | 실제 시간 | 차이 |
|-------|-----------|--------|----------|
| Phase 1 | 1시간 | 0.2시간 | -0.8시간 |
| Phase 2 | 4시간 | 0.3시간 | -3.7시간 |
| Phase 3 | 3시간 | 0.2시간 | -2.8시간 |
| Phase 4 | 2시간 | 0.1시간 | -1.9시간 |
| **합계** | 10시간 | 0.8시간 | -9.2시간 |

---

## 📝 노트 및 배운 점 (Notes & Learnings)

### 구현 노트
- aiogoogle 5.17.0 버전 사용, 안정적으로 동작함
- slack_sdk 3.39.0의 `AsyncWebClient`가 네이티브 비동기 완벽 지원
- Port/Adapter 패턴으로 외부 서비스를 추상화하여 테스트 용이성 확보

### 직면한 차단 요소 (Blockers)
- 없음

### 향후 개선 사항
- OAuth 플로우 구현 시 `auth.py` 모듈 추가 필요
- Block Kit 메시지 빌더는 UI 요구사항 확정 후 구현
- DI Container는 Application Layer(Use Cases) 구현 시 설정

---

## 📚 참조문서 (References)

### 문서
- [aiogoogle Documentation](https://aiogoogle.readthedocs.io/)
- [Slack SDK for Python](https://slack.dev/python-slack-sdk/)
- [Google Calendar API](https://developers.google.com/calendar/api/v3/reference)

### 관련 이슈
- DO_004: External Integration Strategy

---

## ✅ 최종 체크리스트 (Final Checklist)

**계획을 COMPLETE로 표시하기 전에**:
- [x] 모든 페이즈가 완료되고 품질 게이트를 통과했음
- [x] 전체 테스트 수행됨 (15 passed)
- [x] 문서 업데이트됨
- [x] 보안 검토 완료됨 (API 키는 환경변수로 관리)
- [x] `.env.example` 업데이트됨

# Implementation Plan: 프레젠테이션 계층 (Presentation Layer)

**Status**: ✅ Complete
**Plan ID**: PLAN_006
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
사용자와 시스템이 만나는 접점인 **Presentation Layer**를 구현합니다.
FastAPI를 사용하여 Slack Event를 수신하고, Google OAuth Callback을 처리합니다.
비동기 작업 처리를 위해 **Redis Queue (arq)**를 도입합니다.

### 성공 기준 (Success Criteria)
- [x] Redis가 Docker Compose에 추가되고 정상 동작해야 함.
- [x] `/slack/events` 엔드포인트가 Slack의 Challenge 요청과 Event 요청을 정상 처리해야 함.
- [x] 사용자가 1:1 DM으로 말을 걸면(예: "로그인"), 백그라운드 Worker가 이를 처리하고 응답해야 함.
- [x] `/auth/google/callback`이 Google 인증 후 Slack 앱으로 리다이렉트해야 함.

### 사용자 영향 (User Impact)
- 사용자는 Slack DM을 통해 자연스럽게 서비스와 대화할 수 있습니다.
- Google 로그인을 통해 캘린더가 연동됩니다.

---

## 🏗️ 아키텍처 결정 (Architecture Decisions)

| 결정 사항 | 근거 | 트레이드오프 |
|----------|-----------|------------|
| **arq (Async Redis Queue)** | `asyncio` 기반의 가볍고 빠른 Job Queue, FastAPI와 호환성 우수 | Celery보다 기능은 적음 (하지만 현재 요구사항엔 충분) |
| **Slack Event API** | RTM API(Deprecated) 대신 사용, 서버리스 친화적 | 3초 타임아웃 제한 있음 (Queue 필수) |
| **Deep Link Redirect** | OAuth 완료 후 즉시 Slack 복귀로 UX 향상 | 모바일/데스크톱 동작 차이 발생 가능 |

---

## 📦 의존성 (Dependencies)

### 시작 전 필요 사항
- [x] PLAN_005 (Application Layer)
- [x] DO_006 (Interaction Design - Queue, DM, Deep Link)

### 외부 의존성
- `arq`: Redis Queue
- `redis`: Redis Client
- Docker Redis Image

---

## 🧪 테스트 전략 (Test Strategy)

### 테스트 접근 방식
- **End-to-End Test**: `TestClient`를 사용하여 API 엔드포인트 호출을 시뮬레이션합니다.
- **Worker Test**: `arq` 워커 함수를 직접 호출하거나 Mocking하여 로직을 검증합니다.

### 테스트 파일 구조
```
tests/
├── integration/
│   ├── test_api_auth.py  ✅
│   └── test_api_slack.py ✅
└── unit/
    └── presentation/
        └── test_worker.py ✅
```

---

## 🚀 구현 페이즈 (Implementation Phases)

### Phase 1: 인프라 구성 (Redis & arq)
**목표**: 비동기 작업 처리를 위한 Redis 컨테이너 및 arq 설정
**예상 시간**: 2시간
**상태**: ✅ Complete

#### 작업 (Tasks)
- [x] **Task 1.1**: `docker-compose.local.yml`에 Redis 서비스 추가
- [x] **Task 1.2**: `poetry add arq redis`
- [x] **Task 1.3**: `src/config/settings.py`에 Redis 설정 추가
- [x] **Task 1.4**: `src/worker.py` (Worker Entrypoint) 생성 및 Job 함수 정의

#### 품질 게이트 (Quality Gate) ✋
- [x] **Redis 연결 확인**: `docker-compose up` 후 `redis-cli ping` 성공
- [x] **Worker 실행 확인**: `arq src.worker.WorkerSettings` 실행 시 에러 없음

---

### Phase 2: Slack Event 수신 및 Enqueue
**목표**: Slack Event 수신 엔드포인트 구현 및 Queue잉
**예상 시간**: 3시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 작성**
- [x] **Test 2.1**: Slack Event API 테스트 (`test_api_slack.py`)
  - url_verification 처리 검증
  - event_callback 수신 시 200 OK 및 Enqueue 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 2.2**: `src/presentation/api/routers/slack.py` 구현
  - `slack_events` 엔드포인트
  - `RequestVerifier` 미들웨어/의존성 (서명 검증)
- [x] **Task 2.3**: `src/main.py`에 라우터 등록 및 `arq` Pool 생성/연결

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/integration/test_api_slack.py`
- [x] **린트**: `ruff check .`

---

### Phase 3: Worker 로직 구현 (DM 처리)
**목표**: 큐에서 작업을 꺼내 DM 의도를 파악하고 응답
**예상 시간**: 4시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 작성**
- [x] **Test 3.1**: Worker 함수 테스트 (`test_worker.py`)
  - `handle_slack_event` 함수 호출 시 의도 파악 및 Service 호출 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 3.2**: `src/application/use_cases/handle_dm.py` (혹은 Service 내) 구현
  - 간단한 키워드 매칭("로그인", "연결") -> Auth Link 발송
  - 그 외 -> "아직 배우는 중입니다" 응답
- [x] **Task 3.3**: Worker 함수에서 UseCase 실행 로직 연결

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/unit/presentation/test_worker.py`

---

### Phase 4: Google OAuth Callback 구현
**목표**: OAuth 인증 완료 및 리다이렉트
**예상 시간**: 2시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 작성**
- [x] **Test 4.1**: Callback API 테스트 (`test_api_auth.py`)
  - code 수신 후 Service 호출 및 Redirect 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 4.2**: `src/presentation/api/routers/auth.py` 구현
  - `google_callback` 엔드포인트
  - `slack://` Deep Link 리다이렉트

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/integration/test_api_auth.py`

---

## ⚠️ 위험 평가 (Risk Assessment)

| 위험 | 발생확률 | 영향도 | 완화 전략 |
|------|-------------|--------|---------------------|
| **Slack Retry Storm** | 중간 | 높음 | `X-Slack-Retry-Num` 헤더 확인하여 중복 처리 방지 (Redis Key 활용) |
| **Worker Down** | 낮음 | 높음 | Docker Restart Policy, 모니터링 |

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
| Phase 1 | 2시간 | 0.4hr | -1.6hr |
| Phase 2 | 3시간 | 0.5hr | -2.5hr |
| Phase 3 | 4시간 | 0.5hr | -3.5hr |
| Phase 4 | 2시간 | 0.3hr | -1.7hr |
| **합계** | 11시간 | 1.7hr | -9.3hr |

---

## ✅ 최종 체크리스트 (Final Checklist)

- [x] Redis Queue가 정상 동작함
- [x] Slack DM에 봇이 응답함
- [x] Google 로그인이 정상적으로 완료되고 Slack으로 돌아옴

# Implementation Plan: 애플리케이션 계층 (Service Layer)

**Status**: ✅ Complete
**Plan ID**: PLAN_005
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
도메인 모델과 인프라스트럭처 어댑터를 조율하여 실제 비즈니스 로직을 수행하는 **Application Service Layer**를 구현합니다.
사용자 인증(OAuth), 캘린더 동기화, 알림 발송 등의 Use Case를 처리합니다.

### 성공 기준 (Success Criteria)
- [x] **UserAuthService**: Slack 사용자가 Google OAuth 인증을 완료하고 User/Token 정보가 DB에 저장되어야 함.
- [x] **CalendarSyncService**: 사용자의 Google Calendar 이벤트를 조회하여 DB에 최신 상태로 동기화(저장/업데이트)되어야 함.
- [x] **NotificationService**: 비즈니스 로직에 따라 Slack 메시지(Block Kit 포함)가 전송되어야 함.

### 사용자 영향 (User Impact)
- 최초 1회 로그인(OAuth)으로 서비스를 이용할 수 있게 됩니다.
- 캘린더 일정이 시스템에 자동으로 반영됩니다.

---

## 🏗️ 아키텍처 결정 (Architecture Decisions)

| 결정 사항 | 근거 | 트레이드오프 |
|----------|-----------|------------|
| **Service Layer 패턴** | 비즈니스 로직과 인프라/API 계층 분리 | 클래스가 많아질 수 있음 (UseCase별 분리 고려 가능하나 초기엔 Service로 그룹화) |
| **Transaction 관리** | Service 메서드 단위로 DB 트랜잭션 관리 (`uow` 패턴 또는 Session 주입) | 구현 복잡도 증가 vs 데이터 무결성 보장 |

---

## 📦 의존성 (Dependencies)

### 시작 전 필요 사항
- [x] PLAN_003 (DB Repository)
- [x] PLAN_004 (External Adapters - Google/Slack)

### 내부 모듈
- `src/domain/services`: 도메인 서비스(순수 로직)
- `src/application/services`: 애플리케이션 서비스(Workflow)

---

## 🧪 테스트 전략 (Test Strategy)

### 테스트 접근 방식
**Mockist TDD**: Service Layer 테스트 시 Repository와 Adapter를 Mocking하여 순수 비즈니스 플로우를 검증합니다.

### 테스트 파일 구조
```
tests/
├── unit/
│   └── application/
│       ├── test_auth_service.py         ✅
│       ├── test_sync_service.py         ✅
│       └── test_notification_service.py ✅
```

---

## 🚀 구현 페이즈 (Implementation Phases)

### Phase 1: 인증 서비스 (UserAuthService)
**목표**: Slack ID와 Google 계정 연동 및 토큰 저장
**예상 시간**: 3시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 1.1**: 인증 URL 생성 및 콜백 처리 테스트
  - 파일: `tests/unit/application/test_auth_service.py`
  - 상세: `generate_auth_url`, `handle_google_callback` 메서드 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 1.2**: UserAuthService 구현
  - 파일: `src/application/services/auth_service.py`
  - 기능: 
    - `generate_auth_url(slack_id)`: 인증 링크 생성
    - `handle_google_callback(code, slack_id)`: 토큰 교환, User/Token DB 저장

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/unit/application/test_auth_service.py`
- [x] **린트**: `ruff check .`

---

### Phase 2: 캘린더 동기화 서비스 (CalendarSyncService)
**목표**: Google Calendar 이벤트를 DB로 동기화
**예상 시간**: 4시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 2.1**: 동기화 로직 테스트
  - 파일: `tests/unit/application/test_sync_service.py`
  - 상세: Adapter에서 조회한 이벤트를 Repository에 저장하는지 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 2.2**: CalendarSyncService 구현
  - 파일: `src/application/services/sync_service.py`
  - 기능: `sync_user_calendar(user_id)` 구현
    - GoogleAdapter.get_events() 호출
    - EventRepo.save() 호출 (기존 이벤트 업데이트 및 신규 생성)

**🔵 REFACTOR: 코드 개선**
- [x] **Task 2.3**: 중복/변경 감지 로직 최적화
  - 상세: Repository에서 Upsert 처리 가정 (save 호출)

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/unit/application/test_sync_service.py`
- [x] **린트**: `ruff check .`

---

### Phase 3: 알림 서비스 (NotificationService)
**목표**: 사용자에 대한 Slack 알림 발송 중앙화
**예상 시간**: 2시간
**상태**: ✅ Complete

#### 작업 (Tasks)

**🔴 RED: 실패하는 테스트 먼저 작성**
- [x] **Test 3.1**: 알림 발송 테스트
  - 파일: `tests/unit/application/test_notification_service.py`
  - 상세: 단순 텍스트 및 Block 메시지 전송 요청 검증

**🟢 GREEN: 테스트 통과를 위한 구현**
- [x] **Task 3.2**: NotificationService 구현
  - 파일: `src/application/services/notification_service.py`
  - 기능: `send_welcome_message`, `send_event_reminder` 등 추상화된 메서드 제공

#### 품질 게이트 (Quality Gate) ✋
- [x] **테스트 통과**: `pytest tests/unit/application/test_notification_service.py`
- [x] **린트**: `ruff check .`

---

### Phase 4: Container 등록
**목표**: DI 컨테이너에 서비스 등록
**예상 시간**: 1시간
**상태**: ✅ Complete

#### 작업 (Tasks)
- [x] **Task 4.1**: `src/infrastructure/container.py`에 서비스 Factory 추가
  - `get_auth_service()`, `get_sync_service()`, `get_notification_service()`

#### 품질 게이트 (Quality Gate) ✋
- [x] **전체 테스트 통과**: `pytest`
- [x] **린트**: `ruff check .`

---

## ⚠️ 위험 평가 (Risk Assessment)

| 위험 | 발생확률 | 영향도 | 완화 전략 |
|------|-------------|--------|---------------------|
| **토큰 만료 중 동기화 시도** | 높음 | 높음 | Adapter 내부의 자동 갱신 로직 활용, 실패 시 사용자에게 재인증 요청 알림 |
| **API Rate Limit 초과** | 중간 | 중간 | 동기화 주기를 길게 설정 (초기엔 수동/요청시 동기화 위주) |

---

## 🔄 롤백 전략 (Rollback Strategy)

### Phase 실패 시
- 파일 삭제: `src/application/services/*.py`
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
| Phase 1 | 3시간 | 0.5hr | -2.5hr |
| Phase 2 | 4시간 | 0.5hr | -3.5hr |
| Phase 3 | 2시간 | 0.3hr | -1.7hr |
| Phase 4 | 1시간 | 0.2hr | -0.8hr |
| **합계** | 10시간 | 1.5hr | -8.5hr |

---

## ✅ 최종 체크리스트 (Final Checklist)

**계획을 COMPLETE로 표시하기 전에**:
- [x] 모든 Services가 구현되고 테스트됨
- [x] DI Container에 등록되어 주입 가능함

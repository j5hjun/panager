# Implementation Plan: 외부 캘린더 연동 및 스마트 일정 어시스턴트

**Status**: 🔒 Blocked (P-014 대기)
**Plan ID**: P-013
**Started**: -
**Last Updated**: 2026-01-05
**Estimated Completion**: -
**Dependencies**: P-010, P-011, **P-014** (다중 사용자 시스템)

---

**⚠️ 주의**: 이 계획은 P-014 (다중 사용자 시스템)가 완료된 후 진행합니다.

다중 사용자 환경에서 각 사용자별 OAuth 토큰 관리가 필요하므로,
P-014에서 토큰 저장소와 인증 흐름을 먼저 구현해야 합니다.

---

**⚠️ CRITICAL INSTRUCTIONS**: After completing each phase:
1. ✅ Check off completed task checkboxes
2. 🧪 Run all quality gate validation commands
3. ⚠️ Verify ALL quality gate items pass
4. 📅 Update "Last Updated" date above
5. 📝 Document learnings in Notes section
6. ➡️ Only then proceed to next phase

⛔ **DO NOT skip quality gates or proceed with failing checks**

---

## 📋 Overview

### Feature Description

**외부 캘린더(Google Calendar, iCloud)와 연동**하여:
1. 캘린더에 일정이 등록되면 **트리거**되어 사용자에게 필요한 정보 제공
2. 슬랙 메신저를 통해 **캘린더에 일정 등록** 가능

현재 시스템은 로컬 SQLite DB만 사용합니다. 이를 외부 캘린더와 양방향 동기화하고,
일정 기반 **스마트 어시스턴트** 기능을 추가합니다.

**⚠️ 다중 사용자 지원**: 각 사용자별 Google/iCloud 계정 연동 (P-014 필요)

### Success Criteria

- [ ] Google Calendar API 연동 (사용자별)
- [ ] iCloud Calendar 연동 (사용자별)
- [ ] 일정 등록 시 자동 트리거 → 사용자에게 정보 제공
- [ ] 슬랙에서 자연어로 일정 등록 → 캘린더 반영
- [ ] 교통 정보, 출발 시간, 준비물 등 스마트 정보 제공
- [ ] 사용자 패턴 기반 등록 정보 자동 완성
- [ ] 모든 테스트 통과 (커버리지 ≥80%)

### User Impact

- **자동화**: 캘린더 일정 등록만으로 필요한 모든 정보 제공
- **편의성**: 슬랙에서 바로 일정 등록
- **스마트**: 패턴 학습 기반 정보 자동 완성

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| Google Calendar API | 가장 널리 사용, 문서 풍부 | OAuth 인증 필요 |
| CalDAV for iCloud | 표준 프로토콜, 범용성 | Apple 특유의 제약 |
| Polling 방식 | 단순, WebHook 설정 불필요 | 지연 있음 (5분 주기) |
| 기존 CalendarService 확장 | 코드 재사용, 호환성 유지 | 인터페이스 변경 최소화 |
| **P-014 토큰 저장소 활용** | 다중 사용자, 보안 | P-014 의존성 |

---

## 📦 Dependencies

### Required Before Starting
- [x] P-010 자율 판단 코어 완료
- [x] P-011 메모리 시스템 완료
- [ ] **P-014 다중 사용자 시스템 완료** ← 먼저 진행 필요
- [ ] Google Cloud 프로젝트 설정 (API 키)
- [ ] iCloud 앱 비밀번호 생성

### External Dependencies
```bash
poetry add google-api-python-client google-auth-oauthlib caldav
```

---

## 🧪 Test Strategy

### Testing Approach
**TDD Principle**: Write tests FIRST, then implement to make them pass

### Test Pyramid for This Feature
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Unit Tests** | ≥80% | API 클라이언트, 파서 |
| **Integration Tests** | Critical paths | 캘린더 동기화 |
| **E2E Tests** | Key flows | 일정 등록 → 알림 |

### Test File Organization
```
tests/unit/services/calendar/
├── test_google_calendar.py
├── test_icloud_calendar.py
└── test_calendar_sync.py

tests/unit/core/autonomous/
└── test_schedule_trigger.py

tests/integration/
└── test_calendar_integration.py
```

---

## 🚀 Implementation Phases

### Phase 1: 캘린더 인터페이스 추상화
**Goal**: 외부 캘린더 연동을 위한 추상 인터페이스 설계
**Estimated Time**: 2시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 1.1**: CalendarProvider 인터페이스 테스트
  - `test_list_events`: 일정 목록 조회
  - `test_get_event`: 단일 일정 조회
  - `test_create_event`: 일정 생성
  - `test_sync_events`: 일정 동기화

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 1.2**: CalendarProvider 프로토콜 정의
  - File: `src/services/calendar/provider.py`

- [ ] **Task 1.3**: LocalCalendarProvider 구현 (기존 SQLite 래핑)
  - File: `src/services/calendar/local_provider.py`

- [ ] **Task 1.4**: CalendarService 리팩토링
  - Provider 기반 구조로 변경
  - 기존 테스트 호환성 유지

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] 기존 CalendarService 테스트 호환

---

### Phase 2: Google Calendar 연동
**Goal**: Google Calendar API 연동
**Estimated Time**: 4시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: GoogleCalendarProvider 테스트
  - `test_authenticate`: OAuth 인증
  - `test_list_events`: 일정 목록 조회
  - `test_create_event`: 일정 생성
  - `test_webhook_trigger`: 변경 감지

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.2**: GoogleCalendarProvider 구현
  - File: `src/services/calendar/google_provider.py`
  - OAuth 2.0 인증 흐름
  - Events API 연동

- [ ] **Task 2.3**: 일정 동기화 서비스
  - File: `src/services/calendar/sync_service.py`
  - 폴링 기반 변경 감지 (5분 주기)
  - 증분 동기화 (pageToken 활용)

#### Quality Gate ✋
- [ ] Mock API로 테스트 통과
- [ ] 실제 Google Calendar 연동 테스트 (수동)

---

### Phase 3: iCloud Calendar 연동
**Goal**: iCloud Calendar (CalDAV) 연동
**Estimated Time**: 4시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 3.1**: ICloudCalendarProvider 테스트
  - `test_authenticate`: 앱 비밀번호 인증
  - `test_list_events`: CalDAV 일정 조회
  - `test_create_event`: CalDAV 일정 생성

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 3.2**: ICloudCalendarProvider 구현
  - File: `src/services/calendar/icloud_provider.py`
  - CalDAV 프로토콜 사용
  - caldav 라이브러리 활용

#### Quality Gate ✋
- [ ] Mock CalDAV 서버로 테스트 통과
- [ ] 실제 iCloud 연동 테스트 (수동)

---

### Phase 4: 일정 트리거 시스템
**Goal**: 새 일정 등록 시 자동으로 스마트 정보 제공
**Estimated Time**: 4시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 4.1**: ScheduleTrigger 테스트
  - `test_trigger_on_new_event`: 새 일정 감지 시 트리거
  - `test_enrich_event_info`: 일정 정보 보강 (교통, 날씨)
  - `test_ask_clarification`: 정보 부족 시 질문
  - `test_send_notification`: 사용자에게 알림

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 4.2**: ScheduleTrigger 구현
  - File: `src/core/autonomous/triggers/schedule_trigger.py`
  - 새 일정 감지 → 정보 보강 → 알림

- [ ] **Task 4.3**: EventEnricher 구현
  - File: `src/core/autonomous/enrichers/event_enricher.py`
  - 장소 → 교통 정보 (get_directions)
  - 날씨 정보 (get_weather)
  - 출발 시간 계산 (calculate_departure)
  - 준비물 추천 (LLM 기반)

- [ ] **Task 4.4**: ClarificationService 구현
  - File: `src/core/autonomous/services/clarification_service.py`
  - 정보 부족 시 사용자에게 질문
  - 응답 대기 및 처리

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] E2E 시나리오 테스트

---

### Phase 5: 슬랙에서 일정 등록
**Goal**: 슬랙 메시지로 캘린더에 일정 등록
**Estimated Time**: 3시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 5.1**: ScheduleRegistration 테스트
  - `test_parse_natural_language`: 자연어 파싱
  - `test_register_to_google`: Google Calendar에 등록
  - `test_register_to_icloud`: iCloud에 등록
  - `test_auto_fill_patterns`: 사용자 패턴 기반 자동 완성

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 5.2**: 기존 add_schedule 도구 확장
  - Google/iCloud 선택 옵션 추가
  - 사용자 기본 캘린더 설정

- [ ] **Task 5.3**: 패턴 기반 자동 완성
  - MemoryManager의 patterns 활용
  - 자주 가는 장소, 기본 시간대 등

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] 실제 슬랙 → 캘린더 등록 테스트

---

### Phase 6: 통합 테스트 및 문서화
**Goal**: E2E 테스트 및 문서 정리
**Estimated Time**: 2시간
**Status**: ⏳ Pending

#### Tasks

- [ ] **Task 6.1**: E2E 테스트 작성
  - 시나리오 1: 캘린더 일정 등록 → 자동 알림
  - 시나리오 2: 슬랙 → 캘린더 등록

- [ ] **Task 6.2**: README 업데이트
  - 설정 가이드 (Google API, iCloud)
  - 사용법

- [ ] **Task 6.3**: 계획서 완료 처리
  - PLAN_master.md 업데이트
  - P-013 완료 표시

#### Quality Gate ✋
- [ ] 전체 테스트 통과
- [ ] Docker 테스트 통과
- [ ] 문서 완료

---

## 📊 Progress Tracking

### Completion Status
```
Phase 1: 인터페이스 추상화  ░░░░░░░░░░░░   0%
Phase 2: Google Calendar   ░░░░░░░░░░░░   0%
Phase 3: iCloud Calendar   ░░░░░░░░░░░░   0%
Phase 4: 트리거 시스템     ░░░░░░░░░░░░   0%
Phase 5: 슬랙 일정 등록    ░░░░░░░░░░░░   0%
Phase 6: 통합 테스트       ░░░░░░░░░░░░   0%
─────────────────────────────────────────
Total:                      ░░░░░░░░░░░░   0%
```

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 2시간 | - | - |
| Phase 2 | 4시간 | - | - |
| Phase 3 | 4시간 | - | - |
| Phase 4 | 4시간 | - | - |
| Phase 5 | 3시간 | - | - |
| Phase 6 | 2시간 | - | - |
| **Total** | 19시간 | - | - |

---

## ⚠️ Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Google API 할당량 초과 | 중 | 낮음 | 폴링 주기 조절, 캐싱 |
| iCloud 인증 문제 | 중 | 중간 | CalDAV 표준 준수, 앱 비밀번호 |
| 외부 API 장애 | 중 | 낮음 | 로컬 캐시, 폴백 로직 |
| OAuth 토큰 만료 | 낮음 | 높음 | 자동 갱신 로직 |

---

## 🔙 Rollback Strategy

Phase별 독립적 롤백 가능:
- **Phase 1**: Provider 인터페이스만 추가, 기존 코드 영향 없음
- **Phase 2-3**: 개별 Provider 삭제로 롤백
- **Phase 4**: 트리거 비활성화
- **Phase 5**: 도구 옵션 제거

---

## 📁 File Changes Summary

### 새로 생성되는 파일
```
src/services/calendar/
├── provider.py              # CalendarProvider 프로토콜
├── local_provider.py        # 기존 SQLite 래핑
├── google_provider.py       # Google Calendar 연동
├── icloud_provider.py       # iCloud Calendar 연동
└── sync_service.py          # 동기화 서비스

src/core/autonomous/triggers/
└── schedule_trigger.py      # 일정 트리거

src/core/autonomous/enrichers/
└── event_enricher.py        # 일정 정보 보강

src/core/autonomous/services/
└── clarification_service.py # 질문/응답 서비스
```

### 수정되는 파일
```
src/services/calendar/sqlite_calendar.py   # Provider 패턴 적용
src/core/tools/plugins/calendar.py         # 캘린더 선택 옵션
src/main.py                                # 동기화 서비스 초기화
pyproject.toml                             # 의존성 추가
```

---

## 🔗 Related Documents

- [PLAN_master.md](./PLAN_master.md) - 통합 계획서
- [PLAN_autonomous_core.md](./PLAN_autonomous_core.md) - 자율 판단 코어 (P-010)
- [PLAN_memory_system.md](./PLAN_memory_system.md) - 메모리 시스템 (P-011)

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [ ] 모든 Phase 완료 및 Quality Gate 통과
- [ ] Google Calendar 실제 연동 테스트
- [ ] iCloud Calendar 실제 연동 테스트
- [ ] 트리거 → 알림 E2E 테스트
- [ ] 슬랙 → 캘린더 등록 E2E 테스트
- [ ] 문서 업데이트
- [ ] PLAN_master.md 업데이트

---

**Plan Status**: ⏳ Planned
**Next Action**: Phase 1 시작 전 Google Cloud 프로젝트 설정 필요

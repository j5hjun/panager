# Implementation Plan: Core Domain Modeling

**Status**: 🔄 In Progress
**Plan ID**: PLAN_002
**Started**: 2026-01-07
**Last Updated**: 2026-01-07

---

**⚠️ CRITICAL INSTRUCTIONS**: Review this plan with the User before starting implementation.

---

## 📋 Overview

### Feature Description
Panager의 핵심 비즈니스 로직을 담을 **Domain Layer**를 구현합니다.
Clean Architecture 원칙에 따라, 이 계층은 외부 라이브러리(Slack SDK, SQLAlchemy 등)에 의존하지 않는 순수한 Python 객체(POJO/Pydantic)로 구성됩니다.

### Success Criteria
- [ ] 핵심 엔티티(`User`, `Token`, `Event`)가 Pydantic 모델로 정의됨
- [ ] 데이터 접근을 위한 추상 인터페이스(Ports)가 정의됨 (`UserRepository`, `TokenRepository`)
- [ ] 엔티티의 유효성 검사 및 비즈니스 로직에 대한 단위 테스트 통과

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Pydantic for Entities** | 타입 안전성 및 데이터 검증(Validation) 자동화 | 순수 Class보다 약간의 오버헤드 (무시 가능 수준) |
| **Abstract Base Classes (ABC)** | 의존성 역전 원칙(DIP) 준수. 구현체 교체 용이성 확보 | 인터페이스 정의에 별도 코드 필요 |

---

## 🚀 Implementation Phases

### Phase 1: User & Token Domain
**Goal**: 사용자 및 인증 토큰 모델링
**Status**: ✅ Complete

#### Tasks
- [x] **User Entity**: `src/domain/models/user.py` 생성 (slack_id, is_active 등)
- [x] **Token Entity**: `src/domain/models/token.py` 생성 (access_token, refresh_token, expires_at)
- [x] **Repository Ports**: `src/domain/ports/user_repo.py`, `token_repo.py` 인터페이스 정의

#### Quality Gate
- [x] `User` 생성 시 필수 필드 검증 테스트 통과
- [x] `Token.is_expired()` 메서드 동작 테스트 통과

---

### Phase 2: Calendar Event Domain
**Goal**: 캘린더 이벤트 모델링
**Status**: ✅ Complete

#### Tasks
- [x] **Event Entity**: `src/domain/models/event.py` 생성 (summary, start_time, end_time, location)
- [x] **Event Logic**: 이벤트 기간 계산, 중복 확인 등 도메인 로직 추가
- [x] **Repository Port**: `src/domain/ports/event_repo.py` 인터페이스 정의

#### Quality Gate
- [x] `Event`의 시작 시간이 끝 시간보다 늦을 경우 에러 발생 확인 테스트

---

## 📊 Progress Tracking

```
Phase 1: User/Token     ████████████ 100%
Phase 2: Event          ████████████ 100%
```

---

## 🔗 Related Documents
- [SRS_autonomous_panager.md](../SRS_autonomous_panager.md)

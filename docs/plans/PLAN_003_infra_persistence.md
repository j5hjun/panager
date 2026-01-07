# Implementation Plan: Infrastructure Persistence (PostgreSQL)

**Status**: 🔄 In Progress
**Plan ID**: PLAN_003
**Started**: 2026-01-07
**Last Updated**: 2026-01-07
**Estimated Completion**: 2026-01-08

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
Core Domain에서 정의한 Repository Interface(`User`, `Token`, `Event`)를 구현하는 인프라스트럭처 계층을 구축합니다.
**DO_003** 결정에 따라 **PostgreSQL**을 데이터베이스로 사용하며, **SQLAlchemy (Async)**와 **Alembic**으로 관리합니다.

### Success Criteria
- [ ] `docker-compose` 환경에 PostgreSQL 컨테이너 추가 및 구동 확인
- [ ] SQLAlchemy 비동기 엔진 연결 (`postgresql+asyncpg`) 및 세션 설정 완료
- [ ] Alembic을 통한 초기 스키마(User, Token, Event) 마이그레이션 적용
- [ ] Repository Adapter 구현체 작성 및 통합 테스트(Integration Test) 100% 통과

### User Impact
- 데이터 영속성 확보로 인해 서버 재시작 시에도 사용자 정보와 일정 데이터가 유지됩니다.
- 동시성 처리가 강화되어 다중 사용자 요청을 안정적으로 처리할 수 있습니다.

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **PostgreSQL 15+** | DO_003에 따른 결정. 데이터 안정성 및 확장성 확보 | 초기 리소스 사용량 증가 (Docker로 해결) |
| **asyncpg** | 성능이 가장 우수한 Python 비동기 드라이버 | 빌드 의존성 존재 (Docker 환경에서 제어 가능) |
| **Pydantic V2** | SQLAlchemy 모델과 Pydantic 모델 간의 변환 최적화 | - |

---

## 📦 Dependencies

### Required Before Starting
- [x] PLAN_001 (Docker Environment)
- [x] PLAN_002 (Core Domain Entities & Ports)
- [x] DO_003 (Persistence Strategy Decision)

### External Dependencies
- sqlalchemy: ^2.0
- asyncpg: ^0.29
- alembic: ^1.13
- pytest-asyncio: ^0.23 (Test)

---

## 🧪 Test Strategy

### Testing Approach
**TDD Principle**: Write tests FIRST, then implement to make them pass

### Test Pyramid for This Feature
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Unit Tests** | N/A | (Core 로직은 PLAN_002에서 완료됨) |
| **Integration Tests** | 100% (Connections) | DB 연결, 스키마 생성, CRUD 동작 검증 |
| **E2E Tests** | N/A | 이번 단계에서는 제외 |

### Test File Organization
```
tests/
├── integration/
│   ├── test_db_connection.py  (Phase 1)
│   └── test_repositories.py   (Phase 3)
```

### Coverage Requirements by Phase
- **Phase 1 (DB Setup)**: DB 연결 성공 여부 100% 검증
- **Phase 2 (Schema)**: Alembic 마이그레이션 성공 여부 검증
- **Phase 3 (Repositories)**: Adapter CRUD 로직 100% 커버리지

---

## 🚀 Implementation Phases

### Phase 1: DB Infrastructure Setup
**Goal**: PostgreSQL 컨테이너 실행 및 애플리케이션 연결
**Estimated Time**: 2 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 1.1**: Write connection test
  - File(s): `tests/integration/test_db_connection.py`
  - Expected: Fails because DB config and driver dependecies are missing
  - Details: `SELECT 1` query execution test using `get_db` dependency

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 1.2**: Update Docker Compose
  - File(s): `docker-compose.local.yml`, `docker-compose.yml`
  - Goal: Add `postgres` service with volume persistence
- [ ] **Task 1.3**: Add Dependencies and Config
  - File(s): `pyproject.toml`, `.env.local`, `src/infrastructure/db.py`
  - Goal: Install `asyncpg/sqlalchemy`, implement `AsyncEngine` and session factory

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 1.4**: Optimize Config
  - File(s): `src/infrastructure/db.py`
  - Goal: Ensure proper connection pooling settings

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed to Phase 2 until ALL checks pass**

- [ ] **TDD Compliance**: Red-Green-Refactor cycle followed
- [ ] **Build**: `docker compose up -d` starts successfully
- [ ] **All Tests Pass**: `pytest tests/integration/test_db_connection.py` PASSED
- [ ] **Linting**: `ruff check .` PASSED

---

### Phase 2: Schema & Migration
**Goal**: 테이블 스키마 정의 및 적용 (Alembic)
**Estimated Time**: 2 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: Verify Table Existence (Manual/Script)
  - Details: Connect to DB and check for `users` table -> Should not exist

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.2**: Define ORM Models
  - File(s): `src/infrastructure/schema.py`
  - Goal: Map `User`, `Token`, `Event` entities to SQLAlchemy Base
- [ ] **Task 2.3**: Configure Alembic
  - File(s): `alembic.ini`, `migrations/env.py`
  - Goal: Support async migration
- [ ] **Task 2.4**: Run Migration
  - Command: `alembic revision --autogenerate`, `alembic upgrade head`

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 2.5**: Review Migration Script
  - File(s): `migrations/versions/*.py`
  - Goal: Ensure generated SQL is correct and readable

#### Quality Gate ✋

- [ ] **TDD Compliance**: Verified schemas before and after
- [ ] **Functionality**: `alembic upgrade head` runs without error
- [ ] **Verification**: Tables `users`, `tokens`, `events` exist in Postgres

---

### Phase 3: Repository Implementation
**Goal**: 도메인 포트 구현 (Adapter)
**Estimated Time**: 4 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 3.1**: Integration Tests for Repositories
  - File(s): `tests/integration/test_repositories.py`
  - Details: Test cases for `save`, `get_by_id`, `is_expired` logic with real DB
  - Expected: Fails (ImportError or NotImplementedError)

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 3.2**: Implement UserRepository
  - File(s): `src/infrastructure/persistence/user_repo.py`
- [ ] **Task 3.3**: Implement TokenRepository
  - File(s): `src/infrastructure/persistence/token_repo.py`
- [ ] **Task 3.4**: Implement EventRepository
  - File(s): `src/infrastructure/persistence/event_repo.py`

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 3.5**: Common Repository Pattern
  - Goal: Extract common CRUD logic if possible (Mixin)

#### Quality Gate ✋

- [ ] **TDD Compliance**: Tests written first
- [ ] **All Tests Pass**: `pytest tests/integration/test_repositories.py` PASSED (100%)
- [ ] **Linting**: No ruff errors

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **DB Container Connect Fail** | Medium | High | `docker-compose` 설정 검증 및 `depends_on` 헬스체크 추가 |
| **Async Driver Compatibility** | Low | Medium | `asyncpg` 버전 명시 및 최소한의 DB 기능만 초기 사용 |
| **Test Data Pollution** | High | Medium | 통합 테스트 시 `pytest-asyncio` fixture로 트랜잭션 롤백 보장 |

---

## 🔄 Rollback Strategy

### If Phase 1 Fails
**Steps to revert**:
- Undo code changes in: `src/infrastructure/db.py`, `docker-compose*.yml`
- Remove dependencies: `poetry remove asyncpg sqlalchemy`
- Stop container: `docker compose down`

### If Phase 2 Fails
**Steps to revert**:
- Database rollback: `alembic downgrade base`
- Undo code changes in: `src/infrastructure/schema.py`, `migrations/`

### If Phase 3 Fails
**Steps to revert**:
- Remove files: `src/infrastructure/persistence/*.py`
- Discard git changes

---

## 📊 Progress Tracking

### Completion Status
- **Phase 1**: ⏳ 0% | 🔄 50% | ✅ 100%
- **Phase 2**: ⏳ 0% | 🔄 50% | ✅ 100%
- **Phase 3**: ⏳ 0% | 🔄 50% | ✅ 100%

**Overall Progress**: 0% complete

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 2 hours | - | - |
| Phase 2 | 2 hours | - | - |
| Phase 3 | 4 hours | - | - |
| **Total** | 8 hours | - | - |

---

## 📝 Notes & Learnings

### Implementation Notes
- (To be filled)

### Blockers Encountered
- (To be filled)

### Improvements for Future Plans
- (To be filled)

---

## 📚 References

### Documentation
- [SQLAlchemy Asyncio Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Async Tutorial](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic)

### Related Issues
- DO_003: Persistence Strategy

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [ ] All phases completed with quality gates passed
- [ ] Full integration testing performed
- [ ] Documentation updated
- [ ] Security review completed (DB Credentials safety)
- [ ] Plan document archived for future reference

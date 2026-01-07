# Implementation Plan: Infrastructure Persistence (PostgreSQL)

**Status**: 🔄 In Progress
**Plan ID**: PLAN_003
**Started**: 2026-01-07
**Last Updated**: 2026-01-07

---

**⚠️ CRITICAL INSTRUCTIONS**: Review this plan with the User before starting implementation.

---

## 📋 Overview

### Feature Description
Core Domain에서 정의한 Repository Interface(`User`, `Token`, `Event`)를 구현하는 인프라스트럭처 레어어를 구축합니다.
**DO_003** 결정에 따라 **PostgreSQL**을 데이터베이스로 사용하며, **SQLAlchemy (Async)**와 **Alembic**으로 관리합니다.

### Success Criteria
- [ ] `docker-compose` 환경에 PostgreSQL 컨테이너 추가 및 구동 확인
- [ ] SQLAlchemy 비동기 엔진 연결 (`postgresql+asyncpg`) 및 세션 설정 완료
- [ ] Alembic을 통한 초기 스키마(User, Token, Event) 마이그레이션 적용
- [ ] Repository Adapter 구현체 작성 및 통합 테스트(Integration Test) 100% 통과

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **PostgreSQL 15+** | DO_003에 따른 결정. 데이터 안정성 및 확장성 확보 | 초기 리소스 사용량 증가 (Docker로 해결) |
| **asyncpg** | 성능이 가장 우수한 Python 비동기 드라이버 | 빌드 의존성 존재 (Docker 환경에서 제어 가능) |
| **Pydantic V2** | SQLAlchemy 모델과 Pydantic 모델 간의 변환 최적화 | - |

---

## � Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **DB Container Connect Fail** | Medium | High | `docker-compose` 설정 검증 및 `depends_on` 헬스체크 추가 |
| **Async Driver Compatibility** | Low | Medium | `asyncpg` 버전 명시 및 최소한의 DB 기능만 초기 사용 |
| **Test Data Pollution** | High | Medium | 통합 테스트 시 `pytest-asyncio` fixture로 트랜잭션 롤백 또는 DB 초기화 보장 |

---

## �🚀 Implementation Phases

### Phase 1: DB Infrastructure Setup
**Goal**: PostgreSQL 컨테이너 실행 및 애플리케이션 연결
**Test Strategy**:
- **Test File**: `tests/integration/test_db_connection.py`
- **Coverage Target**: 100% (DB 연결 성공 여부)
- **Scenarios**: `SELECT 1` 쿼리 실행 성공
**Rollback Strategy**: `docker compose down -v` 로 Volume 삭제 및 설정 파일 원복

#### Tasks
1. **RED Tasks**
   - [ ] `tests/integration/test_db_connection.py` 작성 (DB 연결 시도 -> 실패 예상)

2. **GREEN Tasks**
   - [ ] `docker-compose.local.yml`, `docker-compose.yml`에 `postgres` 서비스 추가
   - [ ] `.env.local`에 `DB_URL` 추가 (Settings 업데이트)
   - [ ] `src/infrastructure/db.py`에 Async Engine 및 `get_db` 구현
   - [ ] 의존성 추가: `sqlalchemy`, `asyncpg`

3. **REFACTOR Tasks**
   - [ ] DB Session Context Manager 최적화

#### Quality Gate
- [ ] `docker compose up -d db` 성공
- [ ] `pytest tests/integration/test_db_connection.py` 통과

---

### Phase 2: Schema & Migration
**Goal**: 테이블 스키마 정의 및 적용 (Alembic)
**Test Strategy**:
- **Test File**: N/A (Alembic 실행 결과로 검증)
- **Scenarios**: `users`, `tokens`, `events` 테이블 생성 확인
**Rollback Strategy**: `alembic downgrade base` 실행

#### Tasks
1. **RED Tasks**
   - [ ] (수동) DB 접속 시 테이블 없음 확인

2. **GREEN Tasks**
   - [ ] `src/infrastructure/schema.py` 작성 (ORM 모델)
   - [ ] `alembic init -t async` 및 환경 설정 (`env.py`)
   - [ ] 초기 마이그레이션 파일 생성 및 적용 (`upgrade head`)

3. **REFACTOR Tasks**
   - [ ] 마이그레이션 스크립트 가독성 점검

#### Quality Gate
- [ ] DB 도구로 접속 시 테이블 생성 확인

---

### Phase 3: Repository Implementation
**Goal**: 도메인 포트 구현 (Adapter)
**Test Strategy**:
- **Test File**: `tests/integration/test_repositories.py`
- **Coverage Target**: >90% (Adapter 코드)
- **Scenarios**: 
    - User 저장 및 조회
    - Token 저장, 조회, 삭제
    - Event 저장 및 범위 조회
**Rollback Strategy**: 구현 파일 삭제 및 Git Revert

#### Tasks
1. **RED Tasks**
   - [ ] `tests/integration/test_repositories.py` 작성 (구현체 없음 -> Import Error 또는 실패)

2. **GREEN Tasks**
   - [ ] `src/infrastructure/persistence/user_repo.py` 구현
   - [ ] `src/infrastructure/persistence/token_repo.py` 구현
   - [ ] `src/infrastructure/persistence/event_repo.py` 구현

3. **REFACTOR Tasks**
   - [ ] 중복 쿼리 로직 제거 (Mixin 활용 고려)

#### Quality Gate
- [ ] `pytest tests/integration/test_repositories.py` 전 항목 통과

---

## 📊 Progress Tracking

```
Phase 1: DB Setup       ⬜⬜⬜⬜⬜ 0%
Phase 2: Schema/Mig     ⬜⬜⬜⬜⬜ 0%
Phase 3: Repositories   ⬜⬜⬜⬜⬜ 0%
```

---

## 🔗 Related Documents
- [PLAN_002_core_domain.md](./PLAN_002_core_domain.md)
- [DO_003_persistence_strategy.md](../designs/DO_003_persistence_strategy.md)

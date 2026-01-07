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
**DO_002** 결정에 따라 **PostgreSQL**을 데이터베이스로 사용하며, **SQLAlchemy (Async)**와 **Alembic**으로 관리합니다.

### Success Criteria
- [ ] `docker-compose` 환경에 PostgreSQL 컨테이너 추가 및 구동 확인
- [ ] SQLAlchemy 비동기 엔진 연결 (`postgresql+asyncpg`) 및 세션 설정 완료
- [ ] Alembic을 통한 초기 스키마(User, Token, Event) 마이그레이션 적용
- [ ] Repository Adapter 구현체 작성 및 통합 테스트(Integration Test) 통과

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **PostgreSQL 15+** | DO_002에 따른 결정. 데이터 안정성 및 확장성 확보 | 초기 리소스 사용량 증가 (Docker로 해결) |
| **asyncpg** | 성능이 가장 우수한 Python 비동기 드라이버 | 빌드 의존성 존재 (Docker 환경에서 제어 가능) |
| **Pydantic V2** | SQLAlchemy 모델과 Pydantic 모델 간의 변환 최적화 | - |

---

## 🚀 Implementation Phases

### Phase 1: DB Infrastructure Setup
**Goal**: PostgreSQL 컨테이너 실행 및 애플리케이션 연결
**Status**: ⏳ Pending

#### Tasks
- [ ] **Docker**: `docker-compose.local.yml`에 `db` 서비스(Postgres) 추가
- [ ] **Docker**: `docker-compose.yml` (Prod)에 `db` 서비스 추가 및 Volume 영속화 설정
- [ ] **Env**: `.env.local`에 `DB_URL` 등 접속 정보 추가 (Configuration 업데이트)
- [ ] **Code**: `src/infrastructure/db.py`에 Async Engine 및 `get_db` 구현

#### Quality Gate
- [ ] `docker compose up -d db` 성공
- [ ] 애플리케이션에서 `SELECT 1` 쿼리 테스트 성공

---

### Phase 2: Schema & Migration
**Goal**: 테이블 스키마 정의 및 적용 (Alembic)
**Status**: ⏳ Pending

#### Tasks
- [ ] **Dependencies**: `sqlalchemy`, `asyncpg`, `alembic` 설치 (`poetry add`)
- [ ] **ORM Models**: `src/infrastructure/schema.py` 작성 (Base 상속, 테이블 매핑)
- [ ] **Alembic Init**: `alembic init -t async` 및 `env.py` 설정 (MetaData 연동)
- [ ] **Migrate**: 초기 리비전 생성 및 `upgrade head` 실행

#### Quality Gate
- [ ] DB 도구(CLI/GUI)로 접속 시 `users`, `tokens`, `events` 테이블 생성 확인

---

### Phase 3: Repository Implementation
**Goal**: 도메인 포트 구현 (Adapter)
**Status**: ⏳ Pending

#### Tasks
- [ ] **UserRepository**: `src/infrastructure/persistence/user_repo.py` 구현
- [ ] **TokenRepository**: `src/infrastructure/persistence/token_repo.py` 구현
- [ ] **EventRepository**: `src/infrastructure/persistence/event_repo.py` 구현
- [ ] **Test**: `tests/integration/` 디렉토리에 통합 테스트 작성 (CRUD 검증)

#### Quality Gate
- [ ] 통합 테스트(`pytest tests/integration`) 100% 통과

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
- [DO_002_persistence_strategy.md](../designs/DO_002_persistence_strategy.md)

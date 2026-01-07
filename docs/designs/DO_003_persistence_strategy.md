# Design Options: Persistence Strategy

**Date**: 2026-01-07
**Author**: Antigravity
**Status**: Draft

---

## 1. Context and Problem Statement
Panager는 사용자 정보, 인증 토큰, 캘린더 이벤트를 저장해야 합니다.
현재 프로젝트는 초기 단계이며, 로컬 개발 및 소규모 배포(사용자 1~10명 내외)를 목표로 합니다.
적절한 데이터베이스 엔진과 ORM(Object-Relational Mapping) 전략을 결정해야 합니다.

## 2. Requirements (Constraints)
- **비동기(Async) 지원**: FastAPI와 호환되는 Non-blocking I/O 필수
- **설정 간소화**: 배포 및 유지보수가 쉬워야 함 (NFR-005)
- **데이터 무결성**: 관계형 데이터(User-Token) 표현 가능해야 함
- **마이그레이션**: 스키마 변경 이력 관리가 되어야 함

---

## 3. Options Analysis

### Option A: SQLite (With Wal Mode)
파일 기반의 임베디드 데이터베이스입니다.
- **Stack**: SQLite + `aiosqlite` + SQLAlchemy
- **Pros**:
    - 별도의 서버 프로세스가 필요 없음 (설정 제로)
    - 백업이 단순함 (파일 복사)
    - Python 내장 라이브러리로 접근성 높음
- **Cons**:
    - 동시 쓰기(Write) 성능 제약 (WAL 모드로 완화 가능하지만 한계 있음)
    - 일부 고급 SQL 기능 미지원 (PostgreSQL 대비)

### Option B: PostgreSQL (Dockerized)
강력한 엔터프라이즈급 오픈소스 RDBMS입니다.
- **Stack**: PostgreSQL Container + `asyncpg` + SQLAlchemy
- **Pros**:
    - 강력한 동시성 제어 및 트랜잭션 관리
    - 풍부한 데이터 타입 (JSONB 등) 및 확장성
- **Cons**:
    - 리소스(RAM/CPU) 소모가 더 큼
    - 운영 복잡도 증가 (별도 컨테이너 관리, 백업 정책 수립 필요)

### Option C: NoSQL / Document Store (e.g., TinyDB, MongoDB)
JSON 문서 형태의 저장소입니다.
- **Stack**: TinyDB or MongoDB
- **Pros**:
    - 스키마가 유연함 (Schema-less)
    - 초기 개발 속도가 빠를 수 있음
- **Cons**:
    - 관계(Relation) 표현이 어려움 (User-Token Join 등)
    - TinyDB는 성능 이슈, MongoDB는 운영 복잡도 있음
    - ACID 트랜잭션 보장이 약하거나 복잡함

---

## 5. Decision
**Selection**: Option B (PostgreSQL)

**Justification**:
서비스의 장기적인 성장과 데이터 안정성을 고려하여 엔터프라이즈급 RDBMS인 PostgreSQL을 선택합니다.
초기 리소스 비용이 들더라도, 동시성 처리와 미래의 확장을 위해 처음부터 견고한 기반을 다지는 것이 중요합니다.
- [ ] Option A: SQLite
- [x] Option B: PostgreSQL
- [ ] Option C: NoSQL

# DO-001: Architecture & Data Sync Strategy

**Version**: 1.1
**Date**: 2026-01-08
**Status**: APPROVED

---

## 1. Problem Statement
**"사용자에게 능동적으로 정보를 제공하는 AI 에이전트"**를 만들기 위해 해결해야 할 두 가지 기술적 난제가 있습니다.
1.  **Code Structure**: 복잡한 AI 로직과 외부 API(Google, Slack) 연동 코드를 어떻게 유연하게 관리할 것인가?
2.  **Data Synchronization**: 캘린더의 변동 사항을 가장 빠르고 효율적으로 감지(Real-time)할 방법은 무엇인가?

---

## 2. Options Analysis

### Issue A: Code Architecture (코드 구조)

#### Option A-1: MVC (Model-View-Controller)
전통적인 웹 프레임워크(Django, Rails) 스타일.
*   **구조**: `routers`(View)가 비즈니스 로직과 DB 처리까지 모두 담당.
*   **Pros**: 직관적이고 초기 구현 속도가 매우 빠름.
*   **Cons**: 프로젝트가 커질수록 Router 파일이 방대해짐(Fat Controller). AI 로직과 API 호출 코드가 뒤섞여 유지보수가 어려움.

#### Option A-2: Simplified DDD (Domain-Driven Design) - **[Recommended]**
비즈니스 로직을 'Service Layer'로 분리하는 방식.
*   **구조**: `routers` -> `services`(비즈니스 로직) -> `db`(데이터 접근).
*   **Pros**: 
    *   **관심사의 분리**: Slack 로직(`slack_service.py`)과 Calendar 로직(`calendar_service.py`)이 명확히 나뉨.
    *   **재사용성**: 챗봇에서도, 백그라운드 작업에서도 동일한 Service 함수를 호출 가능.
*   **Cons**: MVC보다 파일 개수가 많아짐.

### Issue B: Calendar Sync Strategy (동기화 전략)

#### Option B-1: Polling (주기적 조회)
서버가 1분마다 "변경된 거 있니?"라고 Google API를 호출.
*   **Pros**: 구현이 매우 단순함. 로컬 개발 환경 제약 없음.
*   **Cons**:
    *   **API Quota 낭비**: 변동이 없어도 계속 호출하여 구글 API 한도 초과 위험.
    *   **지연 시간**: 최대 1분의 알림 지연 발생.

#### Option B-2: Webhook (Event-Driven) - **[Recommended]**
Google이 변동 발생 시 우리 서버로 알림(POST 요청)을 보냄.
*   **Pros**:
    *   **Real-time**: 변동 즉시 알림 발송 가능.
    *   **Efficiency**: 변동이 있을 때만 API를 호출하므로 효율적.
*   **Cons**: 로컬 개발 시 터널링(Ngrok) 필요, 보안 검증 로직 구현 필요.

---

## 3. Decision & Rationale

### 3.1 Decisions
1.  **Architecture**: **Option A-2 (Simplified DDD)**
2.  **Sync Strategy**: **Option B-2 (Webhook with SyncToken)**

### 3.2 Rationale
*   **확장성**: 추후 'Google Tasks'나 'Email' 등 다른 도구가 추가될 때, Service Layer 패턴이 훨씬 유연하게 대응할 수 있습니다.
*   **사용자 경험**: "Proactive"한 비서라면 사용자가 일정을 바꾸자마자 반응해야 하므로(Real-time), Webhook 방식이 필수적입니다. API 비용 절감을 위해서도 `SyncToken`을 활용한 델타 업데이트가 최선입니다.

---

## 4. Detailed Design
상세한 데이터베이스 스키마와 API 명세, 코드 구조는 별도의 명세서인 **[SPEC-001: System Specification](../specs/SPEC_001_system_design.md)**에서 다룹니다.

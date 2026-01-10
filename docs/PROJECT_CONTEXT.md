# Project Context & Agent Onboarding

**Last Updated**: 2026-01-10
**Current Phase**: ✅ MVP Setup Completed (Maintenance & Feature Expansion)

> **🚨 New Agent Checklist (작업 전 필독)**
>
> 작업을 시작하기 전에 다음 절차를 반드시 따르십시오:
> 1. **전체 문서 분석**: **`docs/` 하위의 폴더들**(`requirements/`, `designs/`, `specs/`, `plans/`, `templates/`)에 있는 **모든 파일**을 읽고 맥락을 파악하십시오.
> 2. **연속적 수행**: 만약 한 번에 모든 파일을 분석하지 못했다면, **반드시 이어서 나머지 파일들도 분석**하여 전체 맥락을 파악한 뒤 작업을 시작해야 합니다.

---

## 1. Project Overview
**Proactive Manager (Panager)**는 사용자의 캘린더와 상황을 능동적으로 분석하여 필요한 정보를 먼저 제공하는 AI 서비스입니다.

### Core Philosophy
*   **Proactive**: 묻기 전에 알려준다.
*   **Privacy**: 개인 데이터는 안전하게.
*   **Async**: 모든 처리는 비동기로.

---

## 2. Current Status (Where are we?)

### Project Documentation Map
현재 프로젝트의 모든 핵심 문서 목록과 요약입니다. 에이전트는 작업 전 이 문서들을 확인해야 합니다.

#### 1. Requirements (`docs/requirements/`)
*   **[SRS-001 MVP Setup](requirements/SRS_001_mvp_setup.md)**: Slack 봇과 Google Calendar 연동을 위한 MVP 기능 요구사항 및 사용자 스토리.

#### 2. Designs (`docs/designs/`)
*   **[DO-001 Architecture Strategy](designs/DO_001_architecture_and_schema.md)**: Simplified DDD 패턴 도입 및 Webhook 기반 동기화 방식에 대한 의사결정 기록.

#### 3. Specifications (`docs/specs/`)
*   **[SPEC-000 CI/CD Workflow](specs/SPEC_000_cicd_workflow.md)**: Git 브랜치 전략, 커밋 메시지 규칙, CI/CD 파이프라인 정의.
*   **[SPEC-001 System Design](specs/SPEC_001_system_design.md)**: 데이터베이스 스키마(ERD), API 엔드포인트 명세, 패키지 구조 상세.

#### 4. Plans (`docs/plans/`)
*   **[PLAN-001 MVP Implementation](plans/PLAN_001_mvp_implementation.md)**: MVP 구축을 위한 단계별 실행 계획. (✅ Completed on 2026-01-10)

#### 5. Templates (`docs/templates/`)
*   `SKILL.md`: 기능 기획 및 계획 수립을 위한 AI 에이전트용 가이드.
*   각종 문서 표준 템플릿(`SRS`, `Design Options`, `Plan`) 포함.

### Architecture Snapshot
*   **Stack**: FastAPI (Async), PostgreSQL, Slack Socket Mode, Ngrok
*   **Key Pattern**: Webhook-based Event Driven (Using Push Notifications)

---

## 3. Next Immediate Tasks
> MVP 구축이 완료되었습니다. 다음 작업은 새로운 마일스톤(예: AI 분석 기능)을 정의하고 시작하는 것입니다.

### ✅ Phase 1: Environment & Foundation (Completed)
*   [x] Task 1.1: Project Skeleton (Hello World)
*   [x] Task 1.2: CI/CD Setup
*   [x] Task 1.3: Docker Compose

### ✅ Phase 2: Database & Models (Completed)
*   [x] **Task 2.1**: Async Session Test (Connection Check)
*   [x] **Task 2.2**: Models Implementation (User, Credential)
*   [x] **Task 2.3**: Alembic Migrations

### ✅ Phase 3: Domain Services (Completed)
*   [x] **Test 3.1**: Security Service Test
*   [x] **Test 3.2**: Auth Service Test
*   [x] **Task 3.6**: Slack Logic Implementation

### ✅ Phase 4: API Integration (Completed)
*   [x] **Test 4.1**: Login Redirect Endpoint Test
*   [x] **Test 4.2**: Webhook Processing Test
*   [x] **Task 4.3**: Auth Router Implementation

### ✅ Phase 5: Calendar Watch & UX (Completed)
*   [x] **Task 5.2**: Calendar Watch Implementation
*   [x] **Task 5.3**: Deep Link & HTML Success Page
*   [x] **Task 5.4**: Ngrok Tunneling Setup


---

## 4. Development Rules
*   **Documentation First**: 코드 작성 전 SRS -> DO -> PLAN 업데이트 필수.
*   **Planning Standard**: 모든 구현 계획(PLAN)은 **[`docs/templates/SKILL.md`](templates/SKILL.md)** 표준을 따라 작성해야 함.
*   **Test Driven**: 테스트 코드를 통해 기능을 검증.
*   **Conventions**: Google Python Style Guide 준수.

# Software Requirements Specification (SRS): Panager (Proactive AI Manager)

**Version**: 1.0
**Status**: Draft
**Last Updated**: 2026-01-07

---

## 1. Introduction

### 1.1 Purpose
본 문서는 사용자(User)의 캘린더 이벤트를 감지하여 능동적으로 필요한 정보를 수집하고, 적절한 시점에 리마인더나 제안을 제공하는 자율형 AI 에이전트 'Panager'의 요구사항을 정의합니다.

### 1.2 Scope
- **핵심 트리거**: 사용자의 캘린더 일정 변경(생성, 수정, 삭제) 시에만 시스템이 능동적으로 동작을 시작합니다.
- **완전 자율성**: "언제 알림을 보낼지", "무엇을 물어볼지"에 대한 하드코딩된 규칙(Rule)을 배제하고, AI가 상황을 판단하여 결정합니다.
- **인터페이스**: 초기 진입 장벽을 낮추기 위해 기존 도구(Slack, Google Calendar)를 활용합니다.
- **대상 사용자**: 다중 사용자(Multi-user)를 지원합니다.

---

## 2. Overall Description

### 2.1 User Characteristics
- 일정이 많고 관리에 어려움을 겪는 사용자
- 새로운 앱 설치나 학습에 거부감이 있고, 기존 메신저(Slack)와 캘린더 환경을 선호하는 사용자

### 2.2 Product Functions
1.  **Calendar Monitoring**: 사용자의 캘린더 변경사항을 실시간(또는 준실시간)으로 감지
2.  **Proactive Inquiry**: 일정의 맥락을 파악하여 부족한 정보나 필요한 준비 사항을 사용자에게 능동적으로 질문
3.  **Contextual Reminder**: 단순 시간 알림이 아닌, 사용자의 답변과 상황을 고려한 '맥락적 리마인더' 제공
4.  **Natural Language Commands**: Slack 대화를 통해 일정 등록/수정/삭제 수행

### 2.3 General Constraints
- **Rule-Free**: `if time == 9:00 then alert`와 같은 고정 규칙 사용 금지. 모든 판단은 AI의 추론(Reasoning)에 의존해야 함.
- **Privacy**: 다중 사용자 환경이므로, 개인의 일정과 대화 내용은 철저히 격리되어야 함.

---

## 3. Specific Requirements

### 3.1 Functional Requirements (FR)

#### FR-001: 캘린더 이벤트 감지 (Event Trigger)
- **FR-001-1**: 시스템은 등록된 사용자의 Google Calendar 변경 사항(생성, 수정, 삭제)을 감지해야 한다.
- **FR-001-2**: 변경 감지 시, 해당 이벤트의 메타데이터(제목, 시간, 장소, 설명 등)를 AI 판단 모듈로 전달해야 한다.

#### FR-002: 자율적 판단 및 질의 (Autonomous Reasoning & Inquiry)
- **FR-002-1**: AI는 이벤트 정보를 분석하여 사용자에게 "질문이 필요한지", "무시해도 되는지" 스스로 판단해야 한다. (예: "미팅 준비물은 챙기셨나요?" 같은 질문 생성)
- **FR-002-2**: 질문이 필요하다고 판단된 경우, Slack을 통해 사용자에게 자연어로 질문해야 한다.

#### FR-003: 맥락적 리마인더 (Contextual Reminder)
- **FR-003-1**: 사용자의 답변을 바탕으로, AI는 "언제 다시 알림을 줄지" 스스로 결정하여 스케줄링해야 한다.
- **FR-003-2**: 결정된 시간에 Slack으로 리마인더 메시지를 발송해야 한다.

#### FR-004: 대화형 일정 관리 (Conversational Management)
- **FR-004-1**: 사용자가 Slack에서 자연어로 일정 "등록", "변경", "삭제"를 요청하면 이를 Calendar API를 통해 수행해야 한다.
- **FR-004-2**: Calendar API 수행 결과는 다시 FR-001의 트리거로 작용하지 않아야 한다(무한 루프 방지) 또는 AI가 "내가 한 작업"임을 인지해야 한다.

#### FR-005: 다중 사용자 지원 (Multi-tenancy)
- **FR-005-1**: 각 사용자는 개별적으로 자신의 Google Calendar 계정을 연결(OAuth)할 수 있어야 한다.
- **FR-005-2**: Slack ID와 Calendar 계정은 1:1로 매핑되어, 타인의 일정에 접근할 수 없어야 한다.

---

### 3.2 Non-Functional Requirements (NFR)

#### NFR-001: Usability (사용성)
- 별도의 회원가입 절차 없이 Slack 계정과 OAuth만으로 사용이 가능해야 한다.

#### NFR-002: Latency (응답성)
- 일정 변경 감지 후 AI 판단까지 30초 이내에 이루어져야 한다. (Webhook 사용 권장)

#### NFR-003: Expandability (확장성)
- 향후 Google Calendar 외 다른 캘린더나 메신저(디스코드 등)로 확장 가능하도록 인터페이스가 추상화되어야 한다.

#### NFR-004: Deployment Automation (배포 자동화)
- **NFR-004-1**: `main` 브랜치는 보호되며, CI(`test`)를 통과해야만 머지할 수 있다.
- **NFR-004-2**: CI 성공 시 Docker 이미지를 빌드하여 GHCR(GitHub Container Registry)에 푸시해야 한다.
- **NFR-004-3**: 운영 서버 배포는 무중단(Zero-downtime)으로 이루어져야 하며, 실패 시 자동으로 이전 버전으로 롤백되어야 한다.

#### NFR-005: Configuration Management (설정 관리)
- **NFR-005-1**: 로컬 개발 환경용 설정 파일은 `.local` 접미사를 사용한다. (예: `docker-compose.local.yml`, `.env.local`)
- **NFR-005-2**: 운영 환경 설정은 배포 파이프라인 비밀 변수(Secrets) 등을 통해 주입하며, 소스 코드에 포함하지 않는다.

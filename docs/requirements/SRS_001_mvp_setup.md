# SRS-001: Foundational Setup & Calendar Integration

**Version**: 1.0
**Date**: 2026-01-08
**Status**: APPROVED

---

## 1. Introduction

### 1.1 Purpose
본 문서는 "Proactive Manager(Panager)"의 초기 MVP(Minimum Viable Product)를 위한 요구사항을 정의한다.
핵심 목표는 **Slack을 통한 사용자 소통**, **Google Calendar 연동**, 그리고 **캘린더 변경 사항의 실시간 알림** 구현이다.

### 1.2 Scope
*   **포함**: Slack 봇(Socket Mode), Google OAuth 2.0 인증 서버, Google Calendar 변경 감지(Webhook Only), 기본 캘린더 조회.
*   **제외**: 복잡한 자연어 추론(LLM)을 통한 일정 수정(다음 단계), 다중 캘린더 복합 분석.

---

## 2. Overall Description

### 2.1 Product Perspective
이 시스템은 독립적인 Docker Container로 동작하며, Slack API와 Google Calendar API의 중간 매개체(Middleware) 역할을 수행한다.

### 2.2 User Requirements (User Stories)
1.  **Slack 대화**: 사용자는 Slack DM을 통해 봇과 1:1로 대화할 수 있어야 한다.
2.  **계정 연결**: 사용자가 "구글 로그인"이라고 입력하면, 안전한 인증 링크를 제공받아 자신의 구글 캘린더를 연결할 수 있어야 한다.
3.  **변경 알림**: 사용자는 자신의 구글 캘린더에서 일정이 추가/변경/삭제되었을 때, Slack으로 해당 내역을 알림 받을 수 있어야 한다.

---

## 3. Specific Requirements

### 3.1 External Interface Requirements

#### 3.1.1 Interfaces
*   **SI-01 (Slack)**: Slack Socket Mode를 사용하여 방화벽/NAT 내부에서도 이벤트를 수신한다.
*   **SI-02 (Google Auth)**: `OAuth 2.0 Web Server Flow`를 준수한다. (Scopes: `calendar.readonly`, `calendar.events`)
*   **SI-03 (Google Webhook)**: Google Calendar `watch` API를 통해 변경 사항을 수신한다. (개발 환경에서도 Ngrok 터널링을 통해 Webhook 수신 필수)

### 3.2 Functional Requirements

#### 3.2.1 Slack Integration
*   **FR-Slack-01**: 봇은 멘션 없이도 DM 채널의 메시지를 수신해야 한다 (`message.im` 이벤트).
*   **FR-Slack-02**: 모든 처리는 비동기(Async)로 동작하여 Slack의 3초 응답 제한(Timeout)을 준수해야 한다.

#### 3.2.2 Google Authentication
*   **FR-Auth-01 (Login Trigger)**: 사용자가 "로그인", "구글 계정 연결" 등 자연스러운 대화형 키워드를 입력하면, 시스템은 이를 인식하여 OAuth 인증 링크를 버튼 형태로 응답해야 한다. (Slash Command 사용 금지)
*   **FR-Auth-02 (Callback)**: Google 로그인 완료 후 리다이렉트된 코드(Code)를 교환하여 Refresh Token을 획득해야 한다.
*   **FR-Auth-03 (Security)**: 획득한 토큰은 암호화(AES-256 등)하여 데이터베이스에 저장해야 한다.
*   **FR-Auth-04 (Environment)**: Redirect URI는 환경변수(`REDIRECT_URI`)에 따라 로컬(`localhost`)과 배포 환경을 구분해야 한다.

#### 3.2.3 Calendar Sync & Notification
*   **FR-Sync-01 (Change Detection)**: Google Calendar의 변경 사항이 감지되면, `syncToken`을 사용하여 **변경된 이벤트만** 조회해야 한다.
*   **FR-Sync-02 (Notification)**: 변경된 이벤트의 핵심 정보(제목, 시간, 상태)를 요약하여 해당 사용자에게 Slack DM을 발송해야 한다.
    *   *Input*: Google Calendar Webhook Payload
    *   *Processing*: 변경된 일정 파싱 -> 메시지 포맷팅
    *   *Output*: Slack Message "📅 일정이 생성되었습니다: [제목] (시간)"

### 3.3 Database Requirements (Logical)
*   **Users**: Slack User ID (Primary Key)
*   **Credentials**: User ID (FK), Encrypted Refresh Token, Access Token
*   **SyncStates**: User ID (FK), Resource ID, Sync Token (마지막 동기화 시점 기록용)

### 3.4 Technical Constraints
*   **TC-01 (Docker)**: `docker-compose.yml`(Prod)과 `docker-compose.local.yml`(Dev)로 구성을 분리한다.
*   **TC-02 (Env)**: `.env` 파일은 git에 포함되지 않아야 하며, `.env.local`로 로컬 설정을 덮어쓸 수 있어야 한다.

---

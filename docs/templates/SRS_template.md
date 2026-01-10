# Software Requirements Specification (SRS) for [Project Name]

**Version**: 1.0
**Date**: YYYY-MM-DD
**Author**: [Author Name]
**Status**: DRAFT

---

## 1. Introduction (소개)

### 1.1 Purpose (목적)
> 본 문서의 목적을 기술합니다. 누구를 위한 문서이며, 무엇을 정의하는지 설명합니다.
> *예: 본 문서는 'Proactive AI Manager'의 기능적/비기능적 요구사항을 정의한다.*

### 1.2 Scope (범위)
> 개발할 소프트웨어의 적용 범위와 한계를 정의합니다.
> * 포함되는 기능: (예: Slack 연동, 일정 자동 관리)*
> * 제외되는 기능: (예: 음성 인식, 모바일 앱)*

### 1.3 Definitions, Acronyms, and Abbreviations (정의 및 약어)
> 문서에서 사용하는 전문 용어나 약어를 정의합니다.
> * **LLM**: Large Language Model (거대 언어 모델)
> * **Agent**: 자율적으로 판단하고 행동하는 소프트웨어 주체
> * **Context**: 대화의 맥락 및 사용자 상태 정보

### 1.4 References (참고 자료)
> 프로젝트와 관련된 문서나 표준을 나열합니다.
> * IEEE Std 830-1998
> * Slack API Documentation
> * Google Calendar API Documentation

---

## 2. Overall Description (전반적인 설명)

### 2.1 Product Perspective (제품 조망)
> 이 시스템이 독립적인 제품인지, 더 큰 시스템의 일부인지 설명합니다. 시스템 구성도(Block Diagram)를 포함할 수 있습니다.
> *예: 본 시스템은 Docker 컨테이너 기반으로 동작하며, 외부 Slack API 및 Google API와 통신하는 독립형(Standalone) 백엔드 서비스이다.*

### 2.2 Product Functions (제품 기능 요약)
> 주요 기능을 요약합니다. 세부 사항은 3장에서 다룹니다.
> 1. 자연어 대화 처리 (NLP)
> 2. 일정 조회 및 자동 등록
> 3. 능동적 알림 (Proactive Notification)
> 4. 외부 도구(Tool) 호출 및 실행

### 2.3 User Characteristics (사용자 특성)
> 이 소프트웨어를 사용할 사용자의 유형과 기술 수준을 정의합니다.
> * 일반 사용자: Slack 사용에 익숙하며, 캘린더 관리를 필요로 함.
> * 관리자: 시스템 설정을 관리하는 기술 인력.

### 2.4 Constraints (제약 사항)
> 개발 및 운영 시 지켜야 할 제약 사항입니다.
> * **Hardware**: 로컬 개발(Mac M1) 및 소규모 클라우드 인스턴스.
> * **Technology**: Python 3.11+, FastAPI, Docker Compose.
> * **Regulatory**: Google OAuth 2.0 보안 정책 준수.
> * **API**: Slack 3초 응답 제한 (비동기 처리 필수).

### 2.5 Assumptions and Dependencies (가정 및 의존성)
> 프로젝트가 성공하기 위해 가정한 조건이나 외부 의존성입니다.
> * 사용자는 이미 Google 계정과 Slack 계정을 보유하고 있다.
> * LLM API 서비스(OpenAI/Groq)의 가동률은 99.9% 이상이다.

### 2.6 Apportioning of Requirements (요구사항의 배분)
> 현재 버전에서는 구현하지 않지만, 향후 버전에 포함될 기능이나 요구사항을 명시합니다. (Scope 축소 및 로드맵 관리)
> * *v2.0 예정: 음성 인식(STT) 및 음성 합성(TTS) 인터페이스*
> * *v2.0 예정: 다국어(영어, 일본어) 지원*

---

## 3. Specific Requirements (상세 요구사항)

### 3.1 External Interface Requirements (외부 인터페이스 요구사항)

#### 3.1.1 User Interfaces (사용자 인터페이스)
> * **UI-01**: 사용자는 Slack DM 창을 통해 봇과 대화한다.
> * **UI-02**: 복잡한 정보(일정 리스트 등)는 Slack Block Kit을 사용하여 구조화된 형태로 표시한다.

#### 3.1.2 Hardware Interfaces (하드웨어 인터페이스)
> * **HW-01**: 서버는 Docker Engine이 설치된 Linux/Unix 환경에서 동작해야 한다.

#### 3.1.3 Software Interfaces (소프트웨어 인터페이스)
> * **SI-01 (Slack)**: Slack Socket Mode를 통해 이벤트를 수신한다.
> * **SI-02 (Google)**: Google Calendar API v3를 REST 방식으로 호출한다.
> * **SI-03 (LLM)**: OpenAI 호환 API 인터페이스를 사용하여 추론 요청을 보낸다.

#### 3.1.4 Communications Interfaces (통신 인터페이스)
> * **CI-01**: 모든 외부 통신은 HTTPS (TLS 1.2+) 프로토콜을 사용한다.
> * **CI-02**: 로컬 개발 시 Ngrok 터널링을 통해 Oauth Callback을 수신한다.

### 3.2 Functional Requirements (기능 요구사항)
> 개별 기능에 대한 상세 요구사항을 정의합니다. IEEE 표준에서는 각 기능별로 **입력(Input), 처리(Processing), 출력(Output)**을 명시할 것을 권장합니다.

#### [Template] Functional Requirement Item
> * **ID**: FR-[Category]-[Number]
> * **Description**: 기능에 대한 간략한 설명
> * **Inputs**: 시스템에 입력되는 데이터 (예: 사용자의 메시지, 센서 데이터)
> * **Processing**: 입력 데이터를 출력으로 변환하는 로직, 알고리즘, 유효성 검사
> * **Outputs**: 처리 결과 (예: DB 업데이트, 응답 메시지, 에러 로그)
> * **Error Handling**: 발생 가능한 오류 및 처리 방법

#### 3.2.1 Authentication (인증)
> * **FR-Auth-01**: 시스템은 사용자가 '로그인' 명령 입력 시 Google OAuth 2.0 인증 링크를 생성해야 한다.
>   * **Input**: 사용자 명령어 "/login"
>   * **Output**: OAuth 인증 URL
> * **FR-Auth-02**: 인증 완료 시 발급된 Access/Refresh Token을 암호화하여 DB에 저장해야 한다.
>   * **Exception**: 유효하지 않은 토큰일 경우 재인증 요청 메시지 발송

#### 3.2.2 Proactive Behavior (능동적 행동)
> * **FR-Proactive-01**: 시스템은 매일 오전 8시에 사용자의 당일 일정을 분석하여 브리핑 메시지를 전송해야 한다.
> * **FR-Proactive-02**: 사용자의 다음 일정이 강우 예보 시간과 겹칠 경우, 외출 30분 전 우산 알림을 보내야 한다.

#### 3.2.3 Conversation & Execution (대화 및 실행)
> * **FR-Conv-01**: 사용자의 모호한 요청("다음 주 일정 어때?")에 대해 현재 날짜 기준으로 정확한 날짜 범위를 계산해야 한다.
> * **FR-Exec-01**: LLM이 결정한 도구(Tool) 호출을 안전하게 실행하고, 그 결과를 사용자에게 자연어로 요약하여(Summarization) 전달해야 한다.

### 3.3 Performance Requirements (성능 요구사항)
> * **PR-01 (Latency)**: 사용자의 메시지에 대한 1차 응답(ACK or Typing)은 3초 이내에 이루어져야 한다.
> * **PR-02 (Throughput)**: 단일 인스턴스에서 동시 대화 세션 10개를 지연 없이 처리할 수 있어야 한다.

### 3.4 Design Constraints (설계 제약사항)
> * **DC-01**: 민감 정보(API Key, DB Password)는 반드시 환경 변수(.env)로 관리해야 한다.
> * **DC-02**: Hexagonal(Clean) Architecture 패턴을 준수하여 도메인 로직과 인프라를 분리해야 한다.

### 3.5 Software System Attributes (소프트웨어 속성)
> * **Reliability**: Worker 프로세스 종료 시 자동 재시작(Restart Policy)되어야 한다.
> * **Availability**: 무중단 배포를 지향하되, 초기 버전에서는 1분 미만의 다운타임을 허용한다.
> * **Security**: 사용자의 대화 로그는 개인정보보호법에 의거하여 30일 후 자동 파기되거나 익명화되어야 한다.
> * **Maintainability**: 코드는 모듈화되어야 하며, 주요 로직에는 주석(Docstring)이 100% 작성되어야 한다.
> * **Portability**: 컨테이너 기반으로 작성되어, 특정 OS(host)에 종속되지 않아야 한다.

### 3.6 Logical Database Requirements (논리적 데이터베이스 요구사항)
> 시스템에서 사용하는 정보의 논리적 구조와 제약 조건을 정의합니다.
> * **Types of Information**: 사용자 프로필, 대화 세션 로그, 스케줄 캐시 데이터
> * **Frequency of Use**: 대화 로그는 실시간 쓰기/읽기가 빈번함 (High throughput)
> * **Integrity Constraints**: 삭제된 사용자의 데이터는 즉시 물리적으로 삭제되어야 함(Hard Delete)

### 3.7 Other Requirements (기타 요구사항)
> * **Legal & Compliance**: 데이터 저장 서버의 물리적 위치(Data Residency) 요구사항 등
> * **Internationalization (i18n)**: 모든 시스템 메시지는 리소스 파일로 분리하여 다국어 확장에 대비해야 한다.

---

## 4. Appendices (부록)
> 추가 정보, 참고 도표, 데이터 모델 등을 첨부합니다.
> * ER Diagram (Entity Relationship)
> * API Spec Sheet

# Design Options: 외부 서비스 연동 전략 (Google Calendar & Slack)

## 📋 개요
**기능**: Google Calendar 이벤트 감지 및 Slack 메시지 전송을 위한 외부 API 연동 어댑터 구현
**작성일**: 2026-01-07
**상태**: ✅ 결정 완료

---

## 🎯 요구사항

### 필수 요구사항
- [x] Google Calendar 이벤트 조회 및 변경 감지 (FR-001)
- [x] Slack을 통한 메시지 전송 (FR-002, FR-003)
- [x] OAuth 2.0 기반 사용자 인증 및 토큰 관리 (FR-005)
- [x] 비동기(Async) 처리 지원 (NFR-002: 30초 이내 응답)

### 선택 요구사항
- [ ] Google Calendar Webhook(Push Notification) 실시간 감지
- [ ] Slack Socket Mode (WebSocket 기반 실시간 이벤트)

---

## 🔀 구현 방안 비교

### 🗓️ Google Calendar 연동

#### 방안 A: 공식 SDK (`google-api-python-client`)

**설명**: Google 공식 Python 클라이언트 라이브러리 사용

| 항목 | 내용 |
|------|------|
| **구현 난이도** | 낮음 |
| **예상 시간** | 3시간 |
| **유지보수** | 쉬움 (공식 지원) |
| **확장성** | 좋음 (전체 API 지원) |

**장점**:
- Google 공식 라이브러리로 안정성 및 문서화 우수
- OAuth 흐름 및 토큰 갱신 로직 내장
- 전체 Calendar API 기능 지원 (CRUD, Watch 등)

**단점**:
- 동기(Sync) 방식이 기본 → `run_in_executor` 또는 스레드풀 필요
- 라이브러리 의존성이 다소 무거움

**필요한 것**:
- `google-api-python-client`, `google-auth-oauthlib`
- Google Cloud Console에서 OAuth 자격 증명 생성

---

#### 방안 B: 비공식 Async 라이브러리 (`aiogoogle`)

**설명**: 비동기 네이티브 Google API 클라이언트

| 항목 | 내용 |
|------|------|
| **구현 난이도** | 중간 |
| **예상 시간** | 4시간 |
| **유지보수** | 보통 (커뮤니티 유지) |
| **확장성** | 좋음 |

**장점**:
- Native `async/await` 지원으로 이벤트 루프 친화적
- 코드가 더 깔끔해질 수 있음

**단점**:
- 비공식 라이브러리로 업데이트 지연 가능성
- 일부 기능(예: Watch API)에 대한 지원 불확실
- 문서화 및 커뮤니티 지원이 공식 SDK 대비 부족

**필요한 것**:
- `aiogoogle`
- OAuth 자격 증명

---

#### 방안 C: HTTP 직접 호출 (`httpx`)

**설명**: REST API를 직접 호출

| 항목 | 내용 |
|------|------|
| **구현 난이도** | 높음 |
| **예상 시간** | 6시간+ |
| **유지보수** | 어려움 |
| **확장성** | 보통 |

**장점**:
- 완전한 제어권
- 최소 의존성

**단점**:
- OAuth 토큰 갱신, 에러 핸들링 등 모든 로직 직접 구현 필요
- API 변경 시 수동 대응 필요
- 개발 시간 증가

**필요한 것**:
- `httpx`
- OAuth 자격 증명, 수동 토큰 관리 로직

---

### 💬 Slack 연동

#### 방안 A: 공식 SDK (`slack_sdk`)

**설명**: Slack 공식 Python SDK (Async 지원)

| 항목 | 내용 |
|------|------|
| **구현 난이도** | 낮음 |
| **예상 시간** | 2시간 |
| **유지보수** | 쉬움 (공식 지원) |
| **확장성** | 좋음 |

**장점**:
- **`AsyncWebClient` 제공** → 네이티브 비동기 지원
- Bolt Framework로 이벤트/커맨드 핸들링 가능
- OAuth 및 토큰 관리 내장
- 문서화 우수, 커뮤니티 활발

**단점**:
- Slack 앱 설정 필요 (Bot Token, OAuth Scopes 등)

**필요한 것**:
- `slack_sdk`
- Slack App 생성 및 Bot Token (`xoxb-...`)

---

#### 방안 B: HTTP 직접 호출 (`httpx`)

**설명**: Slack Web API 직접 호출

| 항목 | 내용 |
|------|------|
| **구현 난이도** | 중간 |
| **예상 시간** | 3시간 |
| **유지보수** | 보통 |
| **확장성** | 보통 |

**장점**:
- 최소 의존성
- 필요한 API만 호출

**단점**:
- Rate Limiting, Retry 로직 직접 구현 필요
- 리치 메시지(Block Kit) 구성이 복잡해질 수 있음

**필요한 것**:
- `httpx`
- Slack Bot Token

---

## 📊 비교 요약

### Google Calendar

| 기준 | 방안 A (공식 SDK) | 방안 B (aiogoogle) | 방안 C (httpx) |
|------|------------------|-------------------|----------------|
| 구현 난이도 | 🟢 낮음 | 🟡 중간 | 🔴 높음 |
| 예상 시간 | 3시간 | 4시간 | 6시간+ |
| Async 지원 | 🟡 (Executor) | 🟢 Native | 🟢 Native |
| 유지보수 | 🟢 공식 | 🟡 커뮤니티 | 🔴 수동 |
| 안정성 | 🟢 | 🟡 | 🟡 |

### Slack

| 기준 | 방안 A (공식 SDK) | 방안 B (httpx) |
|------|------------------|----------------|
| 구현 난이도 | 🟢 낮음 | 🟡 중간 |
| 예상 시간 | 2시간 | 3시간 |
| Async 지원 | 🟢 Native | 🟢 Native |
| 유지보수 | 🟢 공식 | 🟡 수동 |
| 기능 완전성 | 🟢 | 🟡 |

---

## 🎯 AI 추천

### Google Calendar: **방안 A (공식 SDK)**

**이유**:
1. **안정성**: 공식 라이브러리는 API 변경 시 빠르게 업데이트됨
2. **기능 완전성**: Watch API (Webhook), Batch 요청 등 고급 기능 지원
3. **동기 문제 해결 가능**: `asyncio.to_thread()` 또는 `run_in_executor`로 비동기화 쉬움
4. **OAuth 지원**: 토큰 갱신 로직이 내장되어 있어 개발 부담 감소

**주의사항**:
- 동기 함수를 비동기 컨텍스트에서 호출 시 `to_thread` 사용 권장
- OAuth 자격 증명(Client ID/Secret)은 `.env`로 관리

---

### Slack: **방안 A (공식 SDK)**

**이유**:
1. **Native Async**: `AsyncWebClient`가 `async/await` 완벽 지원
2. **유지보수 용이**: Slack 정책 변경 시 SDK가 먼저 업데이트됨
3. **Bolt Framework**: 향후 슬래시 커맨드, 이벤트 구독 확장에 유리

**주의사항**:
- Slack App 설정 시 필요한 OAuth Scopes 사전 정의 필요
  - `chat:write`, `users:read`, `im:write` 등

---

## ✅ 결정

> **Google Calendar**: [ ] 방안 A (공식 SDK) / [x] 방안 B (aiogoogle) / [ ] 방안 C (httpx)
> 
> **Slack**: [x] 방안 A (공식 SDK) / [ ] 방안 B (httpx)
> 
> **결정 이유**: 다중 사용자 환경에서 효율적인 동시성 처리를 위해 완전한 비동기 아키텍처 채택. Google은 네이티브 비동기 지원하는 aiogoogle, Slack은 공식 SDK의 AsyncWebClient 사용.
> 
> **결정일**: 2026-01-07

---

## 🔜 다음 단계

결정 후:
1. PLAN_004 문서 작성 (구현 계획) - 위 결정 내용을 Architecture Decisions 섹션에 반영
2. Feature Branch 생성 및 구현 시작

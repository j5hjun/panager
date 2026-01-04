# Implementation Plan: 다중 사용자 시스템

**Status**: ⏳ Planned
**Plan ID**: P-014
**Started**: -
**Last Updated**: 2026-01-05
**Estimated Completion**: 2026-01-08
**Dependencies**: P-011 (메모리 시스템)

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

**다중 사용자 환경**에서 각 사용자별 외부 서비스 인증 정보(OAuth 토큰)를 안전하게 저장하고 관리합니다.

이 시스템은 다음 기능을 위한 **기반 인프라**입니다:
- P-013: 외부 캘린더 연동 (Google Calendar, iCloud)
- 향후: 다른 OAuth 기반 서비스 연동

### Success Criteria

- [ ] TokenRepository 구현 (암호화 저장)
- [ ] OAuth 연결 서비스 구현
- [ ] Slack 명령어로 계정 연결 (`/connect google`, `/connect icloud`)
- [ ] 토큰 자동 갱신 스케줄러
- [ ] 사용자별 설정 관리
- [ ] 모든 테스트 통과 (커버리지 ≥80%)

### User Impact

- **보안**: OAuth 토큰 암호화 저장
- **편의성**: Slack에서 바로 계정 연결
- **자동화**: 토큰 만료 전 자동 갱신

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| SQLite + 암호화 | 단순, 기존 인프라 활용 | 대규모 확장 시 DB 교체 필요 |
| Fernet 대칭키 암호화 | 표준적, cryptography 라이브러리 | 키 관리 필요 |
| 슬래시 명령어 + OAuth URL | UX 간편, 별도 웹서버 불필요 | OAuth 콜백 처리 복잡 |
| APScheduler 토큰 갱신 | 기존 스케줄러 활용 | 실시간성은 부족 |

---

## 📦 Dependencies

### Required Before Starting
- [x] P-011 메모리 시스템 완료

### External Dependencies
```bash
poetry add cryptography
```

---

## 🧪 Test Strategy

### Testing Approach
**TDD Principle**: Write tests FIRST, then implement to make them pass

### Test Pyramid for This Feature
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Unit Tests** | ≥80% | TokenRepository, 암호화 |
| **Integration Tests** | Critical paths | OAuth 흐름 |
| **E2E Tests** | Key flows | Slack → 연결 |

### Test File Organization
```
tests/unit/core/auth/
├── test_token_repository.py
├── test_token_encryption.py
└── test_oauth_service.py

tests/integration/
└── test_oauth_flow.py
```

---

## 🚀 Implementation Phases

### Phase 1: 토큰 저장소 (TokenRepository)
**Goal**: 사용자별 OAuth 토큰 암호화 저장
**Estimated Time**: 3시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 1.1**: TokenRepository 테스트
  - `test_save_token`: 토큰 저장
  - `test_get_token`: 토큰 조회
  - `test_delete_token`: 토큰 삭제
  - `test_token_encryption`: 저장 시 암호화 확인
  - `test_list_user_tokens`: 사용자별 토큰 목록

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 1.2**: 암호화 유틸리티 구현
  - File: `src/core/auth/encryption.py`
  - Fernet 대칭키 암호화
  - 환경변수에서 키 로드

- [ ] **Task 1.3**: TokenRepository 구현
  - File: `src/core/auth/token_repository.py`
  - 테이블: `oauth_tokens`
  - 컬럼: user_id, provider, access_token, refresh_token, expires_at, created_at

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 1.4**: 코드 정리 및 문서화

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] 토큰 암호화 확인 (평문 저장 안 됨)
- [ ] 린트/포매팅 통과

---

### Phase 2: OAuth 연결 서비스
**Goal**: Google/iCloud OAuth 인증 흐름 구현
**Estimated Time**: 4시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: OAuthService 테스트
  - `test_generate_auth_url`: 인증 URL 생성
  - `test_exchange_code`: 인증 코드 → 토큰 교환
  - `test_refresh_token`: 토큰 갱신
  - `test_revoke_token`: 토큰 해지

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.2**: OAuthService 구현
  - File: `src/core/auth/oauth_service.py`
  - Google OAuth 2.0 클라이언트
  - iCloud 앱 비밀번호 인증

- [ ] **Task 2.3**: OAuth 콜백 핸들러
  - Slack 메시지로 인증 코드 수신
  - 또는 별도 경량 웹서버 (선택)

#### Quality Gate ✋
- [ ] Mock OAuth로 테스트 통과
- [ ] 린트/포매팅 통과

---

### Phase 3: Slack 연결 명령어
**Goal**: Slack에서 계정 연결/해제
**Estimated Time**: 3시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 3.1**: Slack 명령어 테스트
  - `test_connect_command`: /connect google 처리
  - `test_disconnect_command`: /disconnect google 처리
  - `test_status_command`: 연결 상태 확인

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 3.2**: Slack 슬래시 명령어 등록
  - `/connect google` - Google 계정 연결
  - `/connect icloud` - iCloud 계정 연결
  - `/disconnect [provider]` - 연결 해제
  - `/accounts` - 연결된 계정 목록

- [ ] **Task 3.3**: 연결 흐름 구현
  - 명령어 → OAuth URL 전송
  - 사용자 OAuth 완료 → 토큰 저장

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] 실제 Slack 테스트 (수동)

---

### Phase 4: 토큰 갱신 스케줄러
**Goal**: 만료 전 토큰 자동 갱신
**Estimated Time**: 2시간
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 4.1**: TokenRefreshScheduler 테스트
  - `test_schedule_refresh`: 갱신 스케줄 등록
  - `test_refresh_before_expiry`: 만료 전 갱신
  - `test_handle_refresh_failure`: 갱신 실패 처리

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 4.2**: TokenRefreshScheduler 구현
  - File: `src/core/auth/token_scheduler.py`
  - APScheduler 활용
  - 만료 10분 전 갱신

- [ ] **Task 4.3**: main.py 통합
  - 스케줄러 초기화
  - 기존 토큰 갱신 스케줄 등록

#### Quality Gate ✋
- [ ] 모든 테스트 통과
- [ ] Docker 테스트 통과

---

### Phase 5: 통합 테스트 및 문서화
**Goal**: E2E 테스트 및 문서 정리
**Estimated Time**: 2시간
**Status**: ⏳ Pending

#### Tasks

- [ ] **Task 5.1**: E2E 테스트 작성
  - 시나리오: Slack 명령어 → OAuth → 토큰 저장 → 갱신

- [ ] **Task 5.2**: README 업데이트
  - 환경변수 설정 (ENCRYPTION_KEY)
  - Slack 앱 설정 (슬래시 명령어)
  - Google Cloud 설정

- [ ] **Task 5.3**: 계획서 완료 처리
  - PLAN_master.md 업데이트
  - P-013 Blocked 해제

#### Quality Gate ✋
- [ ] 전체 테스트 통과
- [ ] Docker 테스트 통과
- [ ] 문서 완료

---

## 📊 Progress Tracking

### Completion Status
```
Phase 1: 토큰 저장소      ░░░░░░░░░░░░   0%
Phase 2: OAuth 서비스     ░░░░░░░░░░░░   0%
Phase 3: Slack 명령어     ░░░░░░░░░░░░   0%
Phase 4: 토큰 갱신        ░░░░░░░░░░░░   0%
Phase 5: 통합 테스트      ░░░░░░░░░░░░   0%
─────────────────────────────────────────
Total:                    ░░░░░░░░░░░░   0%
```

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 3시간 | - | - |
| Phase 2 | 4시간 | - | - |
| Phase 3 | 3시간 | - | - |
| Phase 4 | 2시간 | - | - |
| Phase 5 | 2시간 | - | - |
| **Total** | 14시간 | - | - |

---

## ⚠️ Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| 암호화 키 유출 | 높음 | 낮음 | 환경변수, secrets 관리 |
| OAuth 인증 실패 | 중간 | 중간 | 상세 에러 로깅, 재시도 |
| 토큰 갱신 실패 | 중간 | 낮음 | 재시도 로직, 사용자 알림 |

---

## 🔙 Rollback Strategy

- **Phase 1**: TokenRepository만 추가, 기존 코드 영향 없음
- **Phase 2-3**: Slack 명령어 비활성화로 롤백
- **Phase 4**: 스케줄러 비활성화

---

## 📁 File Changes Summary

### 새로 생성되는 파일
```
src/core/auth/
├── __init__.py
├── encryption.py          # Fernet 암호화
├── token_repository.py    # OAuth 토큰 저장소
├── oauth_service.py       # OAuth 인증 서비스
└── token_scheduler.py     # 토큰 갱신 스케줄러

tests/unit/core/auth/
├── test_encryption.py
├── test_token_repository.py
├── test_oauth_service.py
└── test_token_scheduler.py
```

### 수정되는 파일
```
src/adapters/slack/handler.py  # 슬래시 명령어 추가
src/main.py                    # 스케줄러 초기화
pyproject.toml                 # cryptography 추가
.env.example                   # ENCRYPTION_KEY 추가
```

---

## 🔗 Related Documents

- [PLAN_master.md](./PLAN_master.md) - 통합 계획서
- [PLAN_memory_system.md](./PLAN_memory_system.md) - 메모리 시스템 (P-011)
- [PLAN_calendar_integration.md](./PLAN_calendar_integration.md) - 캘린더 연동 (P-013, 이 계획 완료 후)

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [ ] 모든 Phase 완료 및 Quality Gate 통과
- [ ] 토큰 암호화 저장 확인
- [ ] Slack 명령어 테스트
- [ ] 토큰 갱신 테스트
- [ ] 문서 업데이트
- [ ] PLAN_master.md 업데이트
- [ ] P-013 Blocked 해제

---

**Plan Status**: ⏳ Planned
**Next Action**: Phase 1 시작 - 테스트 먼저 작성

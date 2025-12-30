# Implementation Plan: 배포 및 운영

**Status**: ✅ Complete
**Started**: 2025-12-29
**Last Updated**: 2025-12-30
**Completed**: 2025-12-30

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
패니저를 실제 운영 환경에 배포하고 안정적으로 운영하기 위한 **배포 및 운영 계획**입니다.
개발 환경에서 벗어나 실제 사용자가 24/7 사용할 수 있는 프로덕션 환경을 구축합니다.

#### 배포 목표
- 🐳 **컨테이너화**: Docker를 통한 일관된 배포 환경
- 🏠 **온프레미스 배포**: HP T620 Ubuntu 서버에 안정적 배포
- 🔄 **자동화**: docker-compose로 간편한 배포 및 재시작
- 📊 **모니터링**: 로그 수집, 에러 추적, 리소스 모니터링
- 🔒 **보안**: 환경 변수 관리, 파일 권한 설정

### Success Criteria
- [x] Docker 이미지 빌드 및 실행 성공
- [x] HP T620 서버에 배포 완료
- [x] 24시간 이상 안정적 운영 확인
- [x] 서버 재부팅 후 자동 시작 확인 (systemd)
- [x] 모니터링 설정 완료 (Uptime Kuma, Beszel, Dozzle, LoggiFly)
- [x] 에러 발생 시 로그 확인 가능 (Dozzle + LoggiFly Slack 알림)
- [x] 배포 문서 작성 완료 (DEPLOYMENT.md, OPERATIONS.md)

### User Impact
- **안정성**: 24/7 중단 없는 서비스 제공
- **확장성**: 사용자 증가에 대응 가능
- **유지보수**: 쉬운 업데이트 및 롤백

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Docker 컨테이너화** | 환경 일관성, 이식성, 배포 용이 | 이미지 크기, 학습 곡선 |
| **docker-compose 배포** | 간단한 설정, 로컬 제어, 무료 | 서버 직접 관리 필요 |
| **HP T620 온프레미스** | 완전한 제어, 무료 운영, 충분한 스펙 | 전원/네트워크 관리 필요 |
| **systemd 자동 시작** | 재부팅 시 자동 실행 | 초기 설정 필요 |
| **SQLite 로컬 DB** | 간단한 구조, 백업 용이 | 분산 환경 제한 |

### 배포 아키텍처
```
┌─────────────────────────────────────────────────────┐
│                   GitHub Repository                  │
│                                                       │
│  ┌──────────────┐         ┌──────────────┐          │
│  │  Source Code │────────▶│ GitHub Actions│          │
│  └──────────────┘         └──────┬───────┘          │
│                                   │                   │
└───────────────────────────────────┼───────────────────┘
                                    │ (CI - Optional)
                                    ▼
                        ┌───────────────────────┐
                        │  HP T620 Server       │
                        │  Ubuntu 24.04         │
                        │                       │
                        │  ┌─────────────────┐  │
                        │  │ Docker Compose  │  │
                        │  │                 │  │
                        │  │  ┌───────────┐  │  │
                        │  │  │  패니저   │  │  │
                        │  │  │  Container│  │  │
                        │  │  │           │  │  │
                        │  │  │ - Slack   │  │  │
                        │  │  │ - LLM     │  │  │
                        │  │  │ - Schedule│  │  │
                        │  │  │ - SQLite  │  │  │
                        │  │  └───────────┘  │  │
                        │  └─────────────────┘  │
                        │                       │
                        │  /data (Volume)       │
                        │  └─ calendar.db       │
                        │                       │
                        └───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   Slack WebSocket     │
                        │   (Outbound Only)     │
                        └───────────────────────┘
```

---

## 📦 Dependencies

### Required Before Starting
- [x] 패니저 핵심 기능 완료 (Phase 1-7)
- [ ] HP T620 서버 준비 (Ubuntu 24.04 설치)
- [ ] Docker & Docker Compose 설치
- [ ] 인터넷 연결 (Slack WebSocket용)
- [ ] GitHub 계정 (선택 - CI/CD 시)

### External Dependencies
- Docker Engine (20.10+)
- Docker Compose (v2.0+)
- (Optional) Sentry Account (에러 추적)

---

## 🧪 Test Strategy

### Testing Approach
**배포 전 검증**: 각 단계마다 로컬/스테이징 환경에서 테스트 후 프로덕션 배포

### Deployment Testing
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **로컬 Docker 테스트** | 100% | 컨테이너 빌드 및 실행 검증 |
| **스테이징 배포 테스트** | Critical paths | 실제 배포 환경 검증 |
| **프로덕션 스모크 테스트** | Key features | 배포 후 주요 기능 동작 확인 |
| **부하 테스트** | 성능 | 동시 사용자 처리 능력 |

---

## 🚀 Implementation Phases

---

### Phase 1: Docker 컨테이너화
**Goal**: Docker 이미지 빌드 및 로컬 실행 성공
**Estimated Time**: 2-3 hours
**Status**: ✅ Complete

#### Tasks

**🔴 RED: Write Failing Tests First**
- [x] **Test 1.1**: Docker 빌드 테스트
  - 로컬에서 Docker 이미지 빌드 성공
  - 컨테이너 실행 시 애플리케이션 정상 작동

**🟢 GREEN: Implement to Make Tests Pass**
- [x] **Task 1.2**: Dockerfile 작성
  - File: `Dockerfile`
  - Details:
    - Python 3.11-slim 베이스 이미지
    - 멀티 스테이지 빌드 (builder + runtime)
    - Poetry 설치 및 의존성 설치
    - 비root 사용자로 실행

- [x] **Task 1.3**: .dockerignore 작성
  - File: `.dockerignore`
  - Details:
    - 불필요한 파일 제외 (캐시, 테스트, 로그 등)
    - 빌드 최적화

- [x] **Task 1.4**: docker-compose.yml 작성
  - File: `docker-compose.yml`
  - Details:
    - 환경 변수 매핑 (.env 파일)
    - 볼륨 마운트 (./data:/app/data)
    - 로그 로테이션 설정
    - 리소스 제한 (1GB RAM)

**🔵 REFACTOR: Clean Up Code**
- [x] **Task 1.5**: 멀티 스테이지 빌드 적용
  - 이미지 크기 최적화: 243MB
  - Builder와 Runtime 분리

#### Quality Gate ✋

**Build & Tests**:
- [x] `docker build -t panager:test .` 성공
- [x] Docker 이미지 생성 확인 (243MB)
- [x] docker-compose.yml 유효성 검증
- [x] 전체 테스트 통과 (68/68)

**Manual Test Checklist**:
- [ ] Docker 컨테이너에서 실제 실행 테스트 (HP T620에서)
- [ ] 환경 변수 정상 로드 확인
- [ ] Slack Bot 연결 확인
- [ ] 컨테이너 재시작 시 DB 데이터 유지

---

### Phase 2: CI/CD 파이프라인 구축 (선택사항)
**Goal**: GitHub Actions로 자동 빌드 및 테스트 (온프레미스 배포 시 선택)
**Estimated Time**: 2-3 hours
**Status**: ✅ Complete

> **💡 Note**: HP T620 직접 배포 시 이 Phase는 선택사항입니다. 수동 배포로도 충분합니다.

#### Tasks

**🔴 RED: Write Failing Tests First**
- [x] **Test 2.1**: CI 파이프라인 테스트
  - Push 시 자동 테스트 실행
  - 테스트 실패 시 빌드 실패

**🟢 GREEN: Implement to Make Tests Pass**
- [x] **Task 2.2**: GitHub Actions Workflow 작성
  - File: `.github/workflows/ci.yml`
  - Details:
    - 코드 체크아웃
    - Python 환경 설정
    - 의존성 설치
    - 린트 (ruff, black)
    - 테스트 실행 (pytest)
    - 커버리지 확인 (Codecov)

- [x] **Task 2.3**: Docker 이미지 빌드 자동화
  - File: `.github/workflows/docker-build.yml`
  - Details:
    - Docker 이미지 빌드
    - GitHub Container Registry에 푸시
    - 태그 관리 (latest, sha)

**🔵 REFACTOR: Clean Up Code**
- [x] **Task 2.4**: 빌드 캐싱 최적화
  - Docker layer 캐싱 (type=gha)
  - Poetry 캐싱

#### Quality Gate ✋

**CI/CD Validation**:
- [x] PR 생성 시 자동 테스트 실행
- [x] main 브랜치 푸시 시 Docker 이미지 자동 빌드
- [x] 테스트 실패 시 빌드 중단 확인
- [x] GitHub Container Registry에 이미지 업로드 확인

**Manual Test Checklist**:
- [x] PR에서 테스트 결과 확인
- [x] 빌드된 Docker 이미지 확인 (ghcr.io/j5hjun/panager)

---

### Phase 3: HP T620 서버 배포 (Self-hosted Runner)
**Goal**: GitHub Actions 셀프호스팅 러너를 통한 자동 배포
**Estimated Time**: 2-3 hours
**Status**: ✅ Complete

#### Tasks

**🔴 RED: Write Failing Tests First**
- [x] **Test 3.1**: 서버 환경 테스트
  - 셀프호스팅 러너가 온라인 상태
  - Docker 명령어 실행 가능

**🟢 GREEN: Implement to Make Tests Pass**
- [x] **Task 3.2**: 셀프호스팅 러너 확인
  - GitHub repo → Settings → Actions → Runners
  - HP T620 러너가 Online 상태인지 확인
  - 러너가 없으면 새로 등록

- [x] **Task 3.3**: 배포 워크플로우 작성
  - File: `.github/workflows/deploy.yml`
  - Details:
    - self-hosted 러너에서 실행
    - docker compose down → build → up -d --wait
    - Health check

- [x] **Task 3.4**: 서버에 .env 파일 설정
  - GitHub Secrets `ENV_FILE`로 자동 생성
  - 환경 변수 설정 완료

- [x] **Task 3.5**: 배포 테스트
  - main 브랜치에 푸시
  - GitHub Actions에서 배포 성공 확인
  - Slack Bot 온라인 확인

#### Quality Gate ✋

**Deployment Validation**:
- [x] GitHub Actions에서 배포 성공
- [x] HP T620에서 애플리케이션 정상 실행
- [x] Slack Bot이 온라인 상태
- [x] 모든 환경 변수 정상 로드
- [x] 볼륨 마운트로 DB 데이터 영속성 확인

**Manual Test Checklist**:
- [x] Slack에서 "안녕" → 응답 확인
- [x] 날씨 조회 기능 동작
- [x] 일정 관리 기능 동작
- [x] 코드 푸시 → 자동 배포 → 적용 확인

---

### Phase 4: 모니터링 및 로깅
**Goal**: 통합 모니터링, 로그 관리 및 Slack 알림 설정
**Estimated Time**: 2-3 hours
**Status**: ✅ Complete

#### 도구 스택
- **Uptime Kuma**: 서비스 상태 모니터링 + Slack 알림 (다운타임)
- **Beszel**: 시스템 리소스 모니터링 (CPU, 메모리, 디스크)
- **Dozzle**: 통합 로그 뷰어
- **LoggiFly**: 에러 로그 감지 + Slack 알림

#### Tasks

**🔴 RED: Write Failing Tests First**
- [x] **Test 4.1**: 모니터링 도구 접근 테스트
  - Uptime Kuma 웹 UI 접근 가능
  - Beszel 대시보드 접근 가능
  - Dozzle 로그 뷰어 접근 가능

**🟢 GREEN: Implement to Make Tests Pass**
- [x] **Task 4.2**: Uptime Kuma 설치
  - Docker Compose로 설치
  - panager 서비스 헬스체크 등록
  - Slack Webhook 알림 설정 (다운타임)

- [x] **Task 4.3**: Beszel 설치
  - Docker Compose로 설치
  - Beszel Agent 연결
  - panager 컨테이너 리소스 모니터링

- [x] **Task 4.4**: Dozzle 설치
  - Docker Compose로 설치
  - 모든 컨테이너 로그 통합 뷰어

- [x] **Task 4.5**: LoggiFly 설치
  - Docker Compose로 설치
  - config.yaml로 설정 (containers, keywords, apprise)
  - Slack 알림 테스트 완료

- [x] **Task 4.6**: 로그 영구 저장 설정
  - Docker 로깅 드라이버 설정 (json-file)
  - 로그 로테이션 (max-size: 10m, max-file: 3)

**🔵 REFACTOR: Clean Up Code**
- [x] **Task 4.7**: 알림 최적화
  - Uptime Kuma 체크 간격 설정
  - LoggiFly 키워드 최적화

#### Quality Gate ✋

**Monitoring Validation**:
- [x] Uptime Kuma에서 panager 상태 확인 가능
- [x] Beszel에서 CPU/메모리 사용량 확인 가능
- [x] Dozzle에서 모든 컨테이너 로그 확인 가능
- [x] 서비스 다운 시 Slack 알림 수신
- [x] 에러 로그 발생 시 Slack 알림 수신

**Manual Test Checklist**:
- [x] panager 중지 → Slack 다운타임 알림 확인
- [x] panager 재시작 → Slack 복구 알림 확인
- [x] 에러 발생 → Slack 에러 알림 확인 (LoggiFly)
- [x] Dozzle에서 실시간 로그 스트리밍 확인
- [x] 로그 로테이션 설정 확인 (docker-compose.yml)

---

### Phase 5: 문서화 및 운영 가이드
**Goal**: 배포 및 운영 문서 작성
**Estimated Time**: 2-3 hours
**Status**: ✅ Complete

#### Tasks

**🟢 GREEN: Documentation**
- [x] **Task 5.1**: 배포 가이드 작성
  - File: `docs/DEPLOYMENT.md`
  - Details:
    - Docker 빌드 및 실행 방법
    - CI/CD 자동 배포 가이드
    - 환경 변수 설정 방법
    - 트러블슈팅

- [x] **Task 5.2**: 운영 가이드 작성
  - File: `docs/OPERATIONS.md`
  - Details:
    - 모니터링 방법 (Uptime Kuma, Beszel, Dozzle)
    - 로그 확인 방법
    - 배포 롤백 방법
    - 백업 및 복구
    - 긴급 대응 절차

- [x] **Task 5.3**: README 업데이트
  - Docker 배포 섹션 추가
  - 문서 링크 섹션 추가

**🔵 REFACTOR: Clean Up Code**
- [x] **Task 5.4**: 코드 주석 정리
  - 환경 변수 문서화 (.env.example)

#### Quality Gate ✋

**Documentation Validation**:
- [x] 문서만 보고 새로운 팀원이 배포 가능
- [x] 모든 환경 변수 문서화됨
- [x] 트러블슈팅 가이드 포함
- [x] 운영 절차 명확히 기술됨

**Manual Test Checklist**:
- [x] 문서 따라 배포 시뮬레이션 가능
- [x] 링크 및 명령어 동작 확인
- [x] 섹션별 명확한 구조

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| 서버 전원 차단 | Medium | High | UPS 사용, 자동 재시작 (systemd) |
| 네트워크 장애 | Low | High | 안정적인 인터넷 연결, 재연결 로직 |
| 디스크 공간 부족 | Low | Medium | 로그 로테이션, 정기 정리 스크립트 |
| API 키 노출 | Low | High | .env 파일 권한 설정 (600), .gitignore |
| DB 데이터 손실 | Low | High | 정기 백업 스크립트, 볼륨 마운트 |

---

## 🔄 Rollback Strategy

### If Phase 1 Fails (Docker)
- Docker 파일 제거
- 로컬 실행으로 복귀 (`poetry run python -m src.main`)

### If Phase 2 Fails (CI/CD)
- GitHub Actions 파일 제거
- 수동 빌드/배포로 진행

### If Phase 3 Fails (서버 배포)
- 서버에서 `docker-compose down`
- 로컬 Docker로 복귀

### 전체 롤백
- 서버에서 컨테이너 중지 및 삭제
- systemd 서비스 비활성화
- 로컬 개발 환경으로 복귀

---

## 📊 Progress Tracking

### Completion Status
- **Phase 1**: ✅ 100% - Docker 컨테이너화
- **Phase 2**: ✅ 100% - CI/CD 파이프라인
- **Phase 3**: ✅ 100% - HP T620 서버 배포
- **Phase 4**: ✅ 100% - 모니터링 및 로깅
- **Phase 5**: ✅ 100% - 문서화 및 운영 가이드

**Overall Progress**: 100% complete (5/5 phases)

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 2-3 hours | 완료 | - |
| Phase 2 | 2-3 hours | 완료 | - |
| Phase 3 | 2-3 hours | 완료 | - |
| Phase 4 | 2-3 hours | 완료 | - |
| Phase 5 | 2-3 hours | 완료 | - |
| **Total** | 10-15 hours | 2일 | - |

---

## 📝 Notes & Learnings

### Implementation Notes
- **셀프호스팅 러너**: GitHub Actions와 연동으로 CI 성공 후 자동 배포 구현
- **모니터링 스택**: Uptime Kuma + Beszel + Dozzle + LoggiFly 조합으로 완벽한 모니터링
- **LoggiFly 설정**: config.yaml 파일로 설정 필요 (환경변수만으로 불가)
- **Beszel**: Hub + Agent 구조, Agent 별도 설치 필요

### Blockers Encountered
- **Tailscale 버전 이슈**: 서버 접속 불가 → 직접 서버에서 업데이트 필요
- **GHCR 권한 문제**: `packages: write` permission 추가로 해결
- **Codecov 토큰 필요**: v4부터 토큰 필수

### Improvements for Future Plans
- Loki + Grafana 도입 시 장기 로그 보관 가능
- 외부 API 모니터링 (Groq, OpenWeatherMap) 추가 가능
- 디스크 용량 알림 Beszel에서 설정 가능

---

## 📚 References

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Beszel](https://github.com/henrygd/beszel)
- [Dozzle](https://github.com/amir20/dozzle)
- [LoggiFly](https://github.com/clemcer/LoggiFly)

### Tools
- Portainer (Docker GUI): https://www.portainer.io/
- Uptime Kuma: https://github.com/louislam/uptime-kuma
- Beszel: https://github.com/henrygd/beszel
- Dozzle: https://github.com/amir20/dozzle
- LoggiFly: https://github.com/clemcer/LoggiFly

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [x] All phases completed with quality gates passed
- [x] HP T620 서버에서 안정 운영 확인
- [x] docker-compose로 정상 실행 확인
- [x] 서버 재부팅 후 자동 시작 확인 (systemd runner)
- [x] 모니터링 설정 완료 (Uptime Kuma, Beszel, Dozzle, LoggiFly)
- [x] 배포 및 운영 문서 작성 완료 (DEPLOYMENT.md, OPERATIONS.md)
- [x] Slack 알림 테스트 완료 (다운타임 + 에러 로그)

---

**Plan Status**: ✅ Complete
**Completed Date**: 2025-12-30
**Total Duration**: 2일 (2025-12-29 ~ 2025-12-30)

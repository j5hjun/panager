# Implementation Plan: 배포 및 운영

**Status**: ⏳ Pending
**Started**: YYYY-MM-DD
**Last Updated**: 2025-12-29
**Estimated Completion**: YYYY-MM-DD (약 1주)

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
- [ ] Docker 이미지 빌드 및 실행 성공
- [ ] HP T620 서버에 배포 완료
- [ ] 24시간 이상 안정적 운영 확인
- [ ] 서버 재부팅 후 자동 시작 확인
- [ ] 모니터링 설정 완료
- [ ] 에러 발생 시 로그 확인 가능
- [ ] 배포 문서 작성 완료

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
**Status**: ⏳ Pending

> **💡 Note**: HP T620 직접 배포 시 이 Phase는 선택사항입니다. 수동 배포로도 충분합니다.

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: CI 파이프라인 테스트
  - Push 시 자동 테스트 실행
  - 테스트 실패 시 빌드 실패

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.2**: GitHub Actions Workflow 작성
  - File: `.github/workflows/ci.yml`
  - Details:
    - 코드 체크아웃
    - Python 환경 설정
    - 의존성 설치
    - 린트 (ruff, black)
    - 테스트 실행 (pytest)
    - 커버리지 확인

- [ ] **Task 2.3**: Docker 이미지 빌드 자동화
  - File: `.github/workflows/docker-build.yml`
  - Details:
    - Docker 이미지 빌드
    - GitHub Container Registry에 푸시
    - 태그 관리 (latest, version)

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 2.4**: 빌드 캐싱 최적화
  - Docker layer 캐싱
  - Poetry 캐싱

#### Quality Gate ✋

**CI/CD Validation**:
- [ ] PR 생성 시 자동 테스트 실행
- [ ] main 브랜치 푸시 시 Docker 이미지 자동 빌드
- [ ] 테스트 실패 시 빌드 중단 확인
- [ ] GitHub Container Registry에 이미지 업로드 확인

**Manual Test Checklist**:
- [ ] PR에서 테스트 결과 확인
- [ ] 빌드된 Docker 이미지 Pull 후 실행 확인

---

### Phase 3: HP T620 서버 배포
**Goal**: HP T620 Ubuntu 서버에 docker-compose로 프로덕션 배포
**Estimated Time**: 2-3 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 3.1**: 서버 환경 테스트
  - 로컬에서 docker-compose로 실행 성공
  - 환경 변수가 정상 로드됨

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 3.2**: docker-compose.yml 작성 (프로덕션용)
  - File: `docker-compose.yml`
  - Details:
    ```yaml
    version: '3.8'
    services:
      panager:
        build: .
        restart: unless-stopped
        volumes:
          - ./data:/app/data
        env_file:
          - .env
    ```

- [ ] **Task 3.3**: HP T620 서버 준비
  - Ubuntu 24.04 설치 확인
  - Docker 설치: `curl -fsSL https://get.docker.com | sh`
  - Docker Compose 설치
  - 사용자를 docker 그룹에 추가

- [ ] **Task 3.4**: 서버에 코드 배포
  - Git clone 또는 rsync로 전송
  - .env 파일 생성 및 환경 변수 설정
  - 디렉토리 구조 확인

- [ ] **Task 3.5**: systemd 서비스 등록 (자동 시작)
  - File: `/etc/systemd/system/panager.service`
  - Details:
    ```ini
    [Unit]
    Description=Panizer AI Assistant
    After=docker.service
    
    [Service]
    Type=oneshot
    RemainAfterExit=yes
    WorkingDirectory=/home/user/panager
    ExecStart=/usr/bin/docker-compose up -d
    ExecStop=/usr/bin/docker-compose down
    
    [Install]
    WantedBy=multi-user.target
    ```

- [ ] **Task 3.6**: 배포 및 실행
  - `docker-compose up -d` 실행
  - `systemctl enable panager` (부팅 시 자동 시작)

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 3.7**: 배포 스크립트 작성
  - File: `scripts/deploy.sh`
  - Git pull → docker-compose build → docker-compose up -d

#### Quality Gate ✋

**Deployment Validation**:
- [ ] HP T620에서 애플리케이션 정상 실행
- [ ] Slack Bot이 온라인 상태
- [ ] 모든 환경 변수 정상 로드
- [ ] 볼륨 마운트로 DB 데이터 영속성 확인
- [ ] 서버 재부팅 후 자동 시작 확인

**Manual Test Checklist**:
- [ ] Slack에서 "안녕" → 응답 확인
- [ ] 날씨 조회 기능 동작
- [ ] 일정 관리 기능 동작
- [ ] 아침 브리핑 스케줄러 동작 (다음날 확인)
- [ ] 24시간 안정성 확인

---

### Phase 4: 모니터링 및 로깅
**Goal**: 애플리케이션 상태 모니터링 및 에러 추적
**Estimated Time**: 2-3 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 4.1**: 로깅 테스트
  - 에러 발생 시 로그 기록됨
  - 로그가 올바른 형식으로 출력됨

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 4.2**: 구조화된 로깅 개선
  - JSON 형식 로그
  - 주요 이벤트 로깅
  - 에러 스택 트레이스

- [ ] **Task 4.3**: Sentry 통합 (선택)
  - File: `src/main.py`
  - Sentry SDK 설치 및 초기화
  - 에러 자동 추적

- [ ] **Task 4.4**: 로컬 모니터링 설정
  - `docker stats` 명령어로 리소스 모니터링
  - `docker logs -f panager` 로그 확인
  - (선택) Portainer 설치 (GUI 관리 도구)

- [ ] **Task 4.5**: 알림 설정 (선택)
  - 애플리케이션 다운 시 Slack 알림
  - 에러 발생 시 Sentry 알림

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 4.6**: 로그 정리
  - 민감 정보 마스킹
  - 로그 레벨 최적화
  - 로그 로테이션 설정

#### Quality Gate ✋

**Monitoring Validation**:
- [ ] `docker stats`로 리소스 사용량 확인 가능
- [ ] `docker logs`에서 주요 이벤트 추적 가능
- [ ] 에러 발생 시 Sentry에 자동 리포트 (설정 시)
- [ ] 알림 설정 동작 확인 (설정 시)

**Manual Test Checklist**:
- [ ] 일부러 에러 발생 → 로그에서 확인
- [ ] `docker stats`에서 CPU/메모리 사용량 확인
- [ ] 로그에서 사용자 요청 추적 가능

---

### Phase 5: 문서화 및 운영 가이드
**Goal**: 배포 및 운영 문서 작성
**Estimated Time**: 2-3 hours
**Status**: ⏳ Pending

#### Tasks

**🟢 GREEN: Documentation**
- [ ] **Task 5.1**: 배포 가이드 작성
  - File: `docs/DEPLOYMENT.md`
  - Details:
    - Docker 빌드 및 실행 방법
    - 클라우드 배포 단계별 가이드
    - 환경 변수 설정 방법
    - 트러블슈팅

- [ ] **Task 5.2**: 운영 가이드 작성
  - File: `docs/OPERATIONS.md`
  - Details:
    - 모니터링 방법
    - 로그 확인 방법
    - 배포 롤백 방법
    - 백업 및 복구
    - 긴급 대응 절차

- [ ] **Task 5.3**: README 업데이트
  - 배포 섹션 추가
  - 배포 문서 링크

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 5.4**: 코드 주석 정리
  - 프로덕션 관련 주석 추가
  - 환경 변수 문서화

#### Quality Gate ✋

**Documentation Validation**:
- [ ] 문서만 보고 새로운 팀원이 배포 가능
- [ ] 모든 환경 변수 문서화됨
- [ ] 트러블슈팅 가이드 포함
- [ ] 운영 절차 명확히 기술됨

**Manual Test Checklist**:
- [ ] 문서 따라 배포 시뮬레이션
- [ ] 링크 및 명령어 동작 확인
- [ ] 스크린샷 및 예시 포함

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
- **Phase 2**: ⏳ 0% - CI/CD 파이프라인 (선택)
- **Phase 3**: ⏳ 0% - HP T620 서버 배포
- **Phase 4**: ⏳ 0% - 모니터링 및 로깅
- **Phase 5**: ⏳ 0% - 문서화 및 운영 가이드

**Overall Progress**: 20% complete (1/5 phases)

### Time Tracking
| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 2-3 hours | - | - |
| Phase 2 | 2-3 hours (선택) | - | - |
| Phase 3 | 2-3 hours | - | - |
| Phase 4 | 2-3 hours | - | - |
| Phase 5 | 2-3 hours | - | - |
| **Total** | 10-15 hours | - | - |

---

## 📝 Notes & Learnings

### Implementation Notes
- [구현 중 발견한 인사이트 기록]

### Blockers Encountered
- [블로커 기록]

### Improvements for Future Plans
- [개선 사항 기록]

---

## 📚 References

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions) (선택)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/) (선택)

### Tools
- Portainer (Docker GUI): https://www.portainer.io/
- Sentry: https://sentry.io/
- Watchtower (자동 업데이트): https://containrrr.dev/watchtower/

---

## ✅ Final Checklist

**Before marking plan as COMPLETE**:
- [ ] All phases completed with quality gates passed
- [ ] HP T620 서버에서 24시간 이상 안정 운영
- [ ] docker-compose로 정상 실행 확인
- [ ] 서버 재부팅 후 자동 시작 확인
- [ ] 모니터링 설정 완료
- [ ] 배포 및 운영 문서 작성 완료
- [ ] 백업 스크립트 작성 및 테스트 완료

---

**Plan Status**: ⏳ Pending
**Next Action**: Phase 1 시작 - Docker 컨테이너화
**Blocked By**: None

# 구현 계획: CI/CD 파이프라인 구축

**상태**: ⏳ 대기 중 (Pending)
**Plan ID**: PLAN-002
**시작일**: 2026-01-10
**예상 완료일**: 2026-01-10

---

## 1. 개요 (Overview)
**목표**: 코드 품질을 자동으로 검증하고, 검증된 코드를 배포 서버에 안정적으로 배포하는 자동화 파이프라인을 구축합니다.

### 주요 포함 사항
1.  **Automated Testing**: PR 및 Push 시 자동으로 테스트 및 린트 검사.
2.  **Coverage Report**: Codecov를 통한 테스트 커버리지 시각화.
3.  **Process Delivery**: Docker 이미지를 빌드하여 GHCR(GitHub Container Registry)에 업로드.
4.  **Automated Deployment**: 실제 운영 서버에 최신 컨테이너 배포.

---

## 2. 단계별 계획 (Phased Approach)

### Phase 1: CI & Coverage (지속적 통합)
**목표**: 코드 변경 시마다 테스트를 수행하고 커버리지를 리포트한다.

- [ ] **Task 1.1**: Poetry 기반 CI 환경 구성 (`.github/workflows/ci.yml`)
    - Python 3.11 셋업
    - 의존성 캐싱 및 설치 (`poetry install`)
- [ ] **Task 1.2**: Lint & Type Check 추가
    - `ruff check .` (Lint)
    - `ruff format --check .` (Format)
- [ ] **Task 1.3**: Test & Coverage 설정
    - `pytest --cov=app --cov-report=xml` 실행
    - Codecov Action 연동 (`secrets.CODECOV_TOKEN`)

### Phase 2: Delivery & Registry (지속적 제공)
**목표**: 검증된 코드를 실행 가능한 Docker 이미지로 패키징한다.

- [ ] **Task 2.1**: Docker Build Workflow 작성 (`.github/workflows/deploy.yml`)
    - `main` 브랜치 Push 시 트리거
    - GHCR 로그인 (`secrets.GITHUB_TOKEN`)
- [ ] **Task 2.2**: Multi-platform Build (Optional)
    - `linux/amd64`, `linux/arm64` 지원 (필요 시)
    - 이미지 태그 관리 (`latest`, `sha`)

### Phase 3: Deployment (지속적 배포)
**목표**: Self-hosted Runner를 활용하여 안전하게 운영 서버에 배포한다. (SSH 접속 방식 대체)

- [ ] **Task 3.1**: Server Runner Setup
    - 배포 서버에 GitHub Actions Runner 설치 및 등록
    - 서비스 데몬 등록 (`svc.sh install`)
- [ ] **Task 3.2**: Deploy Workflow 작성 (`deploy.yml`)
    - `needs: build` 설정 (빌드 성공 후 실행)
    - `runs-on: self-hosted` 태그 사용
    - GHCR 로그인 및 이미지 Pull
    - `docker-compose.yml` 생성 및 `up -d` 실행
    - 사용하지 않는 이미지 정리 (`docker image prune -f`)

---

## 3. 품질 관문 (Quality Gate)
- **CI Pass**: 모든 테스트와 린트가 통과해야 함.
- **Coverage**: 커버리지 리포트가 성공적으로 Codecov에 업로드되어야 함.
- **Registry Update**: 최신 이미지가 GHCR에 정상적으로 업로드되어야 함.
- **Deploy Success**: 배포 후 서버 엔드포인트가 정상 응답(200 OK)해야 함.

## 4. 필요 Secrets 목록
Github Repository Settings > Secrets and variables > Actions에 등록해야 할 값들:
- `CODECOV_TOKEN`: Codecov 인증 토큰
- `ENV_FILE`: 프로덕션용 `.env` 내용 (Deployment 시 생성)
*참고: Self-hosted Runner 사용 시 SSH 관련 Secrets(`HOST`, `KEY` 등)는 필요하지 않음*

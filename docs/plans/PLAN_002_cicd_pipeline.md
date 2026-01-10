# 구현 계획: CI/CD 파이프라인 구축

**상태**: ✅ 완료 (Completed)
**Plan ID**: PLAN-002
**시작일**: 2026-01-10
**완료일**: 2026-01-10

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

- [x] **Task 1.1**: Poetry 기반 CI 환경 구성 (`.github/workflows/ci.yml`)
    - Python 3.11 셋업
    - 의존성 캐싱 및 설치 (`poetry install`)
- [x] **Task 1.2**: Lint & Type Check 추가
    - `ruff check .` (Lint)
    - `ruff format --check .` (Format)
- [x] **Task 1.3**: Test & Coverage 설정
    - `pytest --cov=app --cov-report=xml` 실행
    - Codecov Action 연동 (`secrets.CODECOV_TOKEN`)

### Phase 2: Delivery & Registry (지속적 제공)
**목표**: 검증된 코드를 실행 가능한 Docker 이미지로 패키징한다.

- [x] **Task 2.1**: Docker Build Workflow 작성 (`.github/workflows/deploy.yml`)
    - `main` 브랜치 Push 시 트리거
    - GHCR 로그인 (`secrets.GITHUB_TOKEN`)
- [x] **Task 2.2**: Multi-platform Build (Optional)
    - `linux/amd64`, `linux/arm64` 지원 (필요 시)
    - 이미지 태그 관리 (`latest`, `sha`)

### Phase 3: Deployment (지속적 배포)
**목표**: Self-hosted Runner를 활용하여 안전하게 운영 서버에 배포한다. (SSH 접속 방식 대체)

- [x] **Task 3.1**: Server Runner Setup
    - 배포 서버에 GitHub Actions Runner 설치 및 등록
    - 서비스 데몬 등록 (`svc.sh install`)
- [x] **Task 3.2**: Deploy Workflow 작성 (`deploy.yml`)
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

---

## 5. 베스트 프랙티스 (Best Practices)

### 5.1 이미지 태깅 전략
| 방식 | 설명 | 권장 여부 |
|------|------|----------|
| `latest` 단독 사용 | 롤백 불가, 추적 어려움 | ❌ 비권장 |
| SHA 태그 | 불변, 추적 가능 | ✅ 권장 |
| Semantic Version | 릴리스 관리 용이 | ✅ 권장 (정식 릴리스) |

```yaml
# 권장 예시
tags: |
  myapp:${{ github.sha }}    # 불변 태그
  myapp:latest               # 편의용
```

### 5.2 Health Check 구성
#### Dockerfile
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

#### docker-compose.yml
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

#### FastAPI Endpoint
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 5.3 의존성 순서 (depends_on)
```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy  # DB ready 후 앱 시작
```

### 5.4 무중단 배포 패턴

| 패턴 | 복잡도 | 다운타임 | 적용 대상 |
|------|--------|----------|----------|
| **단순 교체** | 낮음 | 있음 (수초) | MVP, 소규모 |
| **Rolling Update** | 중간 | 없음 | 중규모 |
| **Blue-Green** | 높음 | 없음 | 대규모, 미션 크리티컬 |

### 5.5 롤백 전략
```yaml
# 배포 전 현재 버전 저장
- name: Backup current version
  run: |
    CURRENT=$(docker inspect panager --format='{{.Config.Image}}' | cut -d: -f2)
    echo "current=$CURRENT" >> $GITHUB_OUTPUT

# 실패 시 롤백
- name: Rollback on failure
  if: failure()
  run: |
    IMAGE_TAG=${{ steps.backup.outputs.current }}
    docker compose up -d
```

### 5.6 로깅 관리
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # 로그 파일 최대 크기
    max-file: "3"     # 최대 파일 개수 (디스크 보호)
```

### 5.7 Multi-stage Dockerfile
```dockerfile
# Build stage - 빌드 도구 포함
FROM python:3.11-slim AS builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | pip install -r /dev/stdin

# Production stage - 런타임만 포함
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```
**장점**: 이미지 크기 감소, 보안 향상 (빌드 도구 제외)

### 5.8 배포 동시성 제어
```yaml
deploy:
  concurrency:
    group: production
    cancel-in-progress: false  # 진행 중인 배포 보호
```

---

## 6. 개선 필요 사항 (Improvement Checklist)

### 현재 상태 분석
| 항목 | 현재 상태 | 목표 | 우선순위 |
|------|----------|------|----------|
| Immutable 태그 (SHA) | ✅ 적용됨 | 유지 | - |
| Health Check (Dockerfile) | ✅ 적용됨 | 완료 | - |
| Health Check (docker-compose) | ✅ 적용됨 | 완료 | - |
| `/health` 엔드포인트 | ✅ 적용됨 | 완료 | - |
| depends_on condition | ✅ 적용됨 | 완료 | - |
| 로깅 제한 | ✅ 적용됨 | 완료 | - |
| Multi-stage build | ✅ 적용됨 | 완료 | - |
| 롤백 전략 | ✅ SHA 기반 | 완료 | - |
| non-root 사용자 | ✅ 적용됨 | 완료 | - |
| 배포 동시성 제어 | ✅ 적용됨 | 완료 | - |

### 개선 작업 (Phase 4) - ✅ 완료
- [x] **Task 4.1**: `/health` 엔드포인트 추가 (`app/main.py`)
- [x] **Task 4.2**: Dockerfile에 HEALTHCHECK 추가
- [x] **Task 4.3**: docker-compose.yml에 healthcheck 및 depends_on 조건 추가
- [x] **Task 4.4**: 로깅 제한 설정 추가
- [x] **Task 4.5**: 배포 워크플로에 SHA 기반 롤백 구현
- [x] **Task 4.6**: Multi-stage Dockerfile로 전환
- [x] **Task 4.7**: non-root 사용자로 컨테이너 실행 (보안 강화)
- [x] **Task 4.8**: 배포 동시성 제어 (concurrency group)

# ====================
# 스테이지 1: 빌더
# ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치 (export 플러그인 포함)
RUN pip install poetry poetry-plugin-export

# 의존성 정의 파일 복사
COPY pyproject.toml poetry.lock* ./

# 가상환경 없이 시스템에 직접 설치
# --without dev: dev 의존성 제외
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# ====================
# 스테이지 2: 프로덕션
# ====================
FROM python:3.11-slim

WORKDIR /app

# 런타임 의존성만 설치 (빌드 도구 제외)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌더에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY . .

# 보안을 위한 non-root 사용자 생성
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 컨테이너 오케스트레이션용 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

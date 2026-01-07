# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 의존성 파일 복사
COPY pyproject.toml poetry.lock ./

# 가상환경 생성 방지 및 패키지 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# 빌드 스테이지에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드 복사
COPY src/ ./src/

# 실행
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy dependency definition
COPY pyproject.toml poetry.lock* ./

# Check if poetry.lock exists, trying to generate it if not, then install
# We allow creating lock file if missing to avoid build failure on first run
RUN poetry config virtualenvs.create false \
    && if [ -f poetry.lock ]; then poetry install --no-root; else poetry lock && poetry install --no-root; fi

# Copy application
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

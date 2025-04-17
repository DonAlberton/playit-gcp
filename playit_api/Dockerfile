# =================== Builder stage ===================
FROM python:3.13-slim AS builder

# Set environment variables
ENV POETRY_VERSION=2.1.2 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies & Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only dependency files first (for better cache)
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# Now copy entire source code
COPY . .

# =================== Final stage ===================
FROM python:3.13-slim

# Install runtime dependencies (uvicorn is needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Set working directory
WORKDIR /app

# Copy installed packages and app from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /app /app

# Give ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port used by FastAPI
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
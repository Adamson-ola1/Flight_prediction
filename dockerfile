# ============================================================
# Flight Prediction - FastAPI Backend
# ============================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Send Python output directly to the terminal
ENV PYTHONUNBUFFERED=1

# Application directory
WORKDIR /app


# ============================================================
# Install Python dependencies
# ============================================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ============================================================
# Copy application files
# ============================================================

COPY backend/ ./backend/
COPY src/ ./src/
COPY models/ ./models/
COPY outputs/ ./outputs/
COPY config.py .
COPY main.py .


# ============================================================
# FastAPI
# ============================================================

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
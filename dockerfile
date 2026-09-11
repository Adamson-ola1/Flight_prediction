ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY src/ ./src/
COPY models/ ./models/
COPY outputs/ ./outputs/
COPY config.py .
COPY main.py .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
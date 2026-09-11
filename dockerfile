# syntax=docker/dockerfile:1

FROM python:3.11-slim

# LightGBM requires the OpenMP runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# The CI workflow runs the training/evaluation pipeline before this image is built.
# The generated models/ and outputs/ are therefore included in the image.
COPY . .

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

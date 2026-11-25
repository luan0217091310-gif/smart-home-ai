FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libgl1 libglib2.0-0 tzdata \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/stream_producer/requirements.txt services/stream_producer/requirements.txt
COPY services/worker_face/requirements.txt services/worker_face/requirements.txt
RUN pip install --no-cache-dir -r services/worker_face/requirements.txt
COPY shared/ shared/
COPY config/ config/
COPY scripts/ scripts/
COPY services/__init__.py services/__init__.py
COPY services/worker_face/ services/worker_face/
CMD ["python", "-W", "ignore", "services/worker_face/main.py"]

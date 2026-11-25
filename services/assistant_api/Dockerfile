FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg tzdata curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/stream_producer/requirements.txt services/stream_producer/requirements.txt
COPY services/assistant_api/requirements.txt services/assistant_api/requirements.txt
RUN pip install --no-cache-dir -r services/assistant_api/requirements.txt
COPY shared/ shared/
COPY config/ config/
COPY scripts/ scripts/
COPY services/__init__.py services/__init__.py
COPY services/assistant_api/ services/assistant_api/
EXPOSE 8000
CMD ["uvicorn", "services.assistant_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

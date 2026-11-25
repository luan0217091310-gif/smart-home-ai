FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg tzdata && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/stream_producer/requirements.txt /tmp/req.txt
RUN pip install --no-cache-dir -r /tmp/req.txt
COPY shared/ shared/
COPY config/ config/
COPY services/__init__.py services/__init__.py
COPY services/stream_producer/ services/stream_producer/
CMD ["python", "services/stream_producer/main.py"]

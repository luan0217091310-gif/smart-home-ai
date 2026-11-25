FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 git tzdata     && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/stream_producer/requirements.txt services/stream_producer/requirements.txt
COPY services/worker_object/requirements.txt services/worker_object/requirements.txt
RUN pip install --no-cache-dir -r services/worker_object/requirements.txt
COPY shared/ shared/
COPY config/ config/
COPY services/__init__.py services/__init__.py
COPY services/worker_object/ services/worker_object/
CMD ["python", "services/worker_object/main.py"]

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends tzdata curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/stream_producer/requirements.txt services/stream_producer/requirements.txt
COPY services/dashboard/requirements.txt services/dashboard/requirements.txt
RUN pip install --no-cache-dir -r services/dashboard/requirements.txt
COPY shared/ shared/
COPY config/ config/
COPY scripts/ scripts/
COPY services/__init__.py services/__init__.py
COPY services/dashboard/ services/dashboard/
EXPOSE 8501
CMD ["streamlit", "run", "services/dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]

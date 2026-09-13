FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
ENV STREAMLIT_SERVER_MAXUPLOADSIZE=500

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpcap-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
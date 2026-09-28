FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
<<<<<<< HEAD
=======
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
>>>>>>> e5900b2 (doker update pipeline update)
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
ENV STREAMLIT_SERVER_MAXUPLOADSIZE=500
<<<<<<< HEAD

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
=======
ENV HOME=/home/appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpcap-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appuser \
    && useradd --system --gid appuser --create-home --home-dir /home/appuser appuser

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app /home/appuser

USER appuser
>>>>>>> e5900b2 (doker update pipeline update)

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

<<<<<<< HEAD
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
=======
CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
>>>>>>> e5900b2 (doker update pipeline update)


FROM --platform=linux/amd64 python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

ARG UID=10001
RUN useradd -m -u ${UID} -s /bin/bash appuser

RUN mkdir -p /home/appuser/.cache/huggingface 
RUN mkdir -p /home/appuser/.cache/matplotlib 
RUN mkdir -p /home/appuser/.config/matplotlib 
RUN chown -R appuser /home/appuser

RUN mkdir -p /app/temp /app/splits && chown -R appuser:appuser /app/temp /app/splits

ENV MPLCONFIGDIR=/home/appuser/.config/matplotlib
ENV HF_HOME=/home/appuser/.cache/huggingface

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

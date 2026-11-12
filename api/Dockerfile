FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODELO_API_PATH=/tmp/modelo_api.joblib

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    libglib2.0-0 \
    libgl1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN groupadd --gid 1000 rendersecrets && \
    useradd --create-home --uid 10001 --groups rendersecrets apiuser && \
    mkdir -p /app/modelos && \
    chown -R apiuser:apiuser /app

USER apiuser

EXPOSE 8000

CMD ["sh", "-c", "set -eu; umask 077; python -c 'import base64,gzip,os,pathlib; data=pathlib.Path(\"/etc/secrets/modelo_api.joblib.gz.b64\").read_bytes(); pathlib.Path(os.environ[\"MODELO_API_PATH\"]).write_bytes(gzip.decompress(base64.b64decode(data, validate=True)))'; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

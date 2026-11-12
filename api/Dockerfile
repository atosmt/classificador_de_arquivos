
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala o OCR em português e as bibliotecas do OpenCV.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    libglib2.0-0 \
    libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Instala as dependências Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia somente o código da aplicação.
COPY app/ ./app/

# Cria um usuário sem privilégios de administrador.
RUN useradd --create-home --uid 10001 apiuser && \
    mkdir -p /app/modelos && \
    chown -R apiuser:apiuser /app

USER apiuser

EXPOSE 8000

# A porta pode ser definida pelo ambiente de hospedagem.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

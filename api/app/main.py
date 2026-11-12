"""API de classificação de RG. Os bytes das imagens não são persistidos."""
import base64
import binascii
import io
from PIL import Image, UnidentifiedImageError

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from .features import extrair_features
from .modelo import MODELO, prever

app = FastAPI(title='Classificador de RG — API', version='1.0.0')
LIMITE_BYTES = 5 * 1024 * 1024
LIMITE_PIXELS = 12_000_000
TIPOS_ACEITOS = {'image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'}


class ImagemBase64(BaseModel):
    imagem_base64: str = Field(min_length=1, max_length=8_000_000)



def decodificar_imagem(dados: bytes) -> np.ndarray:
    if not dados:
        raise HTTPException(
            status_code=422,
            detail="Imagem vazia"
        )

    if len(dados) > LIMITE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Imagem maior que 5 MB"
        )

    try:
        with Image.open(io.BytesIO(dados)) as arquivo:
            largura, altura = arquivo.size

            if largura <= 0 or altura <= 0:
                raise HTTPException(
                    status_code=422,
                    detail="Dimensões inválidas"
                )

            if largura * altura > LIMITE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Imagem com resolução muito alta"
                )

            formatos = {"JPEG", "PNG", "WEBP", "BMP", "TIFF"}

            if arquivo.format not in formatos:
                raise HTTPException(
                    status_code=422,
                    detail="Formato de imagem não suportado"
                )

    except (UnidentifiedImageError, OSError,
            ValueError, Image.DecompressionBombError) as erro:
        raise HTTPException(
            status_code=422,
            detail="Arquivo não é uma imagem válida"
        ) from erro

    imagem = cv2.imdecode(
        np.frombuffer(dados, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )

    if imagem is None or imagem.ndim != 3:
        raise HTTPException(
            status_code=422,
            detail="Arquivo não é uma imagem válida"
        )

    return imagem

def processar(dados: bytes) -> dict:
    imagem = decodificar_imagem(dados)
    try:
        features = extrair_features(imagem)
        return prever(features)
    except Exception as exc:
        # Não devolver detalhes internos ou OCR com dados pessoais ao cliente.
        # Erros de instalação são diagnosticados localmente no terminal.
        raise HTTPException(status_code=500, detail='Falha ao processar imagem') from exc


@app.get('/health')
def health():
    return {'status': 'ok', 'modelo_disponivel': MODELO.is_file()}


@app.post('/predict')
async def predict(arquivo: UploadFile = File(...)):
    if arquivo.content_type not in TIPOS_ACEITOS:
        raise HTTPException(status_code=415, detail='Envie uma imagem JPEG, PNG, WEBP, BMP ou TIFF')
    dados = await arquivo.read(LIMITE_BYTES + 1)
    await arquivo.close()
    if len(dados) > LIMITE_BYTES:
        raise HTTPException(status_code=413, detail='Imagem maior que 5 MB')
    if not MODELO.is_file():
        raise HTTPException(status_code=503, detail='Modelo ainda não foi exportado')
    return await run_in_threadpool(processar, dados)


@app.post('/predict/base64')
async def predict_base64(entrada: ImagemBase64):
    if not MODELO.is_file():
        raise HTTPException(status_code=503, detail='Modelo ainda não foi exportado')
    texto = entrada.imagem_base64
    if texto.startswith('data:'):
        try:
            prefixo, texto = texto.split(',', 1)
            if not prefixo.endswith(';base64'):
                raise ValueError('Prefixo inválido')
        except ValueError as exc:
            raise HTTPException(status_code=422, detail='Base64 inválido') from exc
    try:
        dados = base64.b64decode(texto, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail='Base64 inválido') from exc
    return await run_in_threadpool(processar, dados)

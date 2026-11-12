"""Testes da camada HTTP; sem OCR/modelo para serem rápidos."""
import base64
import io
from PIL import Image
import cv2
import numpy as np
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def imagem_teste():
    ok, buffer = cv2.imencode('.png', np.zeros((24, 32, 3), dtype=np.uint8))
    assert ok
    return buffer.tobytes()


def test_health():
    resposta = client.get('/health')
    assert resposta.status_code == 200
    assert 'modelo_disponivel' in resposta.json()


def test_rejeita_tipo():
    resposta = client.post('/predict', files={'arquivo': ('teste.txt', b'x', 'text/plain')})
    assert resposta.status_code == 415


def test_rejeita_imagem_invalida(monkeypatch):
    monkeypatch.setattr(main.MODELO.__class__, 'is_file', lambda _: True)
    resposta = client.post('/predict', files={'arquivo': ('teste.png', b'nada', 'image/png')})
    assert resposta.status_code == 422


def test_predict(monkeypatch):
    monkeypatch.setattr(main.MODELO.__class__, 'is_file', lambda _: True)
    monkeypatch.setattr(main, 'extrair_features', lambda imagem: {'altura_px': imagem.shape[0]})
    monkeypatch.setattr(main, 'prever', lambda atributos: {'classe': 'rg_novo', 'confianca': 0.9})
    resposta = client.post('/predict', files={'arquivo': ('teste.png', imagem_teste(), 'image/png')})
    assert resposta.status_code == 200
    assert resposta.json()['classe'] == 'rg_novo'


def test_rejeita_arquivo_grande():
    dados = b"x" * (main.LIMITE_BYTES + 1)

    resposta = client.post(
        "/predict",
        files={"arquivo": ("grande.png", dados, "image/png")}
    )

    assert resposta.status_code == 413


def test_rejeita_imagem_muito_grande():
    imagem = Image.new("RGB", (4000, 4000))

    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")

    try:
        main.decodificar_imagem(buffer.getvalue())
    except main.HTTPException as erro:
        assert erro.status_code == 413
    else:
        raise AssertionError("A imagem deveria ser rejeitada")


def test_rejeita_base64_invalido(monkeypatch):
    monkeypatch.setattr(
        main.MODELO.__class__,
        "is_file",
        lambda _: True
    )

    resposta = client.post(
        "/predict/base64",
        json={"imagem_base64": "conteudo-invalido!!!"}
    )

    assert resposta.status_code == 422


def test_predict_base64(monkeypatch):
    monkeypatch.setattr(
        main.MODELO.__class__,
        "is_file",
        lambda _: True
    )

    monkeypatch.setattr(
        main,
        "extrair_features",
        lambda imagem: {"altura_px": imagem.shape[0]}
    )

    monkeypatch.setattr(
        main,
        "prever",
        lambda atributos: {
            "classe": "rg_antigo",
            "confianca": 0.9
        }
    )

    dados = base64.b64encode(imagem_teste()).decode("utf-8")

    resposta = client.post(
        "/predict/base64",
        json={"imagem_base64": dados}
    )

    assert resposta.status_code == 200
    assert resposta.json()["classe"] == "rg_antigo"


"""Testes da camada HTTP; sem OCR/modelo para serem rápidos."""
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

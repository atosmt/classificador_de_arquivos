"""Carrega somente artefatos de modelo locais e confiáveis.

Não abra modelos pickle/joblib de fontes desconhecidas: desserializar pode
executar código. O bundle deve ser gerado pelo nosso exportador.
"""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

MODELO = Path(__file__).resolve().parents[1] / 'modelos' / 'modelo_api.joblib'


@lru_cache(maxsize=1)
def carregar_modelo():
    if not MODELO.is_file():
        raise FileNotFoundError(
            'Modelo da API ausente. Execute python exportar_modelo.py com o CSV privado.'
        )
    pacote = joblib.load(MODELO)
    if not isinstance(pacote, dict) or not {'pipeline', 'features'} <= pacote.keys():
        raise ValueError('Artefato incompatível: esperado pipeline e features')
    if not hasattr(pacote['pipeline'], 'predict') or not isinstance(pacote['features'], list):
        raise ValueError('Artefato inválido')
    return pacote


def prever(features: dict) -> dict:
    pacote = carregar_modelo()
    esperadas = pacote['features']
    faltantes = [c for c in esperadas if c not in features]
    if faltantes:
        raise ValueError(f'Características ausentes: {faltantes}')
    quadro = pd.DataFrame([{col: features[col] for col in esperadas}])
    pipeline = pacote['pipeline']
    classe = str(pipeline.predict(quadro)[0])
    resposta = {'classe': classe}
    if hasattr(pipeline, 'predict_proba'):
        probabilidades = pipeline.predict_proba(quadro)[0]
        classes = pipeline.classes_
        probs = {str(c): round(float(p), 6) for c, p in zip(classes, probabilidades)}
        resposta['probabilidades'] = probs
        resposta['confianca'] = probs[classe]
    return resposta

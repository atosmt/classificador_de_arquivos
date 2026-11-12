import re
import unicodedata

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

PALAVRAS_CHAVE = (
    'BRASIL', 'REPUBLICA', 'IDENTIFICACAO', 'CPF',
    'NASCIMENTO', 'FILIACAO', 'REGISTRO GERAL', 'CARTEIRA DE IDENTIDADE',
)


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize('NFD', texto.upper())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')


def ler_melhor_texto(imagem_bgr: np.ndarray):
    orientacoes = (
        ('original', imagem_bgr),
        ('90_direita', cv2.rotate(imagem_bgr, cv2.ROTATE_90_CLOCKWISE)),
        ('90_esquerda', cv2.rotate(imagem_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)),
        ('180', cv2.rotate(imagem_bgr, cv2.ROTATE_180)),
    )
    melhor = ('', 'original', -1, -1.0)
    for nome, rotacionada in orientacoes:
        cinza = cv2.cvtColor(rotacionada, cv2.COLOR_BGR2GRAY)
        dados = pytesseract.image_to_data(
            cinza, lang='por', config='--psm 6', output_type=Output.DICT,
            timeout=12,
        )
        palavras, confiancas = [], []
        for palavra, conf in zip(dados['text'], dados['conf']):
            palavra = str(palavra).strip()
            if palavra:
                palavras.append(palavra)
                try:
                    conf = float(conf)
                    if conf >= 0:
                        confiancas.append(conf)
                except (ValueError, TypeError):
                    pass
        texto = ' '.join(palavras)
        texto_normalizado = normalizar_texto(texto)
        pontuacao = sum(termo in texto_normalizado for termo in PALAVRAS_CHAVE)
        confianca = sum(confiancas) / len(confiancas) if confiancas else 0.0
        if (pontuacao, confianca) > (melhor[2], melhor[3]):
            melhor = (texto, nome, pontuacao, confianca)
        if pontuacao >= 3:
            break
    return melhor


def extrair_features(imagem_bgr: np.ndarray) -> dict:
    altura, largura = imagem_bgr.shape[:2]
    texto, orientacao, pontuacao, confianca = ler_melhor_texto(imagem_bgr)
    texto_normalizado = normalizar_texto(texto)
    cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    detector_rosto = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    if detector_rosto.empty():
        raise RuntimeError('Detector de rosto indisponível')
    rostos = detector_rosto.detectMultiScale(
        cinza, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25)
    )
    try:
        tem_qr = int(cv2.QRCodeDetector().detect(imagem_bgr)[0])
    except cv2.error:
        tem_qr = 0
    tem_filiacao = int('FILIACAO' in texto_normalizado)
    tem_identidade = int(any(x in texto_normalizado for x in (
        'CARTEIRA DE IDENTIDADE', 'IDENTIDADE NACIONAL', 'IDENTIFICACAO'
    )))
    return {
        'arquivo': '',
        'largura_px': largura,
        'altura_px': altura,
        'proporcao_largura_altura': round(largura / altura, 3),
        'orientacao_ocr_escolhida': orientacao,
        'pontuacao_palavras_chave': pontuacao,
        'confianca_media_ocr': round(confianca, 2),
        'quantidade_caracteres': len(texto_normalizado),
        'quantidade_palavras': len(texto.split()),
        'texto_extraido': '',
        'tem_texto_rg': int('REGISTRO GERAL' in texto_normalizado or re.search(r'\bRG\b', texto_normalizado) is not None),
        'tem_cpf': int('CPF' in texto_normalizado),
        'tem_republica': int('REPUBLICA' in texto_normalizado),
        'tem_brasil': int('BRASIL' in texto_normalizado),
        'tem_carteira_de_identidade': tem_identidade,
        'tem_data_nascimento': int('NASCIMENTO' in texto_normalizado or 'DATA DE NASC' in texto_normalizado),
        'tem_filiacao': tem_filiacao,
        'tem_filiacao_bilingue': int(tem_filiacao and ('PARENTAGE' in texto_normalizado or 'FILIATION' in texto_normalizado)),
        'possivel_cnh': int('CARTEIRA NACIONAL DE HABILITACAO' in texto_normalizado or re.search(r'\bCNH\b', texto_normalizado) is not None),
        'tem_qr_code': tem_qr,
        'tem_rosto_detectado': int(len(rostos) > 0),
        'nitidez_imagem': round(float(cv2.Laplacian(cinza, cv2.CV_64F).var()), 2),
    }

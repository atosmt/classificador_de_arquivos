"""Treina e exporta o mesmo pipeline Random Forest do notebook atual.

Uso: python exportar_modelo.py CAMINHO_DO_CSV
O CSV permanece no computador; nunca é adicionado ao ZIP/Git.
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

COLUNAS_EXCLUIDAS = (
    'classe', 'arquivo', 'texto_extraido', 'pontuacao_palavras_chave',
    'tem_texto_rg', 'tem_carteira_de_identidade',
)


def exportar(caminho_csv: Path) -> Path:
    dados = pd.read_csv(caminho_csv, encoding='utf-8-sig')
    obrigatorias = set(COLUNAS_EXCLUIDAS)
    if dados.empty or not obrigatorias.issubset(dados.columns):
        raise ValueError('CSV vazio ou com colunas obrigatórias ausentes')
    if dados['classe'].isna().any() or dados['classe'].nunique() < 2:
        raise ValueError('CSV precisa conter classes válidas')
    x = dados.drop(columns=list(COLUNAS_EXCLUIDAS)).copy()
    y = dados['classe'].astype(str)
    categoricas = x.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    numericas = [col for col in x.columns if col not in categoricas]
    for coluna in numericas:
        x[coluna] = pd.to_numeric(x[coluna], errors='coerce')
    transformacoes = []
    if numericas:
        transformacoes.append(('numericos', Pipeline([
            ('preencher', SimpleImputer(strategy='median')),
        ]), numericas))
    if categoricas:
        transformacoes.append(('categoricos', Pipeline([
            ('preencher', SimpleImputer(strategy='most_frequent')),
            ('codificar', OneHotEncoder(handle_unknown='ignore')),
        ]), categoricas))
    pipeline = Pipeline([
        ('preprocessar', ColumnTransformer(transformacoes)),
        ('classificador', RandomForestClassifier(n_estimators=100, random_state=42)),
    ])
    pipeline.fit(x, y)
    destino = Path(__file__).resolve().parent / 'modelos' / 'modelo_api.joblib'
    destino.parent.mkdir(exist_ok=True)
    joblib.dump({'pipeline': pipeline, 'features': x.columns.tolist()}, destino)
    print(f'Modelo exportado: {destino} ({len(x)} registros, {len(x.columns)} features)')
    print('Atenção: treinamento sobre todo o CSV serve à API; métricas devem ser avaliadas separadamente.')
    return destino


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python exportar_modelo.py caminho/analise_documentosT.csv')
    exportar(Path(sys.argv[1]))

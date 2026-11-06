# Resultados do treinamento

Avaliação realizada usando o CSV `analise_documentosT.csv` enviado para análise: **300 documentos** (100 por classe), divididos em **240 registros para treinamento** e **60 para teste** (20 documentos de cada classe), com `random_state=42`.

| Modelo | Acurácia | Precisão macro | Recall macro | F1-score macro |
| --- | ---: | ---: | ---: | ---: |
| Random Forest | **98,33%** | **98,41%** | **98,33%** | **98,33%** |
| SVM | 96,67% | 96,97% | 96,67% | 96,66% |
| KNN | 93,33% | 93,33% | 93,33% | 93,33% |

## Interpretação

- **Random Forest**: acertou 59 de 60 documentos de teste, sendo o melhor resultado neste experimento.
- **SVM**: acertou 58 de 60 documentos de teste.
- **KNN**: acertou 56 de 60 documentos de teste, já com padronização de escala.

Os modelos foram avaliados com o mesmo conjunto de teste. A imputação, codificação de atributos categóricos e padronização (nos modelos que a utilizam) foram ajustadas a partir do conjunto de treinamento, por meio de pipelines.

## Limitações

A avaliação usa **uma única divisão** treino/teste e um conjunto de apenas 300 registros. Não houve validação externa com imagens novas. Documentos repetidos, variações da mesma imagem ou dados de aumento artificial podem inflar a estimativa de desempenho. Antes de usar em produção, é importante testar com documentos independentes e verificar possíveis duplicatas.

Nenhum texto pessoal dos documentos ou imagem original foi incluído neste arquivo.

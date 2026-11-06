# Classificador de RG

Projeto da disciplina de Sistemas Inteligentes para classificar imagens em três grupos:
**RG antigo**, **RG novo** e **documento inválido**.

## Organização

- `analise_imagens.ipynb` — extrai características das imagens com OpenCV e OCR, gera um CSV privado.
- `treinamento_modelos.ipynb` — divide os dados, treina KNN, SVM e Random Forest e apresenta as métricas e matrizes de confusão.
- `requirements.txt` — bibliotecas Python necessárias.
- `limpar_notebook_analise.py` — remove saídas do notebook de análise antes de publicá-lo.
- `RESULTADOS.md` — comparação obtida com o CSV usado nos testes.
- `COMO_PUBLICAR.md` — passos para substituir os arquivos no repositório clonado e enviar para o GitHub.
- `random_forest.pkl` — modelo antigo que já existe no GitHub; o arquivo **não foi substituído nem retreinado** neste pacote.

## Treinamento no Google Colab (sem instalar Python no computador)

1. Abra `treinamento_modelos.ipynb` no [Google Colab](https://colab.research.google.com/).
2. Envie o CSV `analise_documentosT.csv` **somente para a sessão privada do Colab**, sem colocá-lo no GitHub.
3. Se a sessão não tiver as bibliotecas, execute `!pip install pandas scikit-learn matplotlib` em uma nova célula.
4. Execute as células do notebook na ordem. Confira acurácia, precisão, recall, F1-score e as matrizes de confusão.

O treinamento também aceita `analise_documentos.csv` e procura os arquivos no diretório atual, em `dados_privados/` e em `/content/`, ou no caminho indicado pela variável `CSV_CLASSIFICADOR`.

## Se precisar gerar um novo CSV a partir das imagens

No Google Colab, abra `analise_imagens.ipynb`, extraia o `Projeto_Suzana.zip` **somente na sessão privada**, execute a célula de instalação do Tesseract (Português), e depois a de extração. A estrutura original `Projeto_Suzana/dataset_rgs/dataset_rgs/` é reconhecida pelo notebook.

O CSV gerado tem 23 colunas, incluindo a coluna `texto_extraido` que fica vazia por padrão para reduzir o tratamento de dados pessoais. O treinamento ignora essa coluna. Não é necessário refazer a análise quando o CSV original já está pronto.

## Como os modelos são comparados

- Divisão estratificada 80% treinamento / 20% teste, com `random_state=42`.
- Imputação e codificação de variáveis dentro de pipelines para evitar vazamento de dados da etapa de teste.
- Padronização no KNN e no SVM; Random Forest sem normalização.
- Métricas: acurácia, precisão macro, recall macro, F1 macro e matriz de confusão.

Veja os números observados em `RESULTADOS.md`. **Essas métricas não garantem desempenho em documentos que não participaram da coleta**; testes externos e checagem de duplicatas seriam necessários.

## Privacidade

**Não adicione ao GitHub** as imagens dos documentos, os CSVs ou textos pessoais extraídos pelo OCR. Use o CSV somente localmente ou em sessão privada do Colab. O `.gitignore` protege contra adições acidentais, mas não remove arquivos que já tenham sido versionados. Revise sempre o `git status` antes de publicar.

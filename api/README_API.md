# Etapa 2 — Classificador de RG por API

Pasta `api/` para copiar para a RAIZ do repositório `classificador_de_arquivos`.
Não substitui o notebook nem o `random_forest.pkl` legado.

## O que foi implementado

- `GET /health`: informa se o servidor está ativo e se o modelo exportado existe.
- `POST /predict`: recebe arquivo JPEG, PNG, WEBP, BMP ou TIFF (multipart/form-data).
- `POST /predict/base64`: recebe JSON `{ "imagem_base64": "..." }`.
- A extração em `app/features.py` foi adaptada do notebook `analise_imagens.ipynb`.
- O modelo é um pipeline Random Forest exportado a partir do **CSV privado do grupo**.
- A documentação interativa é criada automaticamente em `/docs`.

**Por segurança, não incluí rota que baixa URL arbitrária**: isso pode expor recursos internos
(SSRF). O upload ou Base64 atendem à necessidade de enviar imagens ao serviço.

## Instalação no Windows (PowerShell)

Instale Python 3.11 pelo site oficial e marque *Add python.exe to PATH*.
Feche e reabra o VS Code, confira `python --version` ou `py --version`.

Instale também **Tesseract OCR com idioma português (por)** no Windows, com o
executável acessível pelo PATH, ou configure `TESSDATA_PREFIX` e o caminho do executável
na integração local do pytesseract. Confira `tesseract --list-langs` e procure `por`.

Abra o terminal na pasta `api`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest httpx
```

Se o PowerShell bloquear o Activate.ps1, use os executáveis diretamente:
` .\.venv\Scripts\python.exe -m pip install -r requirements.txt `.

## Exportar o modelo a partir do CSV privado

Com o CSV `analise_documentosT.csv` mantido apenas no seu computador:

```powershell
python exportar_modelo.py "C:\caminho\privado\analise_documentosT.csv"
```

O arquivo `modelos/modelo_api.joblib` será criado **localmente** e está ignorado pelo Git.
O exportador usa o mesmo conjunto de colunas excluídas, imputação, OneHotEncoder e
RandomForest (100 árvores, semente 42) do notebook revisado. Ao exportar para uso em
previsões, treina com **todas** as linhas; para avaliação científica, use os resultados
anteriores com treino/teste ou uma validação externa.

**Não use diretamente o `random_forest.pkl` antigo sem verificar formato e compatibilidade.**
Arquivos `.pkl` e `.joblib` podem executar código ao serem carregados; só utilize os
que você mesmo gerou em ambiente confiável.

## Rodar e testar

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abra: http://127.0.0.1:8000/docs . Expanda `POST /predict`, clique
**Try it out**, selecione uma imagem de teste **sem dados reais de identidade**
e clique em **Execute**.

Teste automático da camada HTTP (em outro terminal na pasta `api`):

```powershell
python -m pytest -q
```

## Publicação (Render ou outro serviço)

O `Dockerfile` inclui Tesseract em português. O deploy precisa ter o arquivo
`modelos/modelo_api.joblib`, que **não deve** ser enviado ao GitHub público.
Como este ZIP não inclui modelo nem CSV, subir o Dockerfile sozinho deixa `/health`
ativo, mas `/predict` devolve `503` até o modelo ser disponibilizado por meio
seguro em ambiente privado. Use armazenamento protegido, imagem de contêiner
privada ou mecanismo de artefatos com controle de acesso.

Recomendação: **primeiro validar localmente com dados fictícios**, verificar
privacidade do GitHub e planejar o deploy seguro antes de tornar a API pública.

## Segurança e privacidade

- Nunca envie documentos pessoais reais para a API pública de demonstração.
- Imagens são processadas em memória e não são gravadas pelo código.
- Limites: 5 MB por arquivo e 12 milhões de pixels por imagem após a decodificação.
- Erros não retornam texto de OCR nem detalhes de exceções.
- Para uma versão pública real: autenticação, limitação de requisições,
  redução de dimensões **antes** de decodificar arquivos gigantes,
  isolamento do OCR e revisão de logs e política de retenção.

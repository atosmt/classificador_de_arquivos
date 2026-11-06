# Enviar as correções para o GitHub

O ZIP contém **apenas arquivos de código e documentação**, sem `.git`, imagens ou CSV privado. O `random_forest.pkl` antigo permanece no repositório original, e não precisa ser substituído.

## Opção simples: sua pasta do Git já está clonada

1. Extraia este ZIP para **dentro da pasta clonada `classificador_de_arquivos`**. Confirme a substituição dos arquivos com os mesmos nomes.
2. Abra essa pasta no VS Code.
3. No terminal do VS Code, execute:

```powershell
git status
git add .gitignore README.md requirements.txt analise_imagens.ipynb treinamento_modelos.ipynb limpar_notebook_analise.py RESULTADOS.md COMO_PUBLICAR.md
git commit -m "Organiza treinamento e notebooks"
git push origin ajustes-treinamento-e-analise
```

Caso ainda esteja na `main`, **antes de copiar os arquivos** execute:

```powershell
git fetch origin
git switch ajustes-treinamento-e-analise
```

Se a branch não existir localmente: `git switch --track origin/ajustes-treinamento-e-analise`.

**Não use `git add -A` se houver arquivos particulares não conferidos.** O `git status` deve mostrar somente os arquivos acima, nunca CSV ou imagens. Nenhum Python é necessário para publicar.

## Depois

Abra o repositório no GitHub e crie um Pull Request de `ajustes-treinamento-e-analise` para `main`. Faça o merge quando estiver de acordo com as alterações.

## Treinar os modelos

Pode usar o Google Colab com o notebook e enviar o CSV diretamente à sessão privada, sem precisar instalar o Python no Windows. Nunca suba o CSV para o GitHub.

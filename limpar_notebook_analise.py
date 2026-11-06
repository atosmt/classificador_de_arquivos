"""Remove saídas do notebook de análise antes de publicá-lo no GitHub."""
from pathlib import Path
import nbformat

arquivo = Path(__file__).with_name("analise_imagens.ipynb")
if not arquivo.is_file():
    raise FileNotFoundError(f"Notebook não encontrado: {arquivo}")

notebook = nbformat.read(arquivo, as_version=4)
for celula in notebook.cells:
    if celula.cell_type == "code":
        celula.outputs = []
        celula.execution_count = None
nbformat.validate(notebook)
nbformat.write(notebook, arquivo)
print("Saídas removidas. Revise o conteúdo antes de publicar.")

import os
import json
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Chave OPENAI_API_KEY não encontrada! Configure-a no arquivo .env")

PERSIST_DIR = "text_index"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Arquivos redundantes ou resumidos — já cobertos por versões mais completas
SKIP_FILES = {"catalogo_consolidado_resumido.json"}

# Diretórios varridos em ordem (arquivos com mesmo nome em dirs posteriores são ignorados)
SEARCH_DIRS = [".", "json_folders", "Folders"]


def carregar_json(json_path: Path) -> list[Document]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    docs = []
    for page in data.get("pages", []):
        text = page.get("text_markdown", "").strip()
        if text:
            docs.append(Document(
                page_content=text,
                metadata={"source": json_path.name, "page": page.get("page_number", 0)},
            ))
    return docs


def main():
    base = Path(__file__).parent
    todos_docs: list[Document] = []
    arquivos_vistos: set[str] = set()

    print("=== Carregando documentos ===")
    for pasta in SEARCH_DIRS:
        caminho = base / pasta
        if not caminho.exists():
            continue
        for json_file in sorted(caminho.glob("*.json")):
            if json_file.name in SKIP_FILES or json_file.name in arquivos_vistos:
                continue
            arquivos_vistos.add(json_file.name)
            try:
                docs = carregar_json(json_file)
                todos_docs.extend(docs)
                print(f"  {json_file.name}: {len(docs)} páginas")
            except Exception as e:
                print(f"  ERRO em {json_file.name}: {e}")

    total_arquivos = len(arquivos_vistos)
    print(f"\nTotal: {len(todos_docs)} páginas de {total_arquivos} arquivo(s)\n")

    if not todos_docs:
        print("Nenhum documento carregado. Abortando.")
        return

    print("=== Dividindo em chunks ===")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    chunks = splitter.split_documents(todos_docs)
    print(f"{len(chunks)} chunks gerados (tamanho={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})\n")

    persist_path = base / PERSIST_DIR
    if persist_path.exists():
        print(f"=== Removendo índice antigo ({PERSIST_DIR}/) ===")
        shutil.rmtree(persist_path)
        print("Índice removido.\n")

    print("=== Criando índice vetorial ===")
    embeddings = OpenAIEmbeddings()
    Chroma.from_documents(chunks, embedding=embeddings, persist_directory=str(persist_path))
    print(f"Índice salvo em {PERSIST_DIR}/\n")
    print("Concluído!")


if __name__ == "__main__":
    main()

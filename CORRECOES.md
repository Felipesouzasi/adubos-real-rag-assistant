# Correções — RAG Tião (Adubos Real)

Registro em primeira pessoa de cada alteração feita no projeto, com contexto do problema e o que foi mudado.

---

## [P0] Imports inválidos e dependências faltando

**Problema:** `main.py` importava `ChatOpenAI` de `langchain_community` (caminho deprecated) e `load_qa_chain` de `langchain_classic`, pacote que não existe no PyPI. `update_db.py` usava `langchain_text_splitters` sem ele estar no `requirements.txt`. Além disso, `python-dotenv`, `requests` e `streamlit` também estavam faltando no arquivo de dependências.

**O que mudamos:**
- Em [main.py](main.py): substituímos `from langchain_community.chat_models.openai import ChatOpenAI` por `from langchain_openai import ChatOpenAI` e `from langchain_classic.chains.question_answering import load_qa_chain` por `from langchain.chains.question_answering import load_qa_chain`
- Em [requirements.txt](requirements.txt): adicionamos `langchain-text-splitters`, `python-dotenv`, `requests` e `streamlit`

---

## [P0] Diretório do vectordb inconsistente

**Problema:** O índice ChromaDB salvo no disco estava em `text_index/`, mas tanto `main.py` quanto `update_db.py` referenciavam `text_json_index/` — diretório que não existia. Na prática, o RAG estava carregando um banco vazio e respondendo sem nenhum contexto de documento.

**O que mudamos:**
- Em [main.py](main.py): `persist_directory="text_json_index"` → `persist_directory="text_index"`
- Em [update_db.py](update_db.py): `persist_directory="text_json_index"` → `persist_directory="text_index"`

---

## [P0] `max_tokens=300` truncava respostas

**Problema:** O modelo estava configurado com limite de 300 tokens (~220 palavras). Respostas com tabelas de dosagem, listas de produtos ou explicações técnicas eram cortadas no meio sem aviso.

**O que mudamos:**
- Em [main.py](main.py): `max_tokens=300` → `max_tokens=1000`

---

## [P0] `db_json.persist()` deprecated

**Problema:** ChromaDB ≥ 0.4.0 removeu o método `.persist()` — o salvamento passou a ser automático. Chamar esse método jogava `AttributeError` ao rodar `update_db.py` em qualquer ambiente com versão recente da biblioteca.

**O que mudamos:**
- Em [update_db.py](update_db.py): removemos a linha `db_json.persist()`

---

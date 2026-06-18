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

## [P1] RAG indexava apenas um documento

**Problema:** `update_db.py` processava somente `catalogo_consolidado.json`. Os demais materiais (folders de citros, cafezal, folhosas, hortifruti, enraizamento, bula do Zapp QI) não eram indexados — qualquer pergunta sobre esses produtos retornava sem contexto. Além disso, o `chunk_overlap=20` (2% do chunk) fazia frases na fronteira entre chunks serem perdidas no retrieval.

**O que mudamos:**
- Reescrevemos [update_db.py](update_db.py) do zero com varredura automática dos diretórios `.`, `json_folders/` e `Folders/`, indexando todos os `.json` encontrados
- `chunk_overlap` aumentado de `20` para `150` (15% do chunk_size)
- Adicionamos limpeza do índice antigo com `shutil.rmtree` antes de recriar, evitando duplicação ao rodar o script múltiplas vezes
- Adicionamos constante `SKIP_FILES` para excluir arquivos redundantes (`catalogo_consolidado_resumido.json`)
- Metadados do documento agora incluem o nome do arquivo-fonte em todos os chunks

---

## [P1] Respostas bloqueavam a UI sem feedback visual

**Problema:** A resposta da IA só aparecia depois de 100% gerada. Com `max_tokens=1000` e respostas técnicas longas, o usuário podia esperar 10-20 segundos olhando para "Pensando..." sem nenhum feedback. Não havia timeout configurado na chamada HTTP.

**O que mudamos:**
- Em [main.py](main.py): adicionamos `streaming=True` ao `ChatOpenAI`, importamos `StreamingResponse` e `HumanMessage`, e criamos o endpoint `POST /chat/stream` que transmite tokens em tempo real via `llm_model.astream()` e salva no cache ao final do stream
- Em [chat_ui.py](chat_ui.py): substituímos a chamada `requests.post` + `message_placeholder` por uma função geradora `stream_resposta()` consumida via `st.write_stream()`, que exibe cada token conforme chega; adicionamos `timeout=(5, None)` (5s para conexão, sem limite de leitura) e tratamento separado para `ConnectionError` e `Timeout`

---

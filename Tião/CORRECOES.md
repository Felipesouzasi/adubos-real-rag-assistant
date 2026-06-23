# Correções — RAG Tião (Adubos Real)

Registro em primeira pessoa do que identifiquei como problema e o que alterei para resolver.

---

## [P0] Imports inválidos e dependências faltando

**Problema:** `main.py` importava `ChatOpenAI` de `langchain_community` (caminho deprecated) e `load_qa_chain` de `langchain_classic`, pacote que não existe no PyPI. `update_db.py` usava `langchain_text_splitters` sem ele estar no `requirements.txt`. `python-dotenv`, `requests` e `streamlit` também estavam faltando.

**O que mudei:**
- Em [main.py](main.py): substituí `from langchain_community.chat_models.openai import ChatOpenAI` por `from langchain_openai import ChatOpenAI` e `from langchain_classic.chains.question_answering import load_qa_chain` por `from langchain.chains.question_answering import load_qa_chain`
- Em [requirements.txt](requirements.txt): adicionei `langchain-text-splitters`, `python-dotenv`, `requests` e `streamlit`

---

## [P0] Diretório do vectordb inconsistente

**Problema:** O índice ChromaDB salvo no disco estava em `text_index/`, mas tanto `main.py` quanto `update_db.py` referenciavam `text_json_index/` — diretório que não existia. Na prática, o RAG carregava um banco vazio e respondia sem nenhum contexto de documento.

**O que mudei:**
- Em [main.py](main.py): `persist_directory="text_json_index"` → `persist_directory="text_index"`
- Em [update_db.py](update_db.py): `persist_directory="text_json_index"` → `persist_directory="text_index"`

---

## [P0] `max_tokens=300` truncava respostas

**Problema:** O modelo estava configurado com limite de 300 tokens (~220 palavras). Respostas com tabelas de dosagem, listas de produtos ou explicações técnicas eram cortadas no meio sem aviso.

**O que mudei:**
- Em [main.py](main.py): `max_tokens=300` → `max_tokens=1000`

---

## [P0] `db_json.persist()` deprecated

**Problema:** ChromaDB ≥ 0.4.0 removeu o método `.persist()` — o salvamento passou a ser automático. Chamar esse método jogava `AttributeError` ao rodar `update_db.py` em qualquer ambiente com versão recente da biblioteca.

**O que mudei:**
- Em [update_db.py](update_db.py): removi a linha `db_json.persist()`

---

## [P1] RAG indexava apenas um documento

**Problema:** `update_db.py` processava somente `catalogo_consolidado.json`. Os demais materiais (folders de citros, cafezal, folhosas, hortifruti, enraizamento, bula do Zapp QI) não eram indexados — qualquer pergunta sobre esses produtos retornava sem contexto. O `chunk_overlap=20` (2% do chunk) fazia frases na fronteira entre chunks serem perdidas no retrieval.

**O que mudei:**
- Reescrevi [update_db.py](update_db.py) com varredura automática dos diretórios `.`, `json_folders/` e `Folders/`, indexando todos os `.json` encontrados
- Aumentei o `chunk_overlap` de `20` para `150` (15% do chunk_size)
- Adicionei limpeza do índice antigo com `shutil.rmtree` antes de recriar, evitando duplicação ao rodar o script mais de uma vez
- Criei a constante `SKIP_FILES` para excluir arquivos redundantes como `catalogo_consolidado_resumido.json`
- Incluí o nome do arquivo-fonte nos metadados de todos os chunks

---

## [P1] Respostas bloqueavam a UI sem feedback visual

**Problema:** A resposta da IA só aparecia depois de 100% gerada. Com `max_tokens=1000` e respostas técnicas longas, o usuário esperava 10-20 segundos olhando para "Pensando..." sem nenhum feedback. Não havia timeout configurado na chamada HTTP.

**O que mudei:**
- Em [main.py](main.py): adicionei `streaming=True` ao `ChatOpenAI`, importei `StreamingResponse` e `HumanMessage`, e criei o endpoint `POST /chat/stream` que transmite tokens em tempo real via `llm_model.astream()` e salva no cache ao final do stream
- Em [chat_ui.py](chat_ui.py): substituí a chamada `requests.post` + `message_placeholder` por uma função geradora `stream_resposta()` consumida via `st.write_stream()`, que exibe cada token conforme chega; adicionei `timeout=(5, None)` e tratamento separado para `ConnectionError` e `Timeout`

---

## [P2] Arquivos sensíveis e binários rastreados no git

**Problema:** O `.gitignore` original excluía os JSONs de dados (`json_folders/`, `Folders/`) que são necessários para reconstruir o índice, mas não excluía os arquivos `.db` de runtime. O índice vetorial (`text_index/`) — binário grande e regenerável — estava sendo commitado.

**O que mudei:**
- Reescrevi [.gitignore](.gitignore): removi a exclusão de `json_folders/` e dos JSONs individuais, mantive `*.pdf`, `text_index/`, `*.db` e `.env` fora do repositório
- Criei [.env.example](.env.example) com template de todas as variáveis necessárias

---

## [P2] Autenticação de usuários e isolamento de dados

**Problema:** Qualquer pessoa acessava o Tião sem autenticação, via o histórico de todos os outros usuários e, futuramente, teria acesso a dados de comissão de outros consultores. Não havia conceito de identidade de usuário em nenhuma camada.

**O que mudei:**
- Criei [db.py](db.py): módulo de banco com `buscar_usuario()` (JOIN entre `sec_users` e `ad_user_cfg`), `verificar_senha()` com detecção automática do esquema de hash (bcrypt, SHA-256, SHA-1, MD5) e `resolver_tipo_consultor()` que mapeia `CONSULTOR` → externo + SAP ID e `LOJA` → interno
- Em [chat_ui.py](chat_ui.py): criei a função `_render_login()` com tela de login centralizada e brandada; adicionei o gate `if "usuario" not in st.session_state` antes de todo o CSS e lógica de chat; incluí bloco de usuário + botão "Sair" no topo da sidebar; migrei a tabela `chats` com a coluna `user_login` para isolar o histórico por usuário; filtrei todos os SELECTs e INSERTs por `user_login`
- Em [main.py](main.py): adicionei o campo opcional `user_login: str = ""` ao `ChatRequest` para uso futuro nas consultas de comissão
- Em [requirements.txt](requirements.txt): adicionei `psycopg2-binary` e `bcrypt`
- `API_BASE` agora lido do `.env` com fallback para `http://127.0.0.1:8000`

---

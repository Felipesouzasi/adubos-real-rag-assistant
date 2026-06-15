# Projeto RAG - Adubos Real

Aplicação de RAG para consulta ao catálogo da Adubos Real, com:

- **Backend** em FastAPI para buscar contexto no índice vetorial e responder com LLM.
- **Frontend** em Streamlit para a interface de chat.

## Como rodar

### 1. Preparar o ambiente

No Windows, abra o terminal na pasta do projeto e execute:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Subir o backend

Em um terminal separado, execute:

```bash
python main.py
```

O backend ficará disponível em `http://127.0.0.1:8000`.

### 3. Subir o frontend

Em outro terminal, com o mesmo ambiente ativo, execute:

```bash
streamlit run chat_ui.py
```

O Streamlit normalmente abrirá em `http://localhost:8501`.

## Ordem correta de execução

1. Instalar as dependências.
2. Iniciar o backend com `python main.py`.
3. Iniciar o frontend com `streamlit run chat_ui.py`.

Se o frontend abrir mas não responder, verifique se o backend está rodando antes.

## Arquivos principais

- `main.py`: API FastAPI e lógica de RAG.
- `chat_ui.py`: interface Streamlit.
- `requirements.txt`: dependências do projeto.

# Análise Técnica — RAG Tião (Adubos Real)

## Resumo Executivo

O MVP está funcional e tem uma UX surpreendentemente bem trabalhada para um primeiro projeto. A estrutura geral (FastAPI + Streamlit + ChromaDB) é sólida. Porém, existem **bugs que vão quebrar em produção**, **problemas sérios de segurança**, **gargalos de qualidade do RAG** e uma **arquitetura que não escala** para o roadmap de comissões/multi-usuário. Aqui está cada ponto.

---

## 1. BUGS CRÍTICOS (quebram em produção)

### `main.py`

**Import inexistente no `requirements.txt`**
```python
# main.py linha 10
from langchain_classic.chains.question_answering import load_qa_chain
```
`langchain_classic` não existe no `requirements.txt`. Isso vai travar na primeira instalação limpa. O correto hoje é `langchain.chains`.

**`max_tokens=300` vai truncar respostas**
```python
llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1, max_tokens=300)
```
300 tokens = ~220 palavras. Uma resposta sobre dosagem de fertilizante com tabela de aplicação vai ser cortada no meio. No mínimo 800-1200 para um assistente agronômico.

**`db_json.persist()` deprecated**
```python
# update_db.py linha 50
db_json.persist()
```
ChromaDB ≥ 0.4.0 removeu esse método — o persist é automático. Isso joga um `AttributeError` na cara se rodar com versão nova.

**`vectordb` aponta para diretório inconsistente**
```python
# main.py linha 71
vectordb = Chroma(persist_directory="text_json_index", ...)
# update_db.py linha 49
db_json = Chroma.from_documents(..., persist_directory="text_json_index")
# Mas o glob mostra: text_index/ (diretório real no repo)
```
Dois diretórios diferentes. O índice que existe (`text_index/`) não é o que o `main.py` carrega (`text_json_index/`). O sistema provavelmente está respondendo sem nenhum documento indexado.

**SQLite com thread-safety falsa**
```python
conn = sqlite3.connect("cache_perguntas.db", check_same_thread=False)
cursor = conn.cursor()
```
`check_same_thread=False` suprime o erro mas não resolve o problema. Com FastAPI async + requests concorrentes, dois usuários ao mesmo tempo podem corromper o banco.

---

## 2. QUALIDADE DO RAG (onde o dinheiro vai embora)

**Cache ignora contexto da conversa**

O cache usa a pergunta bruta como chave:
```python
pergunta_limpa = request.question.strip().lower()
cursor.execute("SELECT resposta FROM faq_cache WHERE pergunta = ?", (pergunta_limpa,))
```
Se João perguntou "Quais produtos para milho?" e a resposta ficou cacheada, quando Maria perguntar a mesma coisa num chat diferente, ela recebe a mesma resposta — sem considerar o histórico dela. Tudo bem para FAQs. Péssimo quando o histórico importa.

**Cache exige match exato — na prática não serve**

"Produtos para milho?" e "produto pra milho?" não batem. O cache raramente vai atingir. É uma falsa economia.

**`chunk_overlap=20` é praticamente zero**

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
```
Com chunks de 1000 chars, um overlap de 20 é 2% — frases que atravessam a fronteira do chunk ficam partidas e o retrieval perde contexto. O padrão da indústria é 10-20% → 100-200 chars de overlap.

**Apenas um documento indexado**

```python
# update_db.py
json_link = "catalogo_consolidado.json"
```
O sistema tem 6+ arquivos JSON em `json_folders/` (cafezal, citros, folhosas, hortifruti, enraizamento, bula Zapp), mas o índice só processa o catálogo consolidado. A bula do Zapp QI (produto específico), os folders de citros e café — nada disso está no RAG.

**Modelo fraco para domínio técnico**

`gpt-3.5-turbo` tem conhecimento agronômico limitado e frequentemente alucina em domínios específicos. Para um assistente que vai dar recomendações de dosagem de fertilizante a um produtor rural, um erro técnico é sério.

---

## 3. SEGURANÇA (crítico para o roadmap de comissões)

**Sem autenticação alguma**

A API FastAPI em `http://127.0.0.1:8000` está totalmente aberta. O frontend Streamlit também. Qualquer pessoa na rede local pode fazer requisições. Quando o sistema tiver dados de comissões de consultores, isso é inaceitável.

**Sem CORS configurado**

Nenhum middleware de CORS no FastAPI. Requisições de origens diferentes não são controladas.

**Sem isolamento de dados por usuário**

```python
# chat_ui.py — todos os chats são compartilhados
c.execute("SELECT session_id, titulo, fixado FROM chats ORDER BY fixado DESC, data_criacao DESC")
```
Não existe conceito de `user_id`. Consultor A vê os chats do Consultor B. Quando vier a funcionalidade de comissões, Consultor A poderá ver os dados do B.

---

## 4. ARQUITETURA (não escala para o roadmap)

**Dois SQLites desconexos**

`historico_chats.db` (frontend) e `cache_perguntas.db` (backend) são bancos separados sem nenhuma coordenação. O backend não sabe nada sobre a sessão do usuário. Para futuramente isolar dados por consultor, isso vai exigir refatoração completa.

**Sem streaming de resposta**

A resposta só aparece depois de 100% gerada. Com respostas maiores e modelos melhores, o usuário espera 10-20s olhando para "Pensando...". O LangChain tem suporte nativo a streaming; o Streamlit também suporta via `st.write_stream`.

**Histórico relido do banco a cada interação**

```python
# chat_ui.py — executado a cada rerun do Streamlit
st.session_state.messages = []
c.execute("SELECT role, content FROM mensagens WHERE session_id = ?...")
for row in c.fetchall():
    st.session_state.messages.append(...)
```
Qualquer interação com a UI (clicar num chip, abrir popover) relê todas as mensagens do banco. Conversa com 50 trocas = 50 leituras desnecessárias por clique.

**CSS baseado em classes internas do Streamlit**

```python
# chat_ui.py linha 187
'.st-emotion-cache-1215ydw { display: none !important; }'
```
Classes como `.st-emotion-cache-*` são geradas automaticamente pelo Streamlit e mudam entre versões. Uma atualização de `pip install streamlit --upgrade` vai silenciosamente quebrar o layout.

**Frontend hardcoded na URL da API**

```python
api_url = "http://127.0.0.1:8000/chat"
```
Sem variável de ambiente. Se mais de um computador precisar usar, tem que editar código.

**Sem logging estruturado**

Apenas `print()` espalhados. Em produção não há como monitorar erros, latência, ou quais perguntas estão falhando.

**`.venv` versionado no repositório**

A pasta `.venv` (485MB+ tipicamente) está sendo rastreada pelo git. Deve estar no `.gitignore`.

**`requirements.txt` sem versões**

```
fastapi
langchain
langchain-openai
```
Sem versões fixadas, `pip install` em 6 meses pode instalar versões incompatíveis. LangChain em particular quebra compatibilidade entre minor versions com frequência.

**`langchain_classic` não está no requirements.txt**

`main.py` importa `from langchain_classic.chains.question_answering import load_qa_chain` mas `langchain_classic` não existe como pacote PyPI.

---

## 5. O QUE ESTÁ BEM (para ser justo)

- UX do chat está surpreendentemente polida: chips dinâmicos, histórico com pin/rename/delete, popover com menu, animações
- A ideia do cache SQLite para FAQs repetidas é correta, só a implementação precisa melhorar
- MMR (Maximal Marginal Relevance) no retriever é a escolha certa para diversidade de contexto
- Separação backend/frontend via API é o padrão correto — facilita evoluir os dois independentemente
- O `convert_to_json.py` com `pymupdf4llm` é excelente para extrair tabelas de PDF com fidelidade

---

## Plano de Ataque (prioridades sugeridas)

| Prioridade | Item | Impacto |
|---|---|---|
| 🔴 P0 | Corrigir import `langchain_classic` e `persist()` deprecated | Sistema quebrado na próxima instalação |
| 🔴 P0 | Corrigir diretório do vectordb (`text_index` vs `text_json_index`) | RAG possivelmente não está buscando nada |
| 🔴 P0 | Aumentar `max_tokens` para mínimo 1000 | Respostas truncadas |
| 🟠 P1 | Indexar todos os JSONs (não só o catálogo) | Qualidade do RAG |
| 🟠 P1 | Aumentar `chunk_overlap` para 150-200 | Qualidade do RAG |
| 🟠 P1 | Adicionar autenticação básica | Segurança para multi-usuário |
| 🟠 P1 | Streaming de respostas | UX — feedback em tempo real |
| 🟡 P2 | Thread-safe SQLite (usar `aiosqlite` ou conexões por request) | Estabilidade com múltiplos usuários |
| 🟡 P2 | Adicionar `user_id` às tabelas do banco | Base para dados isolados por consultor |
| 🟡 P2 | Variáveis de ambiente (`.env`) para URL da API e configs | Portabilidade |
| 🟡 P2 | Pinnar versões no `requirements.txt` | Reprodutibilidade |
| 🟡 P2 | `.gitignore` para `.venv` e arquivos `.db` | Higiene do repositório |
| 🟢 P3 | Migrar para modelo melhor (gpt-4o-mini ou Claude Haiku) | Qualidade das respostas |
| 🟢 P3 | Cache semântico (embedding similarity) em vez de match exato | Taxa de hit do cache |
| 🟢 P3 | Logging estruturado | Monitoramento em produção |

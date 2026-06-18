import os
import sqlite3
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se ele existir
load_dotenv()

# 1. Configuração
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Chave OpenAI_API_KEY nao encontrada! Configure-a no arquivo .env")

os.environ["OPENAI_API_KEY"] = openai_key



# 1.5. Configuração do SQLite (Cache Local para economia de tokens)
conn = sqlite3.connect("cache_perguntas.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq_cache (
        pergunta TEXT PRIMARY KEY,
        resposta TEXT
    )
""")
conn.commit()

# 2. Setup do App
app = FastAPI(title="RAG API - Safra Real", description="API para consultas no catálogo da Safra Real com Histórico e Cache")

# 3. Modelos de Dados (Schemas) - Atualizados para receber histórico
class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = [] # Recebe as regras do frontend

class ChatResponse(BaseModel):
    answer: str
    cached: bool = False # Sinaliza se pegou do SQLite ou pagou a API

# 4. Inicialização de Recursos
embeddings_model = OpenAIEmbeddings()
llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1, max_tokens=1000)

# Prompt Customizado: Personalidade e Memória
template = """Você é o Agrônomo Virtual da Adubos Real SA. 
Seja extremamente simpático, didático e ajude o produtor a ter uma lavoura saudável. Use emojis.
Se o usuário perguntar algo de uma conversa passada, verifique o histórico.
Se a resposta para a pergunta não estiver no contexto do catálogo, diga educadamente que não possui essa informação. Nunca chute informações técnicas.

Histórico até o momento:
{chat_history}

Contexto encontrado pelo RAG:
{context}

Pergunta Final do Usuário: {question}
Sua Resposta como Agrônomo da Adubos Real:"""

PROMPT = PromptTemplate(template=template, input_variables=["chat_history", "context", "question"])

# Carrega o banco de vetores gerado previamente
vectordb = Chroma(persist_directory="text_index", embedding_function=embeddings_model)

# Retriever otimizado usando MMR (Maximal Marginal Relevance) para mais diversidade de fontes
retriever = vectordb.as_retriever(
    search_type="mmr", 
    search_kwargs={"k": 4, "fetch_k": 10} # Pega 10 chunks, e escolhe os 4 mais diversos
)
chain = load_qa_chain(llm_model, chain_type="stuff", prompt=PROMPT)

# 5. Rota/Endpoint principal
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    pergunta_limpa = request.question.strip().lower()
    
    # 5.1. BATE NO CACHE DO BD PRIMEIRO (ECONOMIZA SE DEU MATCH)
    cursor.execute("SELECT resposta FROM faq_cache WHERE pergunta = ?", (pergunta_limpa,))
    resultado_cache = cursor.fetchone()
    
    if resultado_cache:
        print(f"Resposta em cache recuperada! Nenhuma requisição gasta na OpenAI.")
        return ChatResponse(answer=resultado_cache[0], cached=True)

    try:
        # Se não tá no cache, formata o histórico para passar ao LLM
        historico_formatado = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in request.history])
        if not historico_formatado:
            historico_formatado = "Nenhuma conversa anterior ainda."

        # Busca documentos relevantes usando MMR
        contexts = retriever.invoke(request.question)
        
        # Gera a resposta via OpenAi
        resultado = chain.invoke({
            "input_documents": contexts, 
            "question": request.question,
            "chat_history": historico_formatado
        })
        
        resposta_final = resultado['output_text']
        
        # Salva o novo conhecimento no Banco de Dados para uso futuro! 💸
        cursor.execute("INSERT OR REPLACE INTO faq_cache (pergunta, resposta) VALUES (?, ?)", (pergunta_limpa, resposta_final))
        conn.commit()

        return ChatResponse(answer=resposta_final, cached=False)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar: {str(e)}")

# 6. Inicialização do Servidor (Para rodar com 'python main.py')
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


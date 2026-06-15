import streamlit as st
import requests
import sqlite3
import uuid
import random
from datetime import datetime

st.set_page_config(page_title="Adubos Real - Assistente", page_icon="🌱", layout="wide")

st.markdown("""
<style>
    :root {
        --sidebar-offset: 150px;
    }

    body:has([data-testid="stSidebar"][aria-expanded="false"]) {
        --sidebar-offset: 0px;
    }

    footer {visibility: hidden;}
    .stApp > header { background-color: transparent !important; }
    .stApp > header .st-emotion-cache-15vw7j6 { display: none !important; }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 24rem !important; /* Muito mais espaço para a "requisição" rolar sem tocar nos botões fixos */
        max-width: 900px !important;
        margin: 0 auto;
    }

    body:has(#empty-state) .block-container {
        padding-bottom: 6rem !important; /* Evita scroll inicial quando o chat está vazio */
    }

    body:has(#chat-has-messages) .block-container,
    div[data-testid="stAppViewContainer"]:has(#chat-has-messages) .block-container,
    section.main:has(#chat-has-messages) .block-container {
        padding-top: 4rem !important; /* Afasta o primeiro bloco da área do topo */
        padding-bottom: 14rem !important; /* Evita espaço gigante entre mensagens */
    }
    
    div.stApp section.main {
        position: relative;
    }

    /* CSS ABSOLUTO E À PROVA DE FALHAS PARA OS CHIPS - Isolados num container! */
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) {
        position: fixed !important;
        bottom: 8px !important; /* Fixado abaixo do input */
        left: 50% !important;
        transform: translateX(calc(-50% + var(--sidebar-offset))) !important; /* Compensa a largura da sidebar para centralizar na área preta */
        width: 100% !important; 
        max-width: 730px !important; 
        z-index: 100000 !important;
        background-color: transparent !important;
        padding-bottom: 0;
        display: flex !important;
        justify-content: center !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) > div.element-container:first-child {
        display: none !important; /* Esconde a âncora pra não roubar espaço */
    }

    /* Formatação das colunas dentro do Container */
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) div[data-testid="stHorizontalBlock"] {
        width: 100% !important;
        gap: 10px !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        flex-wrap: wrap !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) div[data-testid="column"] {
        width: fit-content !important;
        flex: none !important;
        min-width: unset !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) .stButton>button {
        border-radius: 20px; 
        padding: 0.4rem 1.2rem !important; 
        font-size: 14px;
        width: auto !important; 
        transition: all 0.2s ease-in-out;
        border: 1px solid rgba(128, 128, 128, 0.4);
        background-color: var(--background-color, #0e1117) !important; /* Fundo sólido para ocultar sombra do chat input subindo */
    }
    
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) .stButton>button p,
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) .stButton>button div {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) .stButton>button:hover {
        transform: scale(1.05); 
        border-color: #28a745 !important;
    }

    [data-testid="stSidebar"] div[data-testid="column"] {
        gap: 0 !important; /* Remove gaps extras nas colunas do historico para o layout novo */
    }
    
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
        position: relative !important;
        align-items: center !important;
        margin-bottom: 2px !important;
    }

    [data-testid="stSidebar"] .stButton>button {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
        justify-content: flex-start;
        padding: 4px 30px 4px 8px !important; /* Adiciona padding na direita (30px) pra nao sobrepor com os 3 pontinhos */
        margin-bottom: 0 !important;
        border: none !important;
        background-color: transparent !important;
        font-size: 13px !important;
        min-height: 32px !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover,
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-radius: 6px !important;
    }

    /* Coluna 2 flutuante para os 3 pontinhos */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        position: absolute !important;
        right: 0 !important;
        top: 0 !important;
        bottom: 0 !important;
        width: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
        z-index: 10;
        padding-left: 20px !important;
        background: linear-gradient(90deg, transparent 0%, var(--background-color, #262730) 30%, var(--background-color, #262730) 100%) !important;
        border-radius: 0 6px 6px 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover > div:nth-child(2) {
        opacity: 1;
        background: linear-gradient(90deg, transparent 0%, rgba(200, 200, 200, 0.1) 40%, rgba(200, 200, 200, 0.1) 100%) !important; /* Ajusta fundo pra mesclar com o hover do botão pai */
    }
    
    /* Popover Sidebar (Três pontinhos) - Sem borda e sem setinha */
    [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"] {
        padding: 0 !important;
        width: 28px !important;
        height: 28px !important;
        min-height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        background-color: transparent !important;
        opacity: 1 !important; 
        transition: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"]:hover {
        background-color: rgba(128, 128, 128, 0.2) !important;
        border-radius: 6px !important;
    }

    /* ESCONDER A SETA (SVG) de várias das versões possíveis do Streamlit */
    [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"] svg,
    [data-testid="stSidebar"] [data-testid="stPopover"] svg,
    [data-testid="stSidebar"] .st-emotion-cache-1215ydw {
        display: none !important;
    }

    /* Estilo Profissional para o menu que abre (Popover Body) IDÊNTICO AO CLAUDE */
    div[data-testid="stPopoverBody"] {
        padding: 6px !important;
        background-color: #2b2b30 !important; /* Cor mais cinza escuro sofisticado */
        border-radius: 12px !important; /* Bordas mais suaves */
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important; /* Sombreamento flutuante */
    }
    div[data-testid="stPopoverBody"] .stButton>button {
        width: 100% !important;
        justify-content: flex-start !important;
        height: auto !important;
        padding: 8px 12px !important;
        border: none !important;
        background-color: transparent !important;
        font-weight: normal !important;
        font-size: 14px !important;
        color: #e5e5e5 !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stPopoverBody"] .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stMarkdownContainer"] p {
        font-size: 14px !important;
        margin: 0 !important;
    }
    /* Estilizar EXATAMENTE o ÚLTIMO botão (Apagar) dentro do Popover como vermelho */
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 4px;
        padding-top: 4px;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type .stButton>button p {
        color: #ff6b6b !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type .stButton>button span {
        color: #ff6b6b !important; /* Aplica cor ao respectivo icone */
    }

    /* Cores Adubos Real (Verde) para o Botão Primário ("Salvar") e Input em Foco */
    button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #28a745 !important;
    }
    button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
        color: white !important;
    }
    
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    .stChatInputContainer:focus-within,
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 1px #28a745 !important;
        outline: none !important;
    }

    /* CSS MAGIC 1: Mover todo o Container do Input e travar no lugar pra não sobrepor chat. */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 135px !important; 
        left: 50% !important;
        transform: translateX(calc(-50% + var(--sidebar-offset))) !important;
        width: 100% !important;
        max-width: 900px !important;
        z-index: 200;
        background-color: var(--background-color, #0e1117) !important;
        padding-bottom: 20px !important;
        padding-top: 5px !important;
    }
    
    [data-testid="stChatInput"] {
        background-color: transparent !important;
    }

    /* Animação para os novos chips aparecendo */
    @keyframes fade-in-scale {
        0% { opacity: 0; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1); }
    }
    div[data-testid="stHorizontalBlock"] .stButton>button {
        animation: fade-in-scale 0.4s ease-out forwards;
    }

    ::-webkit-scrollbar {
        width: 6px;
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #ccc; 
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("historico_chats.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chats (session_id TEXT PRIMARY KEY, titulo TEXT, data_criacao TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS mensagens (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)")

# Garantir que a coluna 'fixado' exista numa atualização de layout
try:
    c.execute("ALTER TABLE chats ADD COLUMN fixado INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

conn.commit()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_title = "Novo Chat"

if "scroll_mode" not in st.session_state:
    st.session_state.scroll_mode = None

if "popover_nonce" not in st.session_state:
    st.session_state.popover_nonce = 0

def close_sidebar_popover():
    st.session_state.popover_nonce += 1

FAQ_POOL = [
    ("🌱 Catálogo", "Qual é o catálogo completo de produtos da Adubos Real?"),
    ("🥬 Folhosas", "Quais são os fertilizantes ideais para folhosas?"),
    ("🍅 Hortifruti", "Quais as soluções indicadas para tomate e hortifruti?"),
    ("🐄 Pastagem", "Quais as opções de produtos recomendadas para Pastagem?"),
    ("🐛 Controle", "Vocês possuem recomendações de manejo focado na defesa das plantas?"),
    ("🌽 Milho", "Meu foco é na cultura do milho. Quais os produtos e recomendações?"),
    ("☕  Cafezais", "Gostaria de saber as dicas de manejo para lavouras de café."),
    ("🍊 Citros", "O que vocês recomendam para o manejo de Citros?"),
    ("💧 Uso Foliar", "Como funciona e como devo usar a aplicação foliar dos produtos?"),
    ("🔬 Solo", "Como a Adubos Real orienta sobre adubação baseada em análise de solo?")
]

if "active_faqs" not in st.session_state:
    st.session_state.active_faqs = FAQ_POOL[:5]  # Pega os 5 primeiros inicialmente
    st.session_state.used_faqs = set(range(5))   # Marca os índices usados

carregar_sessao = None

@st.dialog("Mudar nome do chat")
def modal_renomear(sid, titulo_atual):
    novo_nome = st.text_input("Nome", value=titulo_atual, label_visibility="collapsed")
    c1, c2 = st.columns([0.5, 0.5])
    if c1.button("Cancelar", use_container_width=True):
        st.session_state["rename_mode"] = None
        st.rerun()
        
    if c2.button("Salvar", type="primary", use_container_width=True):
        c.execute("UPDATE chats SET titulo = ? WHERE session_id = ?", (novo_nome, sid))
        conn.commit()
        st.session_state["rename_mode"] = None
        st.rerun()

with st.sidebar:
    if st.button("➕ Novo Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_title = "Novo Chat"        # Reseta os chips dinâmicos
        st.session_state.active_faqs = FAQ_POOL[:5]
        st.session_state.used_faqs = set(range(5))        
        st.rerun()
        
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px; border: 0; border-top: 1px solid rgba(128,128,128,0.2);'>", unsafe_allow_html=True) 
    
    st.markdown("### Histórico") 
    
    c.execute("SELECT session_id, titulo, fixado FROM chats ORDER BY fixado DESC, data_criacao DESC")
    for sid, titulo, fixado in c.fetchall():
        if st.session_state.get("rename_mode") == sid:
            modal_renomear(sid, titulo)

        col1, col2 = st.columns([0.85, 0.15], gap="small")
        with col1:
            icon_fixo = "📌 " if fixado else ""
            if st.button(f"{icon_fixo}{titulo}", key=f"chat_{sid}", use_container_width=True):
                carregar_sessao = sid
        with col2:
            with st.popover("⋮", use_container_width=True, key=f"menu_{sid}_{st.session_state.popover_nonce}"):
                if st.button("Compartilhar", icon=":material/share:", key=f"sh_{sid}", use_container_width=True):
                    st.toast(f"'{titulo}' copiado para a área de transferência!")
                    close_sidebar_popover()
                    st.rerun()
                
                texto_fixar = "Desfixar" if fixado else "Fixar"
                icone_fixar = ":material/keep:" if fixado else ":material/push_pin:"
                if st.button(texto_fixar, icon=icone_fixar, key=f"pi_{sid}", use_container_width=True):
                    close_sidebar_popover()
                    c.execute("UPDATE chats SET fixado = ? WHERE session_id = ?", (int(not fixado), sid))
                    conn.commit()
                    st.rerun()
                    
                if st.button("Renomear", icon=":material/edit:", key=f"rn_{sid}", use_container_width=True):
                    close_sidebar_popover()
                    st.session_state["rename_mode"] = sid
                    st.rerun()
                    
                if st.button("Apagar", icon=":material/delete:", key=f"dl_{sid}", use_container_width=True):
                    close_sidebar_popover()
                    c.execute("DELETE FROM chats WHERE session_id=?", (sid,))
                    c.execute("DELETE FROM mensagens WHERE session_id=?", (sid,))
                    conn.commit()
                    if st.session_state.session_id == sid:
                        st.session_state.session_id = str(uuid.uuid4())
                        st.session_state.chat_title = "Novo Chat"
                        st.session_state.messages = []
                    st.rerun()

if carregar_sessao:
    st.session_state.session_id = carregar_sessao
    c.execute("SELECT titulo FROM chats WHERE session_id = ?", (carregar_sessao,))
    st.session_state.chat_title = c.fetchone()[0]

st.session_state.messages = []
c.execute("SELECT role, content FROM mensagens WHERE session_id = ? ORDER BY id ASC", (st.session_state.session_id,))
for row in c.fetchall():
    st.session_state.messages.append({"role": row[0], "content": row[1]})

# --- PÁGINA INICIAL ---
if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div id='empty-state'></div>
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; margin-top: 10rem;'> <!-- AQUI: Aumente esse valor para abaixar mais -->
            <h1 style='color: var(--text-color); font-size: 2.5rem; font-weight: 600; margin-bottom: 0;'>Olá, como posso ajudar?</h1>
            <p style='color: #86868b; margin-top: 0.1rem; margin-bottom: 2rem;'>Tião | Assistente Adubos Real 🌱</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
else:
    st.markdown("<div id='chat-has-messages'></div>", unsafe_allow_html=True)

if len(st.session_state.messages) > 0:
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if len(st.session_state.messages) > 0:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown("<div id='scroll-anchor'></div>", unsafe_allow_html=True)

# Lógica de atualização dos Chips Dinâmicos
def replace_chip(chip_index, query):
    st.session_state.faq_query = query
    # Buscar tópicos disponíveis não usados
    available = [i for i in range(len(FAQ_POOL)) if i not in st.session_state.used_faqs]
    
    # Se todos já foram usados, recicla do zero mas mantém os que estão ativos agora intactos
    if not available:
        ativos_atuais = [FAQ_POOL.index(f) for f in st.session_state.active_faqs]
        st.session_state.used_faqs = set(ativos_atuais)
        available = [i for i in range(len(FAQ_POOL)) if i not in st.session_state.used_faqs]
        
    if available:
        new_idx = random.choice(available)
        st.session_state.used_faqs.add(new_idx)
        st.session_state.active_faqs[chip_index] = FAQ_POOL[new_idx]

# MENU DE CHIPS (Agora sempre visível)
with st.container():
    st.markdown("<span id='chips-anchor'></span>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for i in range(5):
        with cols[i]:
            label, query = st.session_state.active_faqs[i]
            # Chave única baseada no texto do botão garante o re-render e a animação do CSS
            if st.button(label, key=f"faq_btn_{label}"):
                replace_chip(i, query)
                st.rerun()

prompt = st.chat_input("Pergunte alguma coisa ao Tião...")

if getattr(st.session_state, "faq_query", None):
    prompt = st.session_state.faq_query
    st.session_state.faq_query = None

if prompt:
    st.session_state.scroll_mode = "bottom"
    if len(st.session_state.messages) == 0:
        novo_titulo = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.session_state.chat_title = novo_titulo
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO chats (session_id, titulo, data_criacao) VALUES (?, ?, ?)", 
                  (st.session_state.session_id, novo_titulo, data_agora))
        
    c.execute("INSERT INTO mensagens (session_id, role, content) VALUES (?, ?, ?)", 
              (st.session_state.session_id, "user", prompt))
    conn.commit()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Pensando...")
        
        try:
            api_url = "http://127.0.0.1:8000/chat"
            historico_envio = st.session_state.messages[:-1][-4:] 
            
            payload = {"question": prompt, "history": historico_envio}
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                dados = response.json()
                answer = dados.get("answer", "Desculpe, a IA retornou erro!")
                is_cached = dados.get("cached", False)
                
                if is_cached:
                    answer += "\n\n*(⚡ Resposta via Cache SQLite)*"

                message_placeholder.markdown(answer)
                
                c.execute("INSERT INTO mensagens (session_id, role, content) VALUES (?, ?, ?)", 
                          (st.session_state.session_id, "assistant", answer))
                conn.commit()
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                if len(st.session_state.messages) == 2:
                    st.rerun()

            else:
                message_placeholder.error(f"⚠️ Erro ao consultar a API. Código: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            message_placeholder.error("🚨 Não foi possível conectar à API. Você rodou seu `main.py`?")

scroll_mode = st.session_state.get("scroll_mode")
if scroll_mode == "bottom":
    scroll_behavior = "smooth"
    script_template = """
        <script>
            const root = window.parent && window.parent.document ? window.parent.document : document;
            const anchor = root.getElementById("scroll-anchor");
            if ("scrollRestoration" in history) {{
                history.scrollRestoration = "manual";
            }}

            const candidates = [
                root.querySelector("section.main"),
                root.querySelector("div[data-testid='stAppViewContainer']"),
                root.querySelector("div[data-testid='stApp']"),
                root.scrollingElement,
                root.documentElement,
                root.body,
            ].filter(Boolean);

            const scrollContainers = Array.from(new Set(candidates));

            const scrollToTop = () => {{
                scrollContainers.forEach((container) => {{
                    container.scrollTop = 0;
                    if (container.scrollTo) {{
                        container.scrollTo({{ top: 0, behavior: "{scroll_behavior}" }});
                    }}
                }});
                window.scrollTo({{ top: 0, behavior: "{scroll_behavior}" }});
                root.documentElement.scrollTop = 0;
                root.body.scrollTop = 0;
            }};

            const scrollToBottom = () => {{
                const messages = root.querySelectorAll("[data-testid='stChatMessage']");
                const lastMessage = messages.length ? messages[messages.length - 1] : null;
                if (lastMessage) {{
                    lastMessage.scrollIntoView({{ behavior: "{scroll_behavior}", block: "end" }});
                }} else if (anchor) {{
                    anchor.scrollIntoView({{ behavior: "{scroll_behavior}", block: "end" }});
                }}
                scrollContainers.forEach((container) => {{
                    container.scrollTop = container.scrollHeight;
                }});
                window.scrollTo({{ top: root.documentElement.scrollHeight, behavior: "{scroll_behavior}" }});
            }};

            scrollToBottom();
            requestAnimationFrame(scrollToBottom);
            setTimeout(scrollToBottom, 100);

            const obsTarget = root.body || root.documentElement;
            if (obsTarget && "MutationObserver" in window) {{
                const observer = new MutationObserver(() => scrollToBottom());
                observer.observe(obsTarget, {{ childList: true, subtree: true }});
                setTimeout(() => observer.disconnect(), 2500);
            }}
            const bottomInterval = setInterval(scrollToBottom, 120);
            setTimeout(() => clearInterval(bottomInterval), 2500);
        </script>
    """
    st.markdown(
        script_template.format(
            scroll_behavior=scroll_behavior,
            scroll_mode=scroll_mode,
        ),
        unsafe_allow_html=True,
    )
    st.session_state.scroll_mode = None
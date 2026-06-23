import os
import streamlit as st
import requests
import sqlite3
import uuid
import random
from datetime import datetime
import db


import base64

logo_base64 = ""
try:
    with open("logo.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except Exception:
    pass

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def _render_login():
    bg_base64 = ""
    try:
        with open("bg_login.png", "rb") as f:
            bg_base64 = base64.b64encode(f.read()).decode()
    except Exception:
        pass

    st.markdown(f"""
    <style>
        /* Esconde sidebar na tela de login */
        [data-testid="stSidebar"] {{ display: none !important; }}

        /* Esconde o cabeçalho do Streamlit (Deploy, menu de 3 pontos, etc.) */
        header, [data-testid="stHeader"] {{
            display: none !important;
        }}
        
        /* Fundo com a imagem do lado direito (contain para manter tamanho original sem crop/zoom) */
        .stApp {{
            background-color: #000000 !important;
            background-image: url('data:image/png;base64,{bg_base64}') !important;
            background-repeat: no-repeat !important;
            background-position: right center !important;
            background-size: contain !important;
            height: 100vh !important;
            overflow: hidden !important;
        }}

        /* Overlay de fade para preto no lado esquerdo */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to right, #000000 0%, #000000 35%, rgba(0,0,0,0.7) 48%, rgba(0,0,0,0) 65%) !important;
            z-index: 1;
            pointer-events: none;
        }}
        
        /* Ajusta o container principal para alinhar à esquerda */
        .block-container {{ 
            max-width: 100% !important; 
            width: 100% !important; 
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            position: relative !important;
            z-index: 2 !important;
        }}

        /* Garante que o vertical block preencha a altura e alinhe o conteúdo */
        div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
            max-width: 480px !important;
            margin-left: 8% !important;
            padding: 2rem !important;
        }}
        
        /* Formulário limpo sem bordas e sombras (conforme mockup) */
        [data-testid="stForm"] {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
            width: 100% !important;
        }}
        
        /* Estilização das inputs */
        div[data-baseweb="input"] {{
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            height: 50px !important;
        }}

        div[data-baseweb="input"] > div, 
        div[data-baseweb="input"] button,
        div[data-baseweb="input"] button:hover,
        div[data-baseweb="input"] button:active {{
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
        }}
        
        div[data-baseweb="input"]:focus-within {{
            border-color: #28a745 !important; /* Borda verde corporativa ao focar */
            box-shadow: 0 0 0 1px #28a745 !important;
        }}

        div[data-baseweb="input"] input {{
            color: #f0f6fc !important;
            font-size: 16px !important;
        }}
        
        /* Esconde a dica "Press Enter to submit form" */
        [data-testid="InputInstructions"] {{
            display: none !important;
        }}
        
        /* Estilização dos labels das inputs */
        label[data-testid="stWidgetLabel"] p {{
            color: #8b949e !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            margin-bottom: 8px !important;
        }}
        
        /* Botão Entrar com Degradê Verde Corporativo (Adubos Real) */
        button[kind="primary"], 
        button[data-testid="baseButton-primary"],
        div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(90deg, #2eb85c 0%, #1b8a3e 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 25px !important; /* Bem arredondado conforme mockup */
            font-size: 16px !important;
            font-weight: 600 !important;
            height: 50px !important;
            box-shadow: 0 4px 20px rgba(46, 184, 92, 0.3) !important;
            transition: all 0.25s ease !important;
            margin-top: 1.5rem !important;
        }}
        
        button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover,
        div[data-testid="stFormSubmitButton"] button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(46, 184, 92, 0.5) !important;
            filter: brightness(1.1) !important;
            background: linear-gradient(90deg, #32c463 0%, #1f9c46 100%) !important;
        }}
        
        button[kind="primary"]:active,
        button[data-testid="baseButton-primary"]:active,
        div[data-testid="stFormSubmitButton"] button:active {{
            transform: translateY(1px) !important;
        }}

        /* Alerta de erro estilizado */
        [data-testid="stNotification"] {{
            background-color: rgba(248, 81, 73, 0.15) !important;
            border: 1px solid rgba(248, 81, 73, 0.3) !important;
            border-radius: 12px !important;
            color: #ff7b72 !important;
        }}
        
        /* Ajuste do botão de submissão do Streamlit para preencher largura total (evita afetar o olho da senha) */
        [data-testid="stForm"] button[type="submit"],
        div[data-testid="stFormSubmitButton"] button {{
            width: 100% !important;
        }}

        /* Container para a logo no lado direito da tela (centralizada na imagem) */
        .right-logo-container {{
            position: fixed !important;
            top: 50% !important;
            left: 70% !important;
            transform: translate(-50%, -50%) !important;
            z-index: 2 !important;
            pointer-events: none !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        
        .right-logo {{
            max-width: 320px !important;
            width: 100% !important;
            height: auto !important;
            filter: drop-shadow(0px 4px 15px rgba(0, 0, 0, 0.5)) !important;
        }}

        /* Responsividade para telas menores (celulares) */
        @media (max-width: 768px) {{
            .stApp {{
                background-image: none !important;
                background-color: #000000 !important;
            }}
            .right-logo-container {{
                display: none !important;
            }}
            .block-container {{
                justify-content: center !important;
            }}
            div[data-testid="stVerticalBlock"] {{
                margin-left: 0 !important;
                margin: 0 auto !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # Título estilizado de acordo com o mockup e logo flutuante no lado direito
    st.markdown(f"""
    <div style='text-align: left; margin-bottom: 2.5rem; animation: fadeIn 0.6s ease-out;'>
        <h1 style='margin: 0; font-size: 3rem; font-weight: 700; color: #ffffff; letter-spacing: -1px; line-height: 1.1;'>
            Inteligência Real<span style='color: #2eb85c;'>.</span>
        </h1>
    </div>
    <div class="right-logo-container">
        <img class="right-logo" src="data:image/png;base64,{logo_base64}" />
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        login = st.text_input("Login ou E-mail", placeholder="@adubosreal.com.br")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)


    if submitted:
        if not login.strip() or not senha:
            st.error("Preencha login e senha.")
            return
        try:
            usuario = db.buscar_usuario(login.strip().lower())
            if usuario and db.verificar_senha(senha, usuario["pswd"]):
                tipo, id_sap = db.resolver_tipo_consultor(usuario)
                st.session_state.usuario = {
                    "login":           usuario["login"],
                    "name":            usuario.get("name") or usuario["login"],
                    "email":           usuario.get("email", ""),
                    "picture":         usuario.get("picture"),
                    "role":            usuario.get("role"),
                    "setor":           usuario.get("setor"),
                    "filial":          usuario.get("filial"),
                    "tipo_consultor":  tipo,
                    "id_sap":          id_sap,
                }
                st.rerun()
            else:
                st.error("Login ou senha incorretos.")
        except Exception as e:
            st.error(f"Não foi possível conectar ao banco de dados. Verifique as configurações do .env. Erro: {e}")
            st.exception(e)
            print(f"[login] erro: {e}")






st.set_page_config(page_title="Adubos Real - Assistente", page_icon="🌱", layout="wide")

if "usuario" not in st.session_state:
    _render_login()
    st.stop()

# ----------------- CORES DINÂMICAS DO TEMA -----------------
is_dark = st.session_state.get("theme", "dark") == "dark"
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    :root {{
        --background-color: {"#0b0d10" if is_dark else "#ffffff"} !important;
        --sidebar-bg: {"#0d1117" if is_dark else "#f0f2f6"} !important;
        --text-color: {"#f0f6fc" if is_dark else "#31333F"} !important;
        --muted-color: {"#8b949e" if is_dark else "#57606a"} !important;
        --input-bg: {"#161b22" if is_dark else "#ffffff"} !important;
        --input-border: {"#30363d" if is_dark else "#e6eaf1"} !important;
        --card-bg: {"rgba(255, 255, 255, 0.03)" if is_dark else "rgba(0, 0, 0, 0.02)"} !important;
        --card-border: {"rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.06)"} !important;
        --user-bubble-bg: {"#1f2937" if is_dark else "#e8f0fe"} !important;
        --user-bubble-border: {"rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.05)"} !important;
        --assistant-bubble-bg: {"#161b22" if is_dark else "#ffffff"} !important;
        --assistant-bubble-border: {"rgba(46, 184, 92, 0.15)" if is_dark else "rgba(46, 184, 92, 0.25)"} !important;
        --sidebar-border: {"rgba(128,128,128,0.2)" if is_dark else "rgba(0,0,0,0.1)"} !important;
        --sidebar-text: {"#c9d1d9" if is_dark else "#24292f"} !important;
        --sidebar-offset: 150px;
    }}

    body:has([data-testid="stSidebar"][aria-expanded="false"]) {{
        --sidebar-offset: 0px;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Estilos Globais */
    .stApp {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    footer {visibility: hidden;}
    header, [data-testid="stHeader"] { background-color: transparent !important; }
    header [data-testid="stHeaderActionElements"] { display: none !important; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 24rem !important;
        max-width: 900px !important;
        margin: 0 auto;
    }

    body:has(#empty-state) .block-container {
        padding-bottom: 6rem !important;
    }

    body:has(#chat-has-messages) .block-container,
    div[data-testid="stAppViewContainer"]:has(#chat-has-messages) .block-container,
    section.main:has(#chat-has-messages) .block-container {
        padding-top: 2rem !important;
        padding-bottom: 14rem !important;
    }
    
    div.stApp section.main {
        position: relative;
        background-color: var(--background-color) !important;
    }

    /* CSS ABSOLUTO E À PROVA DE FALHAS PARA OS CHIPS - Isolados num container! */
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) {
        position: fixed !important;
        bottom: 8px !important;
        left: 50% !important;
        transform: translateX(calc(-50% + var(--sidebar-offset))) !important;
        width: 100% !important; 
        max-width: 730px !important; 
        z-index: 100000 !important;
        background-color: transparent !important;
        padding-bottom: 0;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: bottom 0.3s ease !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div.element-container #chips-anchor) > div.element-container:first-child {
        display: none !important;
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
        border-radius: 24px !important;
        padding: 6px 16px !important;
        font-size: 13px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        color: var(--sidebar-text) !important;
        border: 1px solid var(--input-border) !important;
        background-color: var(--input-bg) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        transition: all 0.25s ease !important;
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
        border-color: #2eb85c !important;
        color: #ffffff !important;
        background-color: rgba(46, 184, 92, 0.05) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(46, 184, 92, 0.15) !important;
    }

    /* CARD DE PERFIL E BOTÕES NO SIDEBAR */
    .user-profile-card {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 4px 2px !important;
        font-family: 'Outfit', sans-serif !important;
    }
    .user-avatar {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        border: 2px solid #2eb85c !important;
        object-fit: cover !important;
    }
    .user-info {
        display: flex !important;
        flex-direction: column !important;
    }
    .user-name {
        color: var(--text-color) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
    }
    .user-role {
        color: var(--muted-color) !important;
        font-size: 11px !important;
        line-height: 1.2 !important;
        margin-top: 1px !important;
    }

    /* (Custom CSS para botões tema/sair removidos para usar tertiary puro do Streamlit) */

    [data-testid="stSidebar"] div[data-testid="column"] {
        gap: 0 !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
        position: relative !important;
        align-items: center !important;
        margin-bottom: 2px !important;
    }

    /* Botão Novo Chat (que será primary) */
    [data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(90deg, #2eb85c 0%, #1b8a3e 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        height: 40px !important;
        box-shadow: 0 4px 12px rgba(46, 184, 92, 0.2) !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(46, 184, 92, 0.4) !important;
        filter: brightness(1.1) !important;
    }

    /* Botões da Lista de Histórico */
    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid transparent !important;
        justify-content: flex-start !important;
        text-align: left !important;
        color: var(--text-color) !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: rgba(128, 128, 128, 0.15) !important;
        border-color: rgba(128, 128, 128, 0.2) !important;
    }

    /* Botões da Lista de Histórico */
    [data-testid="stSidebar"] .stButton>button {
        color: var(--sidebar-text) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
        justify-content: flex-start;
        padding: 6px 30px 6px 10px !important;
        margin-bottom: 0 !important;
        border: none !important;
        background-color: transparent !important;
        font-size: 13px !important;
        min-height: 34px !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: rgba(128, 128, 128, 0.08) !important;
        color: var(--text-color) !important;
    }

    /* 1. Histórico: Reduzir espaçamento (Anulando o gap do Streamlit) */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:not(:has(.user-profile-card)) {
        margin-top: -14px !important;
    }

    /* 2. Histórico: Coluna 2 flutuante para os 3 pontinhos (APENAS HISTÓRICO) */
    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:not(:has(.user-profile-card)) > div:nth-child(2) {
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
        background: linear-gradient(90deg, transparent 0%, var(--sidebar-bg) 30%, var(--sidebar-bg) 100%) !important;
        border-radius: 0 6px 6px 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:not(:has(.user-profile-card)):hover > div:nth-child(2) {
        opacity: 1;
        background: linear-gradient(90deg, transparent 0%, rgba(200, 200, 200, 0.05) 40%, rgba(200, 200, 200, 0.05) 100%) !important;
    }
    
    /* Popover Sidebar (Três pontinhos) e chevron do st.popover */
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
        color: var(--muted-color) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stPopover"] button[kind="secondary"]:hover {
        background-color: rgba(128, 128, 128, 0.15) !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopover"] button svg,
    div[data-testid="stPopover"] button svg,
    div[data-testid="stPopover"] button span.material-symbols-rounded,
    div[data-testid="stPopover"] button span.material-icons,
    div[data-testid="stPopover"] button i {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 3. Perfil: Fixar a LINHA INTEIRA no rodapé absoluto da tela */
    div[data-testid="stHorizontalBlock"]:has(.user-profile-card) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        max-width: 244px !important;
        background-color: var(--sidebar-bg) !important;
        border-top: 1px solid rgba(128, 128, 128, 0.2) !important;
        z-index: 999999 !important;
        padding: 12px 15px !important;
        align-items: center !important;
    }

    /* 4. Perfil: Garantir que os botões Tema e Sair estão visíveis e formatados normais */
    div[data-testid="stHorizontalBlock"]:has(.user-profile-card) > div[data-testid="column"]:nth-child(2),
    div[data-testid="stHorizontalBlock"]:has(.user-profile-card) > div[data-testid="column"]:nth-child(3) {
        opacity: 1 !important;
        visibility: visible !important;
        position: relative !important;
        right: auto !important;
        background: transparent !important;
        width: auto !important;
    }
    
    /* Popover Body */
    div[data-testid="stPopoverBody"] {
        padding: 6px !important;
        background-color: var(--input-bg) !important;
        border-radius: 12px !important;
        border: 1px solid var(--input-border) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
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
        color: var(--text-color) !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stPopoverBody"] .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stMarkdownContainer"] p {
        font-size: 14px !important;
        margin: 0 !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type {
        border-top: 1px solid var(--input-border);
        margin-top: 4px;
        padding-top: 4px;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type .stButton>button p {
        color: #ff6b6b !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"] > div.element-container:last-of-type .stButton>button span {
        color: #ff6b6b !important;
    }

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
    
    /* INPUT DO CHAT */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 110px !important;
        left: 50% !important;
        transform: translateX(calc(-50% + var(--sidebar-offset))) !important;
        width: 100% !important;
        max-width: 800px !important;
        z-index: 200;
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 28px !important;
        transition: bottom 0.3s ease !important;
    }
    
    /* INPUT DO CHAT - RESET TOTAL DE FUNDOS NATIVOS */
    .stChatInputContainer, 
    .stChatInputContainer > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] div[data-baseweb="base-input"],
    [data-testid="stChatInput"] div[data-baseweb="base-input"] > div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] div[data-baseweb="textarea"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* APLICAR DESIGN APENAS NO CONTAINER PRINCIPAL */
    [data-testid="stChatInput"] {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 28px !important;
        padding: 4px 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--text-color) !important;
        box-shadow: 0 0 0 1px var(--text-color), 0 4px 24px rgba(0, 0, 0, 0.08) !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: var(--text-color) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 15px !important;
    }
    
    [data-testid="stChatInput"] button {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-color: var(--text-color) !important;
        transform: scale(1.05) !important;
    }

    /* BALÕES DE MENSAGENS PREMIUM */
    div[data-testid="stChatMessage"] {
        border-radius: 16px !important;
        margin-bottom: 12px !important;
        padding: 16px 20px !important;
        font-family: 'Outfit', sans-serif !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        animation: slideUp 0.4s ease-out !important;
        max-width: 85% !important;
    }
    
    /* Balão do Usuário */
    div[data-testid="stChatMessage"]:has(img[alt="user avatar"]),
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: var(--user-bubble-bg) !important;
        border: 1px solid var(--user-bubble-border) !important;
        margin-left: auto !important;
        border-bottom-right-radius: 4px !important;
    }
    
    /* Balão do Assistente (Tião) */
    div[data-testid="stChatMessage"]:has(img[alt="assistant avatar"]),
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background-color: var(--assistant-bubble-bg) !important;
        border: 1px solid var(--assistant-bubble-border) !important;
        margin-right: auto !important;
        border-bottom-left-radius: 4px !important;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

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
        background: rgba(128, 128, 128, 0.3); 
        border-radius: 10px;
    }

    /* WELCOME/ONBOARDING CARDS E LOGO CENTRAL */
    .welcome-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        max-width: 800px !important;
        margin: 1.5rem auto 1.5rem !important;
        text-align: center !important;
        font-family: 'Outfit', sans-serif !important;
        animation: fadeIn 0.8s ease-out !important;
    }
    
    .welcome-logo {
        width: 110px !important;
        height: auto !important;
        margin-bottom: 0.5rem !important;
        filter: drop-shadow(0px 4px 10px rgba(46, 184, 92, 0.35)) !important;
        animation: float 4s ease-in-out infinite !important;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    
    .welcome-title {
        color: var(--text-color) !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: -0.5px !important;
    }
    
    .welcome-subtitle {
        color: var(--muted-color) !important;
        font-size: 1.1rem !important;
        margin: 0.5rem 0 1.5rem 0 !important;
        font-weight: 400 !important;
    }
    
    .welcome-features {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 16px !important;
        width: 100% !important;
        margin-top: 0 !important;
    }
    
    .feature-card {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    .feature-card:hover {
        background: rgba(46, 184, 92, 0.04) !important;
        border-color: rgba(46, 184, 92, 0.3) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(46, 184, 92, 0.12) !important;
    }
    
    .feature-icon {
        font-size: 24px !important;
        margin-bottom: 12px !important;
    }
    
    .feature-title {
        color: var(--text-color) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }
    
    .feature-desc {
        color: var(--muted-color) !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
    }

    @media (max-width: 768px) {
        .welcome-features {
            grid-template-columns: 1fr !important;
        }
    }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("historico_chats.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chats (session_id TEXT PRIMARY KEY, titulo TEXT, data_criacao TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS mensagens (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)")

for col_migration in [
    "ALTER TABLE chats ADD COLUMN fixado INTEGER DEFAULT 0",
    "ALTER TABLE chats ADD COLUMN user_login TEXT DEFAULT ''",
]:
    try:
        c.execute(col_migration)
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

    if st.button("Novo Chat", icon=":material/add:", type="primary", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_title = "Novo Chat"        # Reseta os chips dinâmicos
        st.session_state.active_faqs = FAQ_POOL[:5]
        st.session_state.used_faqs = set(range(5))        
        st.rerun()
        
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px; border: 0; border-top: 1px solid rgba(128,128,128,0.2);'>", unsafe_allow_html=True) 
    
    st.markdown("### Histórico") 
    
    c.execute(
        "SELECT session_id, titulo, fixado FROM chats WHERE user_login = ? ORDER BY fixado DESC, data_criacao DESC",
        (st.session_state.usuario["login"],),
    )
    for sid, titulo, fixado in c.fetchall():
        if st.session_state.get("rename_mode") == sid:
            modal_renomear(sid, titulo)

        col1, col2 = st.columns([0.85, 0.15], gap="small")
        with col1:
            icon_fixo = "📌 " if fixado else ""
            if st.button(f"{icon_fixo}{titulo}", key=f"chat_{sid}", use_container_width=True):
                carregar_sessao = sid
        with col2:
            with st.popover("\u200B", use_container_width=True, key=f"menu_{sid}_{st.session_state.popover_nonce}"):
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

    # Espaçador para o histórico não ficar embaixo do perfil fixo
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    
    # Perfil no rodapé absoluto da tela
    _u = st.session_state.usuario
    col_nome, col_tema, col_sair = st.columns([0.7, 0.15, 0.15])
    with col_nome:
        avatar_url = _u.get("picture") or "https://www.gravatar.com/avatar/?d=mp"
        st.markdown(f"""
        <div class="user-profile-card">
            <img class="user-avatar" src="{avatar_url}" />
            <div class="user-info">
                <div class="user-name">{_u['name'].split()[0]}</div>
                <div class="user-role">{_u.get('role') or 'Consultor'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_tema:
        theme_icon = ":material/light_mode:" if st.session_state.theme == "dark" else ":material/dark_mode:"
        theme_help = "Mudar para tema claro" if st.session_state.theme == "dark" else "Mudar para tema escuro"
        if st.button("", icon=theme_icon, type="tertiary", help=theme_help, use_container_width=True, key="theme_toggle_btn"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    with col_sair:
        if st.button("", icon=":material/logout:", type="tertiary", help="Encerrar sessão", use_container_width=True, key="logout_btn"):
            del st.session_state.usuario
            st.rerun()

if carregar_sessao:
    st.session_state.session_id = carregar_sessao
    c.execute("SELECT titulo FROM chats WHERE session_id = ?", (carregar_sessao,))
    st.session_state.chat_title = c.fetchone()[0]

st.session_state.messages = []
c.execute("SELECT role, content FROM mensagens WHERE session_id = ? ORDER BY id ASC", (st.session_state.session_id,))
for row in c.fetchall():
    st.session_state.messages.append({"role": row[0], "content": row[1]})

# Lidar com cliques nos cards puros em HTML via query params
if "query" in st.query_params:
    q = st.query_params["query"]
    if q == "catalogo":
        st.session_state.faq_query = "Qual é o catálogo completo de produtos da Adubos Real?"
    elif q == "manejos":
        st.session_state.faq_query = "Gostaria de saber as dicas de manejo para lavouras de café e folhosas."
    elif q == "protecao":
        st.session_state.faq_query = "Vocês possuem recomendações de manejo focado na defesa das plantas?"
    st.query_params.clear()

# --- PÁGINA INICIAL ---
if len(st.session_state.messages) == 0:
    first_name = st.session_state.usuario['name'].split()[0].title()
    st.markdown(
        f"""
        <div id='empty-state'></div>
        <div class="welcome-container">
            <img class="welcome-logo" src="data:image/png;base64,{logo_base64}" />
            <h1 class="welcome-title">Olá, {first_name}!</h1>
            <p class="welcome-subtitle">Eu sou o Tião. Como posso apoiar suas recomendações agronômicas hoje?</p>
            <div class="welcome-features">
                <a href="?query=catalogo" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div class="feature-card">
                        <div class="feature-icon">🌱</div>
                        <div class="feature-title">Catálogo de Produtos</div>
                        <div class="feature-desc">Consulte formulações, dosagens e linhas exclusivas da Adubos Real.</div>
                    </div>
                </a>
                <a href="?query=manejos" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div class="feature-card">
                        <div class="feature-icon">🥬</div>
                        <div class="feature-title">Manejos e Culturas</div>
                        <div class="feature-desc">Dicas de nutrição ideais para hortifrúti, café, pastagens e folhosas.</div>
                    </div>
                </a>
                <a href="?query=protecao" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div class="feature-card">
                        <div class="feature-icon">🛡️</div>
                        <div class="feature-title">Proteção e Nutrição</div>
                        <div class="feature-desc">Recomendações técnicas para a máxima produtividade e defesa da lavoura.</div>
                    </div>
                </a>
            </div>
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

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")


def stream_resposta(payload: dict):
    with requests.post(
        f"{API_BASE}/chat/stream",
        json=payload,
        stream=True,
        timeout=(5, None),
    ) as r:
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


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
        c.execute(
            "INSERT INTO chats (session_id, titulo, data_criacao, user_login) VALUES (?, ?, ?, ?)",
            (st.session_state.session_id, novo_titulo, data_agora, st.session_state.usuario["login"]),
        )
        
    c.execute("INSERT INTO mensagens (session_id, role, content) VALUES (?, ?, ?)", 
              (st.session_state.session_id, "user", prompt))
    conn.commit()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    historico_envio = st.session_state.messages[:-1][-4:]
    payload = {
        "question": prompt,
        "history": historico_envio,
        "user_login": st.session_state.usuario["login"],
    }
    answer = None

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(stream_resposta(payload))
        except requests.exceptions.ConnectionError:
            st.error("🚨 Não foi possível conectar à API. Você rodou seu `main.py`?")
        except requests.exceptions.Timeout:
            st.error("⏱️ A API demorou demais para responder. Tente novamente.")
        except Exception as e:
            st.error(f"⚠️ Erro inesperado: {str(e)}")

    if answer:
        c.execute("INSERT INTO mensagens (session_id, role, content) VALUES (?, ?, ?)",
                  (st.session_state.session_id, "assistant", answer))
        conn.commit()
        st.session_state.messages.append({"role": "assistant", "content": answer})

        if len(st.session_state.messages) == 2:
            st.rerun()

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
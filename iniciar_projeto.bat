@echo off
:: Garante que o terminal mude para a pasta onde o arquivo .bat esta localizado
cd /d "%~dp0"

echo ===================================================
echo   Iniciando RAG - Adubos Real
echo ===================================================

:: 1. Ativa o ambiente virtual local
echo [1/3] Ativando o ambiente virtual (.venv)...
if not exist ".venv" (
    echo [ERRO] Pasta .venv nao encontrada! Garanta que criou o ambiente virtual.
    pause
    exit /b
)

:: 2. Inicia o Backend (FastAPI) em uma nova janela
echo [2/3] Iniciando o Backend (FastAPI) em nova janela...
start "RAG Backend - FastAPI" cmd /k "call .venv\Scripts\activate.bat && python main.py"

:: Aguarda 3 segundos para o backend inicializar antes do frontend
timeout /t 3 /nobreak >nul

:: 3. Inicia o Frontend (Streamlit) na janela atual
echo [3/3] Iniciando o Frontend (Streamlit)...
call .venv\Scripts\activate.bat
python -m streamlit run chat_ui.py


pause

import os
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from dotenv import load_dotenv

# Configuração via arquivo .env
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Chave OpenAI_API_KEY nao encontrada! Configure-a no arquivo .env")

os.environ["OPENAI_API_KEY"] = openai_key


json_link = "catalogo_consolidado.json"

try:
    with open(json_link, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    documents = []
    # Converter o JSON para o formato Document do LangChain
    for page in json_data.get("pages", []):
        doc = Document(
            page_content=page.get("text_markdown", ""),
            metadata={"page": page.get("page_number", 0), "source": json_link}
        )
        documents.append(doc)
        
    print(f"Foram carregadas {len(documents)} páginas do JSON com sucesso!")
    
    # Separar em Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=20,
        length_function=len,
        add_start_index=True
    )
    chunks_json = text_splitter.split_documents(documents)
    print(f"Documento dividido em {len(chunks_json)} chunks.")
    
    # Salvar num novo Vector DB (ChromaDB)
    embeddings_model = OpenAIEmbeddings()
    db_json = Chroma.from_documents(chunks_json, embedding=embeddings_model, persist_directory="text_index")
    print("VectorDB do JSON criado e salvo com sucesso usando catalogo_consolidado.json!")
    
except FileNotFoundError:
    print(f"Arquivo {json_link} não encontrado. Certifique-se de que ele existe na pasta.")
except Exception as e:
    print(f"Erro: {str(e)}")

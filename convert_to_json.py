import json
import time
import argparse
from pathlib import Path

try:
    import pymupdf4llm
except ImportError:
    print("A biblioteca 'pymupdf4llm' não foi encontrada.")
    print("Por favor, instale executando: pip install pymupdf4llm")
    exit(1)

def convert_pdf_to_json(pdf_path: str, json_path: str):
    """
    Converte um PDF estruturado para um arquivo JSON, focado na compreensão por LLMs.
    Utiliza PyMuPDF4LLM para extrair o conteúdo já formatado em Markdown (ótimo para tabelas e hierarquias).
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Erro: O arquivo '{pdf_path}' não foi encontrado.")
        return

    print(f"Iniciando o processamento do arquivo: {pdf_file.name}...")
    start_time = time.time()

    try:
        # A opção page_chunks=True faz com que a biblioteca retorne uma lista de dicionários,
        # cada um representando uma página com seu texto em Markdown e os metadados associados.
        documents = pymupdf4llm.to_markdown(str(pdf_file), page_chunks=True)
        
        # Estrutura do JSON final
        output_data = {
            "document_info": {
                "source_file": pdf_file.name,
                "total_pages": len(documents),
                "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "pages": []
        }

        # Formatando as páginas para o JSON
        for doc in documents:
            page_data = {
                "page_number": doc.get("metadata", {}).get("page", 0),
                "text_markdown": doc.get("text", ""),
                "metadata": doc.get("metadata", {})
            }
            output_data["pages"].append(page_data)

        # Salvando o resultado no arquivo JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

        elapsed_time = time.time() - start_time
        print(f"Sucesso! O PDF foi convertido e salvo em '{json_path}'.")
        print(f"Tempo de processamento: {elapsed_time:.2f} segundos.")
        print(f"Total de páginas processadas: {len(documents)}")

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

if __name__ == "__main__":
    # Configurando argumentos de linha de comando para uso prático
    parser = argparse.ArgumentParser(description="Converter PDF para JSON (Formato Markdown LLM-ready).")
    parser.add_argument("-i", "--input", required=True, help="Caminho do arquivo PDF de entrada.")
    parser.add_argument("-o", "--output", default="output.json", help="Caminho do arquivo JSON de saída.")
    
    args = parser.parse_args()
    
    convert_pdf_to_json(args.input, args.output)

#pip install pymupdf4llm
#python convert_to_json.py -i "zapp_qi.pdf" -o "bula_zap.json"

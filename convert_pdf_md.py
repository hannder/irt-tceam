import os
import argparse
from docling.document_converter import DocumentConverter

def convert_pdfs_to_md(source_folder, output_folder):
    # Criar a pasta de saída se não existir
    os.makedirs(output_folder, exist_ok=True)
    
    # Inicializar o conversor de documentos
    converter = DocumentConverter()
    
    # Listar arquivos na pasta de origem
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(".pdf"):  # Garantir que seja um arquivo PDF
            source_path = os.path.join(source_folder, filename)
            
            try:
                # Converter o arquivo PDF
                result = converter.convert(source_path)
                md_content = result.document.export_to_markdown()
                
                # Criar o caminho do arquivo de saída
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.md")
                
                # Salvar o conteúdo Markdown
                with open(output_path, "w", encoding="utf-8") as md_file:
                    md_file.write(md_content)
                
                print(f"Convertido: {filename} -> {output_path}")
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converter PDFs para Markdown usando Docling.")
    parser.add_argument("source_folder", type=str, help="Pasta contendo os arquivos PDF")
    parser.add_argument("output_folder", type=str, help="Pasta onde os arquivos MD serão salvos")
    
    args = parser.parse_args()
    convert_pdfs_to_md(args.source_folder, args.output_folder)

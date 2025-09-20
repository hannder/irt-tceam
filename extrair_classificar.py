# Standard library imports
import argparse
import csv
import datetime
import json
import os
import shutil
import time
import traceback
from typing import List, Optional
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

# Local imports
from acordao import Acordao
from settings import ARQUIVO_CONTROLE, ARQUIVO_LOG_ERROS, DIRETORIO_MARKDOWN, MODEL_ID, GEMINI_API_KEY

# Load environment variables
load_dotenv()
api_key = GEMINI_API_KEY
client = genai.Client(api_key=api_key)

# Define the model you are going to use
model_id = MODEL_ID

def carregar_prompt() -> str:
    script_dir = Path(__file__).parent
    prompt_dir = script_dir / "prompts"
    
    # Carrega o prompt principal que terá os placeholders
    with open(prompt_dir / "prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()


    # Carrega as temas
    with open(prompt_dir / "temas.txt", "r", encoding="utf-8") as f:
        temas = f.read()

    # Carrega as tipologias
    with open(prompt_dir / "tipologias.json", "r", encoding="utf-8") as f:
        tipologias = f.read()

    # Formata o prompt substituindo os placeholders
    prompt_completo = prompt_template.format(
        temas=temas,
        tipologias=tipologias,
    )
      
    return prompt_completo

def carregar_status_processamento():
    """
    Carrega os status dos arquivos já processados a partir do arquivo de controle.
    Retorna um dicionário onde a chave é o nome do arquivo e o valor é uma lista de status.
    """
    status_arquivos = {}
    if os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, mode="r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) >= 4:
                    nome_arquivo, _, _, status = row[:4]
                    if nome_arquivo not in status_arquivos:
                        status_arquivos[nome_arquivo] = []
                    status_arquivos[nome_arquivo].append(status)
    return status_arquivos

def salvar_txt_com_backup(nome_arquivo_txt: str, result):
    """
    Salva o JSON extraído e mantém uma cópia da versão anterior caso já exista.
    """
    caminho_txt = os.path.join(DIRETORIO_MARKDOWN, nome_arquivo_txt)

    # Se o arquivo JSON já existir, criar uma cópia antes de sobrescrevê-lo
    if os.path.exists(caminho_txt):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_backup = nome_arquivo_txt.replace(".txt", f".txt_versao{timestamp}")
        caminho_backup = os.path.join(DIRETORIO_MARKDOWN, nome_backup)
        shutil.move(caminho_txt, caminho_backup)
        print(f"📂 Backup criado: {caminho_backup}")

    # Salvar o novo JSON gerado
    with open(caminho_txt, "w", encoding="utf-8") as txt_file:
        txt_file.write(result)

    print(f"✅ Novo TXT salvo como '{caminho_txt}'")
    
def salvar_json_com_backup(nome_arquivo_json: str, result):
    """
    Salva o JSON extraído e mantém uma cópia da versão anterior caso já exista.
    """
    caminho_json = os.path.join(DIRETORIO_MARKDOWN, nome_arquivo_json)

    # Se o arquivo JSON já existir, criar uma cópia antes de sobrescrevê-lo
    if os.path.exists(caminho_json):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_backup = nome_arquivo_json.replace(".json", f".json_versao{timestamp}")
        caminho_backup = os.path.join(DIRETORIO_MARKDOWN, nome_backup)
        shutil.move(caminho_json, caminho_backup)
        print(f"📂 Backup criado: {caminho_backup}")

    # Salvar o novo JSON gerado
    with open(caminho_json, "w", encoding="utf-8") as json_file:
        json.dump(result.model_dump(), json_file, ensure_ascii=False, indent=4)

    print(f"✅ Novo JSON salvo como '{caminho_json}'")

def registrar_processamento(nome_md: str, nome_json: Optional[str], status: str):
    """
    Registra o status do processamento no arquivo de controle.
    """
    data_processamento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARQUIVO_CONTROLE, mode="a", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([nome_md, nome_json if nome_json else "N/A", data_processamento, status])

def registrar_erro(nome_arquivo: str, erro: str):
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARQUIVO_LOG_ERROS, mode="a", encoding="utf-8") as log_file:
        log_file.write(f"[{data_hora}] Erro ao processar {nome_arquivo}:\n{erro}\n{'-'*80}\n")

def extract_structured_data(file_path: str, model: BaseModel):
    """
    Extrai dados estruturados de um arquivo markdown usando a API Gemini,
    garantindo detalhamento e categorização conforme o modelo especificado.
    """
    try:
        # Ler o conteúdo do arquivo markdown
        with open(file_path, 'r', encoding='utf-8') as md_file:
            content = md_file.read()

        prompt = carregar_prompt()
        #salvar o prompt de cada processamento em um arquivo diferente
        with open(os.path.join(DIRETORIO_MARKDOWN, "prompt_categorizar_acordao.txt"), "w", encoding="utf-8") as prompt_file:
            prompt_file.write(prompt)

        nome_arquivo_json = os.path.basename(file_path).replace('.md', '.json')
        nome_arquivo_txt = os.path.basename(file_path).replace('.md', '.txt')

        print(f"🔍 Solicitando resposta da extração...")

        # Chamada à API Gemini para extração de conteúdo estruturado
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt, content],
            config={'response_mime_type': 'application/json', 'response_schema': model}
        )
        
        if hasattr(response, "text"):
            salvar_txt_com_backup(nome_arquivo_txt, response.text)

        # Verifica se a resposta é válida
        if response and hasattr(response, "parsed"):
            return response.parsed, nome_arquivo_json, "Sucesso"
        else:
            raise ValueError("Resposta malformada ou incompleta.")

    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print(f"❌ Erro ao processar {file_path}: {e}")
        registrar_erro(os.path.basename(file_path), erro_detalhado)
        return None, None, "Falha"

def processar_arquivos(processar_todos=False, processar_novos_e_falhas=False):
    try:
        if not os.path.exists(DIRETORIO_MARKDOWN):
            print(f"❌ Diretório {DIRETORIO_MARKDOWN} não encontrado.")
            return

        arquivos_md = [f for f in os.listdir(DIRETORIO_MARKDOWN) if f.endswith(".md")]
        status_arquivos = carregar_status_processamento()

        # Filtragem dos arquivos a serem processados
        arquivos_a_processar = []
        for arquivo in arquivos_md:
            historico_status = status_arquivos.get(arquivo, [])
            if processar_todos:
                arquivos_a_processar.append(arquivo)
            elif processar_novos_e_falhas:
                if "Sucesso" in historico_status:
                    continue
                if "Falha" in historico_status or "Erro no parse" in historico_status:
                    arquivos_a_processar.append(arquivo)
            else:
                if not historico_status:
                    arquivos_a_processar.append(arquivo)

        if not arquivos_a_processar:
            print("📂 Nenhum arquivo MD encontrado para processamento.")
            return

        for arquivo in arquivos_a_processar:
            caminho_arquivo = os.path.join(DIRETORIO_MARKDOWN, arquivo)
            print(f"🔍 Processando {arquivo}...")

            result, nome_arquivo_json, status = extract_structured_data(caminho_arquivo, Acordao)

            if status == "Sucesso":
                print(f"✅ Resposta com sucesso")

                if(hasattr(result, "model_dump")):
                    salvar_json_com_backup(nome_arquivo_json, result)
                else:
                    nome_arquivo_json = nome_arquivo_json.replace(".json", ".error")
                    caminho_json = os.path.join(DIRETORIO_MARKDOWN, nome_arquivo_json)
                    with open(caminho_json, "w", encoding="utf-8") as json_file:
                        json.dump(result, json_file, ensure_ascii=False, indent=4)
                    status = "Erro no parse"
                    print(f"❌ Error file salvo como '{caminho_json}'")
                    registrar_erro(os.path.basename(caminho_json), status)
            else:
                print(f"❌ Falha ao processar {arquivo}. Detalhes do erro em {ARQUIVO_LOG_ERROS}")
                erro_detalhado = traceback.format_exc()
                registrar_erro(os.path.basename(arquivo), erro_detalhado)

            registrar_processamento(arquivo, nome_arquivo_json, status)

    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print(f"❌ Erro ao processar {arquivo}: {e}")
        registrar_erro(os.path.basename(arquivo), erro_detalhado)

    print("\n✅ Processamento concluído!")

def processar_arquivo_unico(nome_arquivo: str, teste=True):
    """
    Processa um único arquivo MD, extraindo dados estruturados e salvando o JSON correspondente.
    """
    caminho_arquivo = os.path.join(DIRETORIO_MARKDOWN, nome_arquivo)

    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo '{nome_arquivo}' não encontrado no diretório '{DIRETORIO_MARKDOWN}'.")
        return

    print(f"🔍 Processando '{nome_arquivo}'...")

    result, nome_arquivo_json, status = extract_structured_data(caminho_arquivo, Acordao)

    if teste:
        nome_arquivo_json = nome_arquivo_json.replace(".json", ".json_temp")

    if status == "Sucesso":
        print(f"✅ Resposta com sucesso")

        if hasattr(result, "model_dump"):
            salvar_json_com_backup(nome_arquivo_json, result)
        else:
            nome_arquivo_json = nome_arquivo_json.replace(".json", ".error")
            caminho_json = os.path.join(DIRETORIO_MARKDOWN, nome_arquivo_json)
            with open(caminho_json, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)
            status = "Erro no parse"
            print(f"❌ Error file salvo como '{caminho_json}'")
            registrar_erro(os.path.basename(caminho_json), status)

    else:
        print(f"❌ Falha ao processar '{nome_arquivo}'. Detalhes do erro em {ARQUIVO_LOG_ERROS}")
        erro_detalhado = traceback.format_exc()
        registrar_erro(os.path.basename(nome_arquivo), erro_detalhado)

    if not teste:
        registrar_processamento(nome_arquivo, nome_arquivo_json, status)

    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processador de Acórdãos em Markdown")
    parser.add_argument("--arquivo", type=str, default=None, help="Nome do arquivo MD a ser processado.")
    parser.add_argument("--teste", action="store_true", help="Modo de teste. Não salva resultados permanentemente.")
    parser.add_argument("--processar-todos", action="store_true", help="Processa todos arquivos MD ignorando arquivo controle.")
    parser.add_argument("--processar-novos-e-falhas", action="store_true", help="Processa arquivos novos e aqueles com falhas anteriores.")

    args = parser.parse_args()

    if args.arquivo:
        processar_arquivo_unico(args.arquivo, teste=args.teste)
    else:
        processar_arquivos(processar_todos=args.processar_todos, processar_novos_e_falhas=args.processar_novos_e_falhas) 
"""Módulo de configuração do projeto."""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "gemini-2.0-flash")

# Configurações de arquivos
ARQUIVO_SCHEMA = os.getenv("ARQUIVO_SCHEMA", "acordao_schema.json")
DIRETORIO_PDFS = os.getenv("DIRETORIO_PDFS", "pdfs/")
DIRETORIO_MARKDOWN = os.getenv("DIRETORIO_MARKDOWN", "arquivos_md/")
ARQUIVO_CONTROLE = os.getenv("ARQUIVO_CONTROLE", "controle_processamento.csv")
ARQUIVO_LOG_ERROS = os.getenv("ARQUIVO_LOG_ERROS", "erros.log")

# Configurações de processamento
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30")) 
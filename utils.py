"""Módulo de funções utilitárias."""

import os
import logging
from typing import Optional
from datetime import datetime

from settings import ARQUIVO_LOG_ERROS

def setup_logging() -> None:
    """Configura o sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(ARQUIVO_LOG_ERROS),
            logging.StreamHandler()
        ]
    )

def registrar_erro(erro: Exception, arquivo: str, conteudo: Optional[str] = None) -> None:
    """
    Registra um erro no arquivo de log.
    
    Args:
        erro: A exceção que ocorreu
        arquivo: Nome do arquivo que estava sendo processado
        conteudo: Conteúdo opcional que estava sendo processado
    """
    logging.error(f"Erro ao processar arquivo {arquivo}: {str(erro)}")
    if conteudo:
        logging.error(f"Conteúdo que causou o erro: {conteudo}")

def criar_diretorio_se_nao_existe(diretorio: str) -> None:
    """
    Cria um diretório se ele não existir.
    
    Args:
        diretorio: Caminho do diretório a ser criado
    """
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

def obter_data_atual() -> str:
    """
    Retorna a data atual no formato YYYYMMDD.
    
    Returns:
        str: Data atual formatada
    """
    return datetime.now().strftime("%Y%m%d") 
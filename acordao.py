"""Módulo contendo os modelos de dados para extração de acórdãos."""

from typing import List
from pydantic import BaseModel, Field

class FundamentacaoLegal(BaseModel):
    """Modelo para fundamentação legal de um trecho."""
    norma: str = Field(description="Nome completo da norma ou lei aplicável")
    artigo: str = Field(description="Artigo ou seção específica da lei ou norma citada")
    descricao: str = Field(description="Resumo claro e completo da fundamentação legal")

class TrechoIdentificado(BaseModel):
    """Modelo para trecho identificado em um acórdão."""
    trecho: str = Field(description="Trecho específico extraído do inteiro teor")
    irregularidade: bool = Field(description="Indica se o trecho descreve uma irregularidade")
    relevante_para_indice: bool = Field(description="Indica se o trecho é relevante para o índice")
    tema_irregularidade: str = Field(description="Tema da irregularidade")    
    codigo_irregularidade: str = Field(description="Código da tipologia da irregularidade")
    tipologia_irregularidade: str = Field(description="Tipologia da irregularidade")
    descricao: str = Field(description="Descrição da irregularidade")
    justificativa_tipologia: str = Field(description="Justificativa para a classificação")
    fundamentacao_legal: List[FundamentacaoLegal] = Field(description="Lista de fundamentações legais")

class ItemDeliberacao(BaseModel):
    """Modelo para item de deliberação de um acórdão."""
    tipo: str = Field(description="Tipo da deliberação (irregularidade, recomendação, sanção, determinação)")
    descricao: str = Field(description="Texto completo da deliberação")
    trechos_identificados: List[TrechoIdentificado] = Field(description="Lista de trechos extraídos")

class Acordao(BaseModel):
    """Modelo principal para representação de um acórdão."""
    acordao: str = Field(description="Número do acórdão")
    processo: str = Field(description="Número do processo")
    data_sessao: str = Field(description="Data da sessão de julgamento")
    orgao: str = Field(description="Órgão relacionado ao acórdão")
    municipio: str = Field(description="Município do órgão fiscalizado")
    exercicio: str = Field(description="Ano do exercício analisado")
    responsavel: List[str] = Field(description="Lista de responsáveis")
    itens: List[ItemDeliberacao] = Field(description="Lista de deliberações") 
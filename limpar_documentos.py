#!/usr/bin/env python3
"""
Script para processar documentos em lote, removendo padrões específicos.
"""

import re
import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional

class ProcessadorDocumentos:
    """Classe para processar documentos removendo padrões específicos."""
    
    def __init__(self):
        self.padroes = [
            # Linhas com campos vazios (underscores)
            r'^.*_+.*$',
            
            # Linhas com "De ___/___/___"
            r'^De _+/_+/_+.*$',
            
            # Linhas com "Edição nº___"
            r'^Edição nº_+.*$',
            
            # Linhas com "P roc. Nº ___"
            r'^P roc\. Nº _+.*$',
            
            # Linhas com "Fls. Nº ___"
            r'^Fls\. Nº _+.*$',
            
            # Comentários HTML
            r'<!--.*?-->',
            
            # Linhas de assinatura digital
            r'^Este documento foi assinado digitalmente por.*$',
            
            # Linhas com links de conferência
            r'^Para conferŒncia acesse o site.*$',
            
            # Linhas com códigos de verificação
            r'^e informe o código:.*$',
            
            # Linhas com "Publicado no Diário Eletrônico"
            r'^Publicado no Diário Eletrônico.*$',
            
            # Linhas vazias múltiplas (mais de 2 consecutivas)
            r'\n\s*\n\s*\n+',
            
            # Linhas com apenas espaços ou tabs
            r'^\s+$',
        ]
    
    def adicionar_padrao(self, padrao: str):
        """Adiciona um padrão personalizado."""
        self.padroes.append(padrao)
    
    def limpar_texto(self, texto: str) -> str:
        """Limpa o texto aplicando todos os padrões."""
        resultado = texto
        
        for padrao in self.padroes:
            resultado = re.sub(padrao, '', resultado, flags=re.MULTILINE)
        
        # Remove linhas vazias excessivas
        resultado = re.sub(r'\n\s*\n\s*\n+', '\n\n', resultado)
        
        return resultado
    
    def processar_arquivo(self, arquivo_entrada: str, arquivo_saida: Optional[str] = None) -> dict:
        """
        Processa um único arquivo.
        
        Returns:
            dict: Estatísticas do processamento
        """
        try:
            # Lê o arquivo
            with open(arquivo_entrada, 'r', encoding='utf-8') as f:
                conteudo_original = f.read()
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
        
        tamanho_original = len(conteudo_original)
        
        # Limpa o conteúdo
        conteudo_limpo = self.limpar_texto(conteudo_original)
        tamanho_limpo = len(conteudo_limpo)
        
        # Define arquivo de saída
        if arquivo_saida is None:
            arquivo_path = Path(arquivo_entrada)
            arquivo_saida = str(arquivo_path.parent / f"{arquivo_path.stem}_limpo{arquivo_path.suffix}")
        
        # Salva o arquivo
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(conteudo_limpo)
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
        
        return {
            'sucesso': True,
            'arquivo_entrada': arquivo_entrada,
            'arquivo_saida': arquivo_saida,
            'tamanho_original': tamanho_original,
            'tamanho_limpo': tamanho_limpo,
            'caracteres_removidos': tamanho_original - tamanho_limpo,
            'percentual_removido': ((tamanho_original - tamanho_limpo) / tamanho_original * 100) if tamanho_original > 0 else 0
        }
    
    def processar_pasta(self, pasta_entrada: str, pasta_saida: Optional[str] = None, 
                       extensoes: Optional[List[str]] = None, recursivo: bool = False) -> dict:
        """
        Processa todos os arquivos de uma pasta.
        
        Returns:
            dict: Estatísticas do processamento
        """
        if extensoes is None:
            extensoes = ['.md', '.txt']
        
        pasta_path = Path(pasta_entrada)
        
        if not pasta_path.exists():
            return {'sucesso': False, 'erro': f"Pasta '{pasta_entrada}' não encontrada."}
        
        if not pasta_path.is_dir():
            return {'sucesso': False, 'erro': f"'{pasta_entrada}' não é uma pasta."}
        
        # Define pasta de saída
        if pasta_saida is None:
            pasta_saida = pasta_path.parent / f"{pasta_path.name}_limpos"
        else:
            pasta_saida = Path(pasta_saida)
        
        # Cria pasta de saída
        pasta_saida.mkdir(parents=True, exist_ok=True)
        
        # Encontra arquivos
        if recursivo:
            arquivos = []
            for ext in extensoes:
                arquivos.extend(pasta_path.rglob(f"*{ext}"))
        else:
            arquivos = []
            for arquivo in pasta_path.iterdir():
                if arquivo.is_file() and arquivo.suffix.lower() in extensoes:
                    arquivos.append(arquivo)
        
        # Processa arquivos
        resultados = []
        total_original = 0
        total_limpo = 0
        
        for arquivo in arquivos:
            arquivo_saida = pasta_saida / arquivo.name
            
            # Mantém estrutura de pastas se recursivo
            if recursivo and arquivo.parent != pasta_path:
                rel_path = arquivo.relative_to(pasta_path)
                arquivo_saida = pasta_saida / rel_path
                arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
            
            resultado = self.processar_arquivo(str(arquivo), str(arquivo_saida))
            resultados.append(resultado)
            
            if resultado['sucesso']:
                total_original += resultado['tamanho_original']
                total_limpo += resultado['tamanho_limpo']
        
        sucessos = [r for r in resultados if r['sucesso']]
        falhas = [r for r in resultados if not r['sucesso']]
        
        return {
            'sucesso': True,
            'pasta_entrada': pasta_entrada,
            'pasta_saida': str(pasta_saida),
            'total_arquivos': len(arquivos),
            'sucessos': len(sucessos),
            'falhas': len(falhas),
            'total_original': total_original,
            'total_limpo': total_limpo,
            'total_removido': total_original - total_limpo,
            'percentual_removido': ((total_original - total_limpo) / total_original * 100) if total_original > 0 else 0,
            'resultados': resultados
        }

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Processa documentos removendo padrões específicos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python limpar_documentos.py arquivo.md
  python limpar_documentos.py pasta/ --saida pasta_limpa/
  python limpar_documentos.py pasta/ --extensoes .md,.txt --recursivo
  python limpar_documentos.py pasta/ --padrao "meu_padrao_regex"
        """
    )
    
    parser.add_argument('entrada', help='Arquivo ou pasta para processar')
    parser.add_argument('-o', '--saida', help='Arquivo ou pasta de saída')
    parser.add_argument('-e', '--extensoes', help='Extensões para processar (ex: .md,.txt)')
    parser.add_argument('-r', '--recursivo', action='store_true', help='Processar subpastas recursivamente')
    parser.add_argument('-p', '--padrao', action='append', help='Padrão regex personalizado (pode ser usado múltiplas vezes)')
    parser.add_argument('--preview', action='store_true', help='Mostra preview sem modificar arquivos')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Cria processador
    processador = ProcessadorDocumentos()
    
    # Adiciona padrões personalizados
    if args.padrao:
        for padrao in args.padrao:
            processador.adicionar_padrao(padrao)
    
    # Processa extensões
    extensoes = None
    if args.extensoes:
        extensoes = [ext.strip() for ext in args.extensoes.split(',')]
        extensoes = [ext if ext.startswith('.') else f'.{ext}' for ext in extensoes]
    
    entrada_path = Path(args.entrada)
    
    if entrada_path.is_file():
        # Processa arquivo único
        if args.preview:
            print("Modo preview não implementado para arquivos únicos.")
            return
        
        resultado = processador.processar_arquivo(args.entrada, args.saida)
        
        if resultado['sucesso']:
            print(f"✅ Arquivo processado com sucesso!")
            print(f"   Entrada: {resultado['arquivo_entrada']}")
            print(f"   Saída: {resultado['arquivo_saida']}")
            print(f"   Tamanho: {resultado['tamanho_original']} → {resultado['tamanho_limpo']} caracteres")
            print(f"   Removidos: {resultado['caracteres_removidos']} ({resultado['percentual_removido']:.1f}%)")
        else:
            print(f"❌ Erro: {resultado['erro']}")
            sys.exit(1)
    
    elif entrada_path.is_dir():
        # Processa pasta
        resultado = processador.processar_pasta(
            args.entrada, 
            args.saida, 
            extensoes, 
            args.recursivo
        )
        
        if not resultado['sucesso']:
            print(f"❌ Erro: {resultado['erro']}")
            sys.exit(1)
        
        # Mostra resumo
        print(f"📁 Pasta processada: {resultado['pasta_entrada']}")
        print(f"📁 Pasta de saída: {resultado['pasta_saida']}")
        print(f"📊 Arquivos: {resultado['sucessos']}/{resultado['total_arquivos']} processados com sucesso")
        
        if resultado['falhas'] > 0:
            print(f"⚠️  Falhas: {resultado['falhas']}")
        
        print(f"📈 Tamanho total: {resultado['total_original']} → {resultado['total_limpo']} caracteres")
        print(f"🗑️  Removidos: {resultado['total_removido']} ({resultado['percentual_removido']:.1f}%)")
        
        # Mostra detalhes se verboso
        if args.verbose and resultado['resultados']:
            print("\n📋 Detalhes por arquivo:")
            for res in resultado['resultados']:
                if res['sucesso']:
                    print(f"  ✅ {Path(res['arquivo_entrada']).name}: "
                          f"{res['tamanho_original']} → {res['tamanho_limpo']} "
                          f"(-{res['caracteres_removidos']}, {res['percentual_removido']:.1f}%)")
                else:
                    print(f"  ❌ {Path(res['arquivo_entrada']).name}: {res['erro']}")
    
    else:
        print(f"❌ Erro: '{args.entrada}' não é um arquivo ou pasta válida.")
        sys.exit(1)

if __name__ == '__main__':
    main()

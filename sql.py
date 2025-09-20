import sqlite3
import json
import os
import argparse
import time
import shutil

# 🔹 Função para renomear o banco de dados caso já exista
def verificar_e_renomear_banco(database_path):
    if os.path.exists(database_path):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        novo_nome = f"{database_path.replace('.db', '')}_{timestamp}.db"
        shutil.move(database_path, novo_nome)
        print(f"🔄 Banco de dados existente renomeado para: {novo_nome}")

# 🔹 Configuração da linha de comando
parser = argparse.ArgumentParser(description="Importa JSONs para um banco SQLite")
parser.add_argument("database_path", type=str, help="Caminho do banco de dados SQLite")
parser.add_argument("--diretorio-jsons", type=str, help="Diretório contendo os arquivos JSON")
parser.add_argument("--arquivo-json", type=str, help="Arquivo JSON único a ser inserido")

args = parser.parse_args()
DATABASE_PATH = args.database_path
DIRETORIO_JSONS = args.diretorio_jsons
ARQUIVO_JSON = args.arquivo_json

# 🔹 Verificar se pelo menos uma operação foi solicitada
if not DIRETORIO_JSONS and not ARQUIVO_JSON:
    print("❌ É necessário especificar --diretorio-jsons ou --arquivo-json.")
    exit(1)

# 🔹 Verificar diretório dos arquivos JSON se fornecido
if DIRETORIO_JSONS and not os.path.exists(DIRETORIO_JSONS):
    print(f"❌ Diretório {DIRETORIO_JSONS} não encontrado.")
    exit(1)

# 🔹 Verificar arquivo JSON se fornecido
if ARQUIVO_JSON and not os.path.exists(ARQUIVO_JSON):
    print(f"❌ Arquivo JSON {ARQUIVO_JSON} não encontrado.")
    exit(1)

# 🔹 Renomeia banco de dados se já existir e não estiver apenas um único arquivo
if os.path.exists(DATABASE_PATH):
    verificar_e_renomear_banco(DATABASE_PATH)

# 🔹 Conectar ao banco de dados
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# 🔹 Criar tabelas se não existirem
cursor.executescript("""
CREATE TABLE IF NOT EXISTS acordaos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_arquivo TEXT NOT NULL,                    
    numero_acordao TEXT NOT NULL,
    numero_processo TEXT NOT NULL,
    data_sessao TEXT NOT NULL,
    orgao TEXT NOT NULL,
    municipio TEXT NOT NULL,
    exercicio TEXT NOT NULL,
    responsavel TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS itens_deliberacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    acordao_id INTEGER NOT NULL,
    FOREIGN KEY (acordao_id) REFERENCES acordaos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trechos_identificados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_deliberacao_id INTEGER NOT NULL,
    trecho TEXT NOT NULL,
    irregularidade BOOLEAN NOT NULL,
    relevante_para_indice BOOLEAN NOT NULL,
    tema_irregularidade TEXT NOT NULL,
    codigo_irregularidade TEXT NOT NULL,
    tipologia_irregularidade TEXT NOT NULL,
    descricao TEXT NOT NULL,
    justificativa_tipologia TEXT NOT NULL,
    FOREIGN KEY (item_deliberacao_id) REFERENCES itens_deliberacao(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fundamentacao_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trecho_identificado_id INTEGER NOT NULL,
    norma TEXT NOT NULL,
    artigo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    FOREIGN KEY (trecho_identificado_id) REFERENCES trechos_identificados(id) ON DELETE CASCADE
);

""")
conn.commit()

# 🔹 Função para importar listas de arquivos de texto
def importar_lista_arquivo(arquivo, tabela):
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo {arquivo} não encontrado.")
        return 0
    
    itens_importados = 0
    with open(arquivo, "r", encoding="utf-8") as file:
        for linha in file:
            linha = linha.strip()
            if linha:
                try:
                    cursor.execute(f"INSERT INTO {tabela} (descricao) VALUES (?)", (linha,))
                    itens_importados += 1
                except sqlite3.IntegrityError:
                    # Item já existe na tabela
                    pass
    
    conn.commit()
    return itens_importados

# 🔹 Função para inserir os dados no banco de dados
def inserir_acordao(dados_json):
    if "itens" not in dados_json:
        print(f"❌ Acórdão {dados_json['acordao']} não possui itens.")
        return
        
    cursor.execute("""
        INSERT INTO acordaos (nome_arquivo, numero_acordao, numero_processo, data_sessao, orgao, municipio, exercicio, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados_json["nome_arquivo"],
        dados_json["acordao"],
        dados_json["processo"],
        dados_json["data_sessao"],
        dados_json["orgao"],
        dados_json["municipio"],
        dados_json["exercicio"],
        ", ".join(dados_json["responsavel"]),  # Armazena a lista como string separada por vírgula
    ))

    acordao_id = cursor.lastrowid  # Obtém o ID do acórdão inserido

    # 🔹 Inserir Itens de Deliberação
    for item in dados_json["itens"]:
        if "tipo" not in item or item["tipo"] is None:
            item["tipo"] = "Não especificado"
        
        cursor.execute("""
            INSERT INTO itens_deliberacao (tipo, descricao, acordao_id)
            VALUES (?, ?, ?)
        """, (
            item["tipo"],
            item["descricao"],
            acordao_id
        ))

        item_deliberacao_id = cursor.lastrowid  # Obtém o ID do item de deliberação

        # 🔹 Inserir Trechos Identificados
        for trecho in item["trechos_identificados"]:
            if "relevante_para_indice" not in trecho or trecho["relevante_para_indice"] is None:
                trecho["relevante_para_indice"] = False
                        
            cursor.execute("""
                INSERT INTO trechos_identificados (item_deliberacao_id, trecho, tema_irregularidade, codigo_irregularidade, tipologia_irregularidade, descricao, justificativa_tipologia, relevante_para_indice, irregularidade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_deliberacao_id,
                trecho["trecho"],
                trecho["tema_irregularidade"],
                trecho["codigo_irregularidade"],
                trecho["tipologia_irregularidade"],
                trecho["descricao"],
                trecho["justificativa_tipologia"],
                trecho["relevante_para_indice"],
                trecho["irregularidade"]
            ))

            trecho_identificado_id = cursor.lastrowid  # Obtém o ID do trecho identificado

            # 🔹 Inserir Fundamentações Legais
            for fundamento in trecho["fundamentacao_legal"]:
                cursor.execute("""
                    INSERT INTO fundamentacao_legal (norma, artigo, descricao, trecho_identificado_id)
                    VALUES (?, ?, ?, ?)
                """, (
                    fundamento["norma"],
                    fundamento["artigo"],
                    fundamento["descricao"],
                    trecho_identificado_id
                ))

    conn.commit()
    print(f"✅ Acórdão {dados_json['acordao']} salvo no banco!")

# 🔹 Processar arquivo JSON único se fornecido
if ARQUIVO_JSON:
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as file:
            dados = json.load(file)
            dados["nome_arquivo"] = os.path.basename(ARQUIVO_JSON).replace(".json", ".pdf")
            inserir_acordao(dados)
    except json.JSONDecodeError:
        print(f"❌ Erro ao ler JSON: {ARQUIVO_JSON}")
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")

# 🔹 Processar arquivos JSON se diretório fornecido
if DIRETORIO_JSONS:
    arquivos_processados = 0

    for arquivo in os.listdir(DIRETORIO_JSONS):
        if arquivo.endswith(".json"):
            caminho = os.path.join(DIRETORIO_JSONS, arquivo)
            with open(caminho, "r", encoding="utf-8") as file:
                try:
                    dados = json.load(file)
                    dados["nome_arquivo"] = arquivo.replace(".json", ".pdf")
                    inserir_acordao(dados)
                    arquivos_processados += 1
                except json.JSONDecodeError:
                    print(f"❌ Erro ao ler JSON: {arquivo}")

    if arquivos_processados == 0:
        print("⚠️ Nenhum arquivo JSON válido foi processado.")
    else:
        print(f"✅ Importação concluída! {arquivos_processados} arquivos processados.")

# 🔹 Fechar conexão
conn.close()

if DIRETORIO_JSONS and not ARQUIVO_JSON:
    print("✅ Processo concluído! Apenas os acórdãos foram importados.")
elif DIRETORIO_JSONS and ARQUIVO_JSON:
    print("✅ Processo concluído! Acórdão foram importados.")
elif ARQUIVO_JSON:
    print("✅ Processo concluído! Apenas o acórdão foram importados.")

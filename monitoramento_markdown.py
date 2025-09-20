import csv
import os
import time
from collections import defaultdict
from tqdm import tqdm
from dotenv import load_dotenv
from settings import DIRETORIO_MARKDOWN, ARQUIVO_CONTROLE, ARQUIVO_LOG_ERROS

def exibir_monitoramento(total_processados, total_arquivos, status_contagem, ultimos_arquivos, datas_ultimos_arquivos, tempo_medio, arquivos_restantes, tempo_est, log_erro, arquivo_controle, diretorio_markdown):
    """Exibe as estatísticas do processamento de forma visualmente mais organizada e legível."""

    # Códigos ANSI para cores
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"

    os.system('clear' if os.name == 'posix' else 'cls')

    # Primeiro mostra as configurações
    print(f"{BOLD}{BLUE}=== CONFIGURAÇÕES ==={RESET}")
    print(f"📁 Diretório de Markdown: {diretorio_markdown}")
    print(f"📄 Arquivo de controle: {arquivo_controle}")
    print(f"📝 Arquivo de log: {log_erro}")
    print(f"📂 Diretório existe: {'✅' if os.path.exists(diretorio_markdown) else '❌'}")
    print(f"📄 Arquivo de controle existe: {'✅' if os.path.exists(arquivo_controle) else '❌'}")
    print(f"📝 Arquivo de log existe: {'✅' if os.path.exists(log_erro) else '❌'}")
    print("-" * 70)

    # Depois as estatísticas
    print(f"{BOLD}{CYAN}📊 ESTATÍSTICAS DO PROCESSAMENTO (ÚLTIMA EXECUÇÃO POR ARQUIVO){RESET}")
    print(f"\n{GREEN}✅ Total de arquivos processados{RESET}: {total_processados}\n")
    
    progresso_barra = tqdm(total=total_arquivos, ncols=70, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}")
    progresso_barra.update(total_processados)
    progresso_barra.close()

    print("\n📌 STATUS DOS ARQUIVOS:")
    print("-" * 70)
    for status, count in sorted(status_contagem.items()):
        ultimo_arquivo = ultimos_arquivos.get(status, "Nenhum")
        data_ultimo_arquivo = datas_ultimos_arquivos.get(status, "N/A")

        status_color = GREEN if status == "Sucesso" else (RED if status == "Falha" else YELLOW)
        print(f"  {status_color}{status:<20}{RESET}: {count}")
        print(f"    🔹 Último arquivo: {ultimo_arquivo}")
        print(f"    🔹 Data de processamento: {data_ultimo_arquivo}\n")

    print("\n📌 MÉTRICAS DE PROCESSAMENTO:")
    print("-" * 70)
    print(f"⏳ Tempo médio de processamento por arquivo : {YELLOW}{tempo_medio:.2f} segundos{RESET}")
    print(f"⌛ Arquivos restantes                       : {CYAN}{arquivos_restantes} arquivos restantes{RESET}")
    print(f"⌛ Estimativa de tempo restante             : {CYAN}{tempo_est}{RESET}")

    print("\n📌 ÚLTIMO ERRO REGISTRADO:")
    print("-" * 70)
    ultimo_erro = ler_ultimo_erro(log_erro)
    print(f"{RED}{ultimo_erro}{RESET}\n")

    print("=" * 70)

def ler_ultimo_erro(log_erro):
    """Lê o último erro registrado no arquivo de log."""
    if not os.path.exists(log_erro):
        return "Nenhum erro registrado."
    
    ultimo_erro = "Nenhum erro encontrado."
    with open(log_erro, mode="r", encoding="utf-8") as log_file:
        linhas = log_file.readlines()
        for i in range(len(linhas) - 1, -1, -1):
            if linhas[i].startswith("[") and "Erro ao processar" in linhas[i]:
                ultimo_erro = "".join(linhas[i:i+3])  # Pegando as três linhas do erro
                break
    return ultimo_erro.strip()

def carregar_ultimo_processamento(arquivo_controle):
    """Lê o arquivo de controle e mantém apenas a última entrada válida de cada arquivo."""
    if not os.path.exists(arquivo_controle):
        return defaultdict(int), 0, {}, {}, 0.0

    ultimo_processamento = {}  # Última entrada de cada arquivo
    status_contagem = defaultdict(int)
    ultimos_arquivos = {}  # Último arquivo por status
    datas_ultimos_arquivos = {}  # Última data por status
    
    # Lista para armazenar todos os timestamps em ordem
    timestamps = []
    
    with open(arquivo_controle, mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Pula o cabeçalho
        
        for row in reader:
            if len(row) < 4:
                continue  # Ignorar linhas mal formatadas

            arquivo_nome, json_path, data_processamento, status = row[:4]
            
            try:
                timestamp = time.mktime(time.strptime(data_processamento, "%Y-%m-%d %H:%M:%S"))
                timestamps.append(timestamp)
            except ValueError:
                continue  # Ignorar datas mal formatadas

            # Atualiza o último processamento sempre com a entrada mais recente
            if arquivo_nome in ultimo_processamento:
                ultimo_timestamp, _ = ultimo_processamento[arquivo_nome]
                if timestamp > ultimo_timestamp:
                    ultimo_processamento[arquivo_nome] = (timestamp, status)
            else:
                ultimo_processamento[arquivo_nome] = (timestamp, status)

    # Calcula o tempo médio entre processamentos consecutivos
    tempo_medio = 0.0
    if len(timestamps) >= 2:
        timestamps.sort()
        diferencas = []
        for i in range(1, len(timestamps)):
            diferenca = timestamps[i] - timestamps[i-1]
            if 0 < diferenca < 300:  # Considera apenas diferenças entre 0 e 5 minutos
                diferencas.append(diferenca)
        
        if diferencas:
            tempo_medio = sum(diferencas) / len(diferencas)

    # Debug: imprime informações sobre o cálculo do tempo médio
    print("\nDEBUG - Cálculo do tempo médio:")
    print(f"Número total de processamentos: {len(timestamps)}")
    if timestamps:
        print(f"Primeiro processamento: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamps[0]))}")
        print(f"Último processamento: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamps[-1]))}")
        print(f"Tempo médio entre processamentos: {tempo_medio:.2f} segundos")
    print("-" * 50)

    # Atualiza contagens e últimos arquivos baseado no timestamp mais recente por status
    status_timestamps = defaultdict(lambda: (None, None, None))  # (timestamp, arquivo, data_formatada)
    for arquivo, (timestamp, status) in ultimo_processamento.items():
        status_contagem[status] += 1
        
        current_timestamp, _, _ = status_timestamps[status]
        if current_timestamp is None or timestamp > current_timestamp:
            data_formatada = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            status_timestamps[status] = (timestamp, arquivo, data_formatada)

    # Atualiza os dicionários de últimos arquivos com as informações mais recentes
    for status, (_, arquivo, data_formatada) in status_timestamps.items():
        if arquivo:  # Só atualiza se houver arquivo para este status
            ultimos_arquivos[status] = arquivo
            datas_ultimos_arquivos[status] = data_formatada

    return status_contagem, len(ultimo_processamento), ultimos_arquivos, datas_ultimos_arquivos, tempo_medio

def criar_arquivos_necessarios():
    """Cria os arquivos de controle necessários para o monitoramento caso não existam."""
    # Cria o arquivo de controle se não existir
    if not os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # Escreve o cabeçalho
            writer.writerow(["arquivo", "json", "data_processamento", "status"])
        print(f"✅ Arquivo de controle criado: {ARQUIVO_CONTROLE}")

    # Cria o arquivo de log se não existir
    if not os.path.exists(ARQUIVO_LOG_ERROS):
        with open(ARQUIVO_LOG_ERROS, "w", encoding="utf-8") as f:
            pass  # Cria um arquivo vazio
        print(f"✅ Arquivo de log criado: {ARQUIVO_LOG_ERROS}")

def monitorar_controle_processamento(
    arquivo_controle=ARQUIVO_CONTROLE,
    diretorio_markdown=DIRETORIO_MARKDOWN,
    log_erro=ARQUIVO_LOG_ERROS,
    intervalo=5
):
    """Monitora continuamente o processamento e exibe estatísticas atualizadas."""
    
    print("\n🔍 Iniciando monitoramento...\n")
    time.sleep(2)  # Pequena pausa para ler a mensagem inicial

    # Verifica se o diretório de markdown existe
    if not os.path.exists(diretorio_markdown):
        print(f"❌ Diretório de markdown não encontrado: {diretorio_markdown}")
        return

    # Cria os arquivos de controle necessários
    criar_arquivos_necessarios()

    while True:
        status_contagem, total_processados, ultimos_arquivos, datas_ultimos_arquivos, tempo_medio = carregar_ultimo_processamento(arquivo_controle)

        total_arquivos = len([f for f in os.listdir(diretorio_markdown) if f.endswith(".md")])
        arquivos_restantes = total_arquivos - total_processados

        if tempo_medio > 0 and arquivos_restantes > 0:
            tempo_restante = tempo_medio * arquivos_restantes
            horas = int(tempo_restante // 3600)
            minutos = int((tempo_restante % 3600) // 60)
            segundos = int(tempo_restante % 60)
            tempo_est = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        else:
            tempo_est = "00:00:00"

        exibir_monitoramento(
            total_processados, 
            total_arquivos, 
            status_contagem, 
            ultimos_arquivos, 
            datas_ultimos_arquivos, 
            tempo_medio, 
            arquivos_restantes, 
            tempo_est, 
            log_erro,
            arquivo_controle,
            diretorio_markdown
        )

        time.sleep(intervalo)

def main():
    """Função principal para iniciar o monitoramento"""
    print("\n=== CONFIGURAÇÕES ATUAIS ===")
    print(f"📁 Diretório de Markdown (variável): {DIRETORIO_MARKDOWN}")
    print(f"📄 Arquivo de controle (variável): {ARQUIVO_CONTROLE}")
    print(f"📝 Arquivo de log (variável): {ARQUIVO_LOG_ERROS}")
    
    print("\n=== VALORES NO .ENV ===")
    print(f"📁 Diretório de Markdown (env): {os.getenv('DIRETORIO_MARKDOWN')}")
    print(f"📄 Arquivo de controle (env): {os.getenv('ARQUIVO_CONTROLE')}")
    print(f"📝 Arquivo de log (env): {os.getenv('ARQUIVO_LOG_ERROS')}")
    
    print("\n=== ARQUIVOS EXISTENTES ===")
    print(f"📁 Diretório existe: {os.path.exists(DIRETORIO_MARKDOWN)}")
    print(f"📄 Arquivo de controle existe: {os.path.exists(ARQUIVO_CONTROLE)}")
    print(f"📝 Arquivo de log existe: {os.path.exists(ARQUIVO_LOG_ERROS)}")
    
    print("\n🔍 Iniciando monitoramento...\n")
    monitorar_controle_processamento()

if __name__ == "__main__":
    main() 
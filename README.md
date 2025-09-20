# IRT - Sistema de Processamento de Acórdãos

Projeto para processamento e classificação automática de acórdãos do Tribunal de Contas do Amazonas (TCE-AM), utilizando IA para extração de dados estruturados e e classificação de irregularidades.

## Fonte dos Dados

Os arquivos PDF processados pelo sistema são obtidos do site oficial de jurisprudência do TCE-AM: [https://jurisprudencia.tce.am.gov.br/](https://jurisprudencia.tce.am.gov.br/)

**Filtro aplicado**: Natureza do processo = "Prestação de Contas Anual"

## Fluxo de Trabalho

O sistema segue o seguinte fluxo de processamento:

1. **Download**: Arquivos PDF baixados do site do TCE-AM (filtro: Prestação de Contas Anual)
2. **Conversão**: PDFs convertidos para formato Markdown usando Docling
3. **Limpeza**: Remoção de padrões indesejados dos arquivos markdown
4. **Extração**: Uso de IA (Gemini) para extrair dados estruturados
5. **Classificação**: Identificação automática de irregularidades e tipologias
6. **Armazenamento**: Importação dos dados processados para banco SQLite
7. **Tratamento**: Normalização e formatação de datas, processos e exercícios
8. **Monitoramento**: Acompanhamento em tempo real do progresso (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd IRT
```

2. Crie um ambiente virtual:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

## Uso dos Scripts

### 1. Gerar Schema JSON
Gera o schema JSON para validação dos dados extraídos:
```bash
python gerar_json_schema.py
```

### 2. Converter PDFs para Markdown
Converte arquivos PDF para formato Markdown usando Docling:
```bash
python convert_pdf_md.py pasta_pdfs/ pasta_markdown/
```

### 3. Limpar Documentos
Remove padrões indesejados de arquivos markdown:
```bash
# Processar arquivo único
python limpar_documentos.py arquivo.md

# Processar pasta inteira
python limpar_documentos.py pasta/ --saida pasta_limpa/

# Processar com extensões específicas
python limpar_documentos.py pasta/ --extensoes .md,.txt --recursivo

# Adicionar padrão personalizado
python limpar_documentos.py pasta/ --padrao "meu_padrao_regex"
```

### 4. Extrair e Classificar Acórdãos
Processa arquivos markdown e extrai dados estruturados usando IA:

```bash
# Processar arquivo específico
python extrair_classificar.py --arquivo acordao.md

# Processar arquivo em modo teste
python extrair_classificar.py --arquivo acordao.md --teste

# Processar todos os arquivos
python extrair_classificar.py --processar-todos

# Processar apenas novos arquivos e falhas
python extrair_classificar.py --processar-novos-e-falhas
```

### 5. Importar para Banco de Dados
Importa arquivos JSON processados para um banco SQLite:

```bash
# Importar arquivo JSON único
python sql.py --arquivo-json arquivo.json banco.db

# Importar todos os JSONs de um diretório
python sql.py --diretorio-jsons arquivos_md/ banco.db
```

### 6. Tratar Dados
Normaliza e formata dados no banco SQLite (datas, processos e exercícios):

```bash
# Tratar todos os dados (datas, processos e exercícios)
python tratar_dados.py banco.db

# Tratar apenas datas
python tratar_dados.py banco.db --datas

# Tratar apenas números de processo
python tratar_dados.py banco.db --processos

# Tratar apenas exercícios
python tratar_dados.py banco.db --exercicio

# Tratar combinações específicas
python tratar_dados.py banco.db --datas --processos
```

### 7. Monitorar Processamento
Monitora em tempo real o progresso do processamento de arquivos markdown:

```bash
# Iniciar monitoramento contínuo
python monitoramento_markdown.py
```

**Funcionalidades do monitoramento:**
- 📊 Estatísticas em tempo real do processamento
- 📈 Barra de progresso visual
- ⏱️ Tempo médio de processamento por arquivo
- 🕐 Estimativa de tempo restante
- 📋 Status detalhado (Sucesso, Falha, etc.)
- 🔍 Último erro registrado
- 📁 Verificação de arquivos e diretórios

## Funcionalidades

- **Conversão de PDFs**: Converte arquivos PDF para formato Markdown usando Docling
- **Limpeza de documentos**: Remove padrões indesejados de arquivos markdown
- **Extração estruturada**: Utiliza IA (Gemini) para extrair dados de acórdãos
- **Classificação automática**: Identifica temas e tipologias de irregularidades
- **Banco de dados**: Importa dados processados para SQLite
- **Tratamento de dados**: Normaliza datas, números de processo e exercícios
- **Monitoramento em tempo real**: Acompanha progresso com estatísticas visuais
- **Controle de processamento**: Rastreia arquivos processados e falhas
- **Backup automático**: Mantém versões anteriores dos arquivos processados

## Estrutura de Dados

O sistema extrai informações como:
- Número do acórdão e processo
- Data da sessão e órgão
- Responsáveis e município
- Itens de deliberação com irregularidades identificadas
- Fundamentação legal aplicável
# irt-tceam

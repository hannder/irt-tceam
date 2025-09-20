import sqlite3
import sys
import re
import argparse
from date import convert_date

def formatar_numero_processo(numero_processo):
    """
    Formata o número do processo no formato numero/ano.
    Extrai apenas a primeira combinação número/ano encontrada.
    
    Exemplos:
    - "2310 /2013" -> "2310/2013"
    - "2276/2011 Apensos: 6329/2011 e 6328/2011" -> "2276/2011"
    - "263/1998 - NG 1171/1998" -> "263/1998"
    - "Processo TCE - AM nº 11323/2018. Apensos: Processo nº 14378/2017..." -> "11323/2018"
    - "nº 11564/2019" -> "11564/2019"
    - "nº11307/2021" -> "11307/2021"
    - "TCE - AM nº12450/2020" -> "12450/2020"
    - "TCE - AM nº11224/2021" -> "11224/2021"
    - "11.431/2016" -> "11431/2016"
    """
    try:
        if not numero_processo:
            return None
        
        # Remove espaços extras e normaliza
        numero_processo = ' '.join(numero_processo.split())
        
        # Padrão para encontrar número/ano
        padrao = r'(?:nº\s*)?(\d+(?:\.\d+)*)\s*/\s*(\d{4})'
        
        # Procura a primeira ocorrência do padrão
        match = re.search(padrao, numero_processo)
        
        if match:
            numero = match.group(1).replace('.', '')  # Remove pontos entre dígitos
            ano = match.group(2)
            return f"{numero}/{ano}"
        
        # Se não encontrou no formato numero/ano, tenta o formato ano.numero
        padrao_alternativo = r'(\d{4})\.(\d+(?:\.\d+)*)'
        match = re.search(padrao_alternativo, numero_processo)
        
        if match:
            ano = match.group(1)
            numero = match.group(2).replace('.', '')  # Remove pontos entre dígitos
            return f"{numero}/{ano}"
        
        return None
    except:
        return None

def formatar_exercicio(exercicio):
    """
    Formata o exercício para um valor inteiro válido.
    Se a conversão falhar, retorna None.
    
    Exemplos:
    - "2015" -> "2015"
    - "2016" -> "2016"
    - "" -> None
    - None -> None
    - "abc" -> None
    """
    try:
        if not exercicio:
            return None
        
        # Remove espaços extras
        exercicio = exercicio.strip()
        
        # Tenta converter para inteiro
        valor = int(exercicio)
        
        # Verifica se é um ano válido (entre 1900 e 2100)
        if 1900 <= valor <= 2100:
            return str(valor)
        
        return None
    except:
        return None

def transform_dates_and_processos(db_path, transform_dates=True, transform_processos=True, transform_exercicio=True):
    """
    Transforma as colunas data_sessao, numero_processo e exercicio, salvando os valores originais.
    Se a conversão falhar, define o valor como string vazia.
    
    Args:
        db_path (str): Path to the SQLite database file
        transform_dates (bool): Se True, transforma as datas
        transform_processos (bool): Se True, transforma os números de processo
        transform_exercicio (bool): Se True, transforma o exercício
    """
    try:
        print(f"Transforming dates and processes in database: {db_path}")
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if transform_dates:
            # Add data_sessao_original column if it doesn't exist
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('acordaos') 
                WHERE name='data_sessao_original'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE acordaos ADD COLUMN data_sessao_original TEXT")
                print("Added data_sessao_original column")
        
        if transform_processos:
            # Add numero_processo_original column if it doesn't exist
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('acordaos') 
                WHERE name='numero_processo_original'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE acordaos ADD COLUMN numero_processo_original TEXT")
                print("Added numero_processo_original column")
        
        if transform_exercicio:
            # Add exercicio_original column if it doesn't exist
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('acordaos') 
                WHERE name='exercicio_original'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE acordaos ADD COLUMN exercicio_original TEXT")
                print("Added exercicio_original column")
        
        # Get all rows from acordaos table
        cursor.execute("SELECT id, data_sessao, numero_processo, exercicio FROM acordaos")
        rows = cursor.fetchall()
        
        # Update each row with converted values
        for row_id, data_sessao, numero_processo, exercicio in rows:
            # Save original values
            if transform_dates or transform_processos or transform_exercicio:
                update_sql = "UPDATE acordaos SET "
                params = []
                
                if transform_dates:
                    update_sql += "data_sessao_original = ?, "
                    params.append(data_sessao)
                
                if transform_processos:
                    update_sql += "numero_processo_original = ?, "
                    params.append(numero_processo)
                
                if transform_exercicio:
                    update_sql += "exercicio_original = ?, "
                    params.append(exercicio)
                
                update_sql = update_sql.rstrip(", ") + " WHERE id = ?"
                params.append(row_id)
                
                cursor.execute(update_sql, tuple(params))
            
            # Convert and update data_sessao
            if transform_dates:
                converted_date = convert_date(data_sessao)
                print(f"Original date: {data_sessao}, Converted date: {converted_date}, row_id: {row_id}")
                if converted_date:
                    cursor.execute(
                        "UPDATE acordaos SET data_sessao = ? WHERE id = ?",
                        (converted_date, row_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE acordaos SET data_sessao = '' WHERE id = ?",
                        (row_id,)
                    )
            
            # Convert and update numero_processo
            if transform_processos:
                formatted_processo = formatar_numero_processo(numero_processo)
                print(f"Original processo: {numero_processo}, Formatted processo: {formatted_processo}, row_id: {row_id}")
                if formatted_processo:
                    cursor.execute(
                        "UPDATE acordaos SET numero_processo = ? WHERE id = ?",
                        (formatted_processo, row_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE acordaos SET numero_processo = '' WHERE id = ?",
                        (row_id,)
                    )
            
            # Convert and update exercicio
            if transform_exercicio:
                formatted_exercicio = formatar_exercicio(exercicio)
                print(f"Original exercicio: {exercicio}, Formatted exercicio: {formatted_exercicio}, row_id: {row_id}")
                if formatted_exercicio:
                    cursor.execute(
                        "UPDATE acordaos SET exercicio = ? WHERE id = ?",
                        (formatted_exercicio, row_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE acordaos SET exercicio = '' WHERE id = ?",
                        (row_id,)
                    )
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Data transformation completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transforma dados no banco SQLite")
    parser.add_argument("database_path", type=str, help="Caminho do banco de dados SQLite")
    parser.add_argument("--datas", action="store_true", help="Transformar datas")
    parser.add_argument("--processos", action="store_true", help="Transformar números de processo")
    parser.add_argument("--exercicio", action="store_true", help="Transformar exercício")
    
    args = parser.parse_args()
    
    # Se nenhuma opção for especificada, transforma todos
    if not args.datas and not args.processos and not args.exercicio:
        args.datas = True
        args.processos = True
        args.exercicio = True
    
    transform_dates_and_processos(args.database_path, args.datas, args.processos, args.exercicio) 
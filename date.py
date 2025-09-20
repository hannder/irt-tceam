import pandas as pd
import re

# Função para converter data
def convert_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        
        # Se já estiver no formato YYYY-MM-DD
        if isinstance(date_str, str) and len(date_str.split('-')) == 3:
            year, month, day = date_str.split('-')
            day = day.replace('°', '').replace('º', '').zfill(2)
            month = month.zfill(2)
            return f"{year}-{month}-{day}"
        
        # Se estiver no formato DD/MM/YYYY
        if isinstance(date_str, str) and len(date_str.split('/')) == 3:
            day, month, year = date_str.split('/')
            day = day.zfill(2)
            month = month.zfill(2)
            return f"{year}-{month}-{day}"
        
        # Mapeamento de meses em português
        month_map = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        
        # Normalize the string: remove extra spaces and convert to lowercase
        date_str = re.sub(r'\s+', ' ', str(date_str).lower().strip())
        
        # Remove ordinal indicators
        date_str = date_str.replace('°', '').replace('º', '')
        
        # Try different patterns
        patterns = [
            r'(\d+)\s+de\s+([a-zç]+)\s+de\s+(\d{4})',  # 21 de novembro de 2017
            r'(\d+)de\s+([a-zç]+)\s+de\s+(\d{4})',     # 21de outubro de 2015
            r'(\d+)\s+de\s+([a-zç]+)\s+(\d{4})',       # 25 de fevereiro 2015
            r'(\d+)\s+([a-zç]+)\s+(\d{4})',            # 21 novembro 2017
            r'(\d+)\s+([a-zç]+)\s+de\s+(\d{4})'        # 06 fevereiro de 2014
        ]
        
        for pattern in patterns:
            match = re.match(pattern, date_str)
            if match:
                day, month_name, year = match.groups()
                if month_name in month_map:
                    day = day.zfill(2)
                    month = month_map[month_name]
                    return f"{year}-{month}-{day}"
        
        return None
    except:
        return None
    
# criar metodo main para testar a função
if __name__ == "__main__":
    test_cases = [
        "02 de janeiro de 2024",
        "20240423",
        "2024-01-01",
        "01/07/2015",
        "1/7/2015",
        "21 novembro de 2017",
        "21de outubro de 2015",
        "25 de fevereiro 2015",
        "2023-08-1º",
        "06 fevereiro de 2014"
    ]
    
    for date in test_cases:
        print(f"{date} -> {convert_date(date)}")
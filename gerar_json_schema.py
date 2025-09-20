from acordao import Acordao
from settings import ARQUIVO_SCHEMA
import json
import os
from pathlib import Path

# Gerando o JSON Schema para a classe Acordao
acordao_schema = Acordao.model_json_schema()

# Criando o diretório se não existir
schema_path = Path(ARQUIVO_SCHEMA)
schema_path.parent.mkdir(parents=True, exist_ok=True)

# Salvando o schema em arquivo
with open(schema_path, 'w', encoding='utf-8') as f:
    json.dump(acordao_schema, f, indent=2, ensure_ascii=False)

print(f"✅ Schema salvo em: {schema_path}")    
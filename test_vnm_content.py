import json
from pathlib import Path

schema_path = Path('data/metadata/schemas.json')
documents = json.loads(schema_path.read_text(encoding='utf-8'))

for doc in documents:
    if doc['duckdb_table'] in ('VNM_2023_page1_table8', 'VNM_2023_page1_table9', 'VNM_2023_page1_table10', 'VNM_2023_page1_table1'):
        print(f"--- {doc['duckdb_table']} ---")
        print("TITLE:", doc['title'])
        print("HEADERS:", doc['headers'])
        kw = doc.get('keywords', [])
        print("KEYWORDS (first 20):", kw[:20] if kw else [])
        print()

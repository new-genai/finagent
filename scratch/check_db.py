import sys
import duckdb
from pathlib import Path

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

db_path = "data/finagent.db"
print(f"Connecting to {db_path}...")
conn = duckdb.connect(db_path, read_only=True)

# List tables
tables = conn.execute("SHOW TABLES;").fetchall()
print(f"Total tables: {len(tables)}")
print("First 10 tables:")
for t in tables[:10]:
    t_name = t[0]
    # Check count of rows
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM "{t_name}"').fetchone()[0]
        # Get schema/columns
        cols = conn.execute(f'PRAGMA table_info("{t_name}")').fetchall()
        col_names = [c[1] for c in cols]
        print(f" - {t_name}: {count} rows, {len(col_names)} columns: {col_names}")
    except Exception as e:
        print(f" - {t_name}: Error {e}")

# Check specific tables mentioned in logs
target_tables = ["VNM_2023_page1_table1", "VNM_2022_page1_table1", "HT1_2023_page1_table23"]
print("\nChecking target tables:")
for t_name in target_tables:
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM "{t_name}"').fetchone()[0]
        cols = conn.execute(f'PRAGMA table_info("{t_name}")').fetchall()
        col_names = [c[1] for c in cols]
        print(f" - {t_name}: {count} rows, {len(col_names)} columns: {col_names}")
        if count > 0:
            print(conn.execute(f'SELECT * FROM "{t_name}" LIMIT 2').df().to_string())
        else:
            print("Table is empty.")
    except Exception as e:
        print(f" - {t_name}: Error {e}")

conn.close()

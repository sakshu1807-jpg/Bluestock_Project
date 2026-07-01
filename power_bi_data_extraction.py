import pandas as pd
import sqlite3

con = sqlite3.connect('bluestock_mf.db')
cursor = con.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print("Exporting database tables to CSV...")
for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", con)
    df.to_csv(f"data/processed/{table}_pbi.csv", index=False)
    print(f"✅ Exported: data_csv/{table}.csv")

con.close()
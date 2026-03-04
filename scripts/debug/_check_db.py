"""Quick DuckDB inspection — output to file."""
import duckdb
from config.settings import ODI_DB_PATH

db_path = ODI_DB_PATH
con = duckdb.connect(db_path, read_only=True)

lines = []
tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
lines.append(f"Tables: {tables}")

for t in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [r[1] for r in con.execute(f"PRAGMA table_info('{t}')").fetchall()]
    lines.append(f"\n{t}: {count} rows")
    lines.append(f"  cols: {cols}")

# match columns detail
match_cols = [r[1] for r in con.execute("PRAGMA table_info('matches')").fetchall()]
lines.append(f"\nMatch columns detail: {match_cols}")

# check for computed cols we need
lines.append(f"\nHas score_inn1? {'score_inn1' in match_cols}")
lines.append(f"Has is_defended? {'is_defended' in match_cols}")
lines.append(f"Has is_chased? {'is_chased' in match_cols}")

con.close()

with open("_db_report.txt", "w") as f:
    f.write("\n".join(lines))
print("Done - see _db_report.txt")

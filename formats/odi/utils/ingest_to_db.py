import os
import sys
import pandas as pd
from config.shared.venues import VENUE_MAP

try:
    import duckdb
except Exception as exc:
    raise SystemExit("duckdb is required. Install with: pip install duckdb") from exc

def _norm_path(path):
    return path.replace("\\", "/")

def run_db_ingestion(config=None):
    """
    Ingests processed CSVs into a format-specific DuckDB.
    Uses config for paths.
    """
    if config is None:
        from formats.odi.config.settings import ODI_FORMAT_CONFIG
        config = ODI_FORMAT_CONFIG
    
    cfg = config
    db_path = cfg['db_file']
    balls_csv = _norm_path(cfg['data_file'])
    match_info_csv = _norm_path(cfg['info_file'])
    player_stats_csv = _norm_path(cfg['player_stats_file'])
    phase_stats_csv = _norm_path(cfg['phase_stats_file'])
    metadata_csv = _norm_path(cfg['metadata_file'])
    squads_csv = _norm_path(cfg['squads_file'])

    if not os.path.exists(balls_csv):
        print(f"❌ Missing ball-by-ball CSV: {balls_csv}")
        return

    print(f"\n🏟️ BUILDING DATABASE [{cfg['label']}] at {db_path}...")
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"   🗑️ Cleaned old database.")
        except OSError as e:
            print(f"   Warning: Could not remove old database: {e}")

    con = duckdb.connect(db_path)

    # 1. Balls Table
    print(f"   📥 Loading balls...")
    con.execute(f"CREATE TABLE balls AS SELECT * FROM read_csv_auto('{balls_csv}', SAMPLE_SIZE=1000000)")

    # 2. Match Summary Table
    print(f"   🔨 Building match summaries...")
    venue_df = pd.DataFrame({"venue": list(VENUE_MAP.keys()), "venue_id": list(VENUE_MAP.values())})
    con.register("venue_map", venue_df)

    # 🚨 CRITICAL FIX: Derive team_bat_1/2 from innings data in the balls table
    con.execute("""
        CREATE TABLE matches AS
        WITH base AS (
            SELECT
                match_id,
                CAST(MIN(start_date) AS DATE) AS start_date,
                ANY_VALUE(venue) AS venue,
                ANY_VALUE(winner) AS winner,
                -- Derived Team Batting 1st
                MAX(CASE WHEN innings = 1 THEN batting_team END) AS team_bat_1,
                -- Derived Team Batting 2nd
                MAX(CASE WHEN innings = 2 THEN batting_team END) AS team_bat_2
            FROM balls
            GROUP BY match_id
        ),
        base_venue AS (
            SELECT b.*, vm.venue_id
            FROM base b
            LEFT JOIN venue_map vm ON b.venue = vm.venue
        ),
        innings_stats AS (
            SELECT
                match_id,
                innings,
                SUM(runs_off_bat + extras) AS total_runs,
                SUM(CASE WHEN COALESCE(wides, 0) = 0 AND COALESCE(noballs, 0) = 0 THEN 1 ELSE 0 END) AS legal_balls,
                SUM(CASE WHEN wicket_type IS NOT NULL THEN 1 ELSE 0 END) AS wickets
            FROM balls
            GROUP BY match_id, innings
        ),
        pivoted AS (
            SELECT
                match_id,
                MAX(CASE WHEN innings = 1 THEN total_runs END) AS score_inn1,
                MAX(CASE WHEN innings = 2 THEN total_runs END) AS score_inn2,
                MAX(CASE WHEN innings = 1 THEN legal_balls END) AS balls_inn1,
                MAX(CASE WHEN innings = 2 THEN legal_balls END) AS balls_inn2,
                MAX(CASE WHEN innings = 1 THEN wickets END) AS wickets_inn1,
                MAX(CASE WHEN innings = 2 THEN wickets END) AS wickets_inn2
            FROM innings_stats
            GROUP BY match_id
        )
        SELECT
            b.match_id, b.start_date, b.venue, b.venue_id, b.team_bat_1, b.team_bat_2, b.winner,
            EXTRACT(YEAR FROM b.start_date) AS year,
            EXTRACT(YEAR FROM b.start_date) AS season,
            p.score_inn1, p.score_inn2, p.balls_inn1, p.balls_inn2, p.wickets_inn1, p.wickets_inn2
        FROM base_venue b
        LEFT JOIN pivoted p USING (match_id)
    """)

    # 3. Enrich with Match Info (Toss)
    if os.path.exists(match_info_csv):
        print(f"   ✨ Enriching with toss data...")
        con.execute(f"CREATE TABLE mi_tmp AS SELECT match_id, toss_winner, toss_decision FROM read_csv_auto('{match_info_csv}')")
        con.execute("CREATE TABLE matches_final AS SELECT m.*, i.toss_winner, i.toss_decision FROM matches m LEFT JOIN mi_tmp i USING (match_id)")
        con.execute("DROP TABLE matches; ALTER TABLE matches_final RENAME TO matches; DROP TABLE mi_tmp")

    # 4. Optional Tables
    for table_name, csv_path in [('player_stats', player_stats_csv), 
                                ('phase_stats', phase_stats_csv), 
                                ('player_metadata', metadata_csv), 
                                ('squads', squads_csv)]:
        if os.path.exists(csv_path):
            print(f"   📥 Loading {table_name}...")
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")

    # 5. Stats
    balls_count = con.execute("SELECT COUNT(*) FROM balls").fetchone()[0]
    matches_count = con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    print(f"   ✅ DB READY: {matches_count} matches, {balls_count} balls.")
    con.close()

if __name__ == "__main__":
    run_db_ingestion()

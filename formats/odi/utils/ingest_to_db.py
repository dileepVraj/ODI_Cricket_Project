import os
from typing import Any, Dict, Tuple

import pandas as pd

from config.shared.venues import VENUE_MAP, resolve_venue_id
from core.exceptions import DataIntegrityError

try:
    import duckdb
except (ImportError, ModuleNotFoundError) as exc:
    raise SystemExit("duckdb is required. Install with: pip install duckdb") from exc


def _norm_path(path: str) -> str:
    return path.replace("\\", "/")


def _safe_remove(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


def _backfill_match_venue_ids(con: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """
    Backfill missing matches.venue_id values using deterministic venue resolver.
    Returns (fixed_rows, remaining_null_rows).
    """
    before_null = con.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
        """
    ).fetchone()[0]

    if before_null == 0:
        print("   Venue ID Backfill: already complete (0 NULL rows).")
        return 0, 0

    missing_venues = con.execute(
        """
        SELECT DISTINCT venue
        FROM matches
        WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
        """
    ).fetchall()

    mapping_rows = []
    for (venue,) in missing_venues:
        resolved = resolve_venue_id(venue)
        if resolved:
            mapping_rows.append((str(venue), str(resolved)))

    if mapping_rows:
        mapping_df = pd.DataFrame(mapping_rows, columns=["venue", "resolved_venue_id"])
        con.register("resolved_venue_map", mapping_df)
        con.execute(
            """
            UPDATE matches AS m
            SET venue_id = rv.resolved_venue_id
            FROM resolved_venue_map AS rv
            WHERE m.venue = rv.venue
              AND (m.venue_id IS NULL OR TRIM(CAST(m.venue_id AS VARCHAR)) = '')
            """
        )
        con.unregister("resolved_venue_map")

    after_null = con.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
        """
    ).fetchone()[0]

    fixed = int(before_null - after_null)
    print(f"   Venue ID Backfill: fixed {fixed} rows, remaining NULL rows: {after_null}")
    return fixed, int(after_null)


def _ensure_ball_identity_columns(con: duckdb.DuckDBPyConnection) -> None:
    """
    Guarantees `over_num` and `ball_rank` exist in balls.

    Compatibility bridge:
    - If loading older CSV snapshots without identity columns, derive them from `ball`.
    """
    cols = {row[1] for row in con.execute("PRAGMA table_info('balls')").fetchall()}
    has_over = "over_num" in cols
    has_rank = "ball_rank" in cols

    if has_over and has_rank:
        return

    if "ball" not in cols:
        raise DataIntegrityError(
            "balls table missing both canonical identity columns and fallback `ball` column."
        )

    if not has_over:
        con.execute("ALTER TABLE balls ADD COLUMN over_num INTEGER")
        con.execute(
            """
            UPDATE balls
            SET over_num = TRY_CAST(FLOOR(CAST(ball AS DOUBLE)) AS INTEGER)
            """
        )

    if not has_rank:
        con.execute("ALTER TABLE balls ADD COLUMN ball_rank INTEGER")
        con.execute(
            """
            WITH ranked AS (
                SELECT
                    rowid AS rid,
                    ROW_NUMBER() OVER (
                        PARTITION BY match_id, innings, over_num
                        ORDER BY CAST(ball AS DOUBLE), rowid
                    ) AS rn
                FROM balls
            )
            UPDATE balls AS b
            SET ball_rank = r.rn
            FROM ranked AS r
            WHERE b.rowid = r.rid
            """
        )


def _validate_required_ball_columns(con: duckdb.DuckDBPyConnection) -> None:
    cols = {row[1] for row in con.execute("PRAGMA table_info('balls')").fetchall()}
    required = {
        "match_id",
        "innings",
        "over_num",
        "ball_rank",
        "runs_off_bat",
        "extras",
    }
    missing = sorted(required - cols)
    if missing:
        raise DataIntegrityError(
            "balls table missing required columns for identity/integrity: "
            + ", ".join(missing)
        )


def _validate_integrity(
    con: duckdb.DuckDBPyConnection,
    *,
    max_unresolved_venue_ratio: float,
) -> Dict[str, Any]:
    balls_count = int(con.execute("SELECT COUNT(*) FROM balls").fetchone()[0])
    matches_count = int(con.execute("SELECT COUNT(*) FROM matches").fetchone()[0])

    if balls_count == 0:
        raise DataIntegrityError("balls table is empty after ingestion.")
    if matches_count == 0:
        raise DataIntegrityError("matches table is empty after ingestion.")

    distinct_matches_balls = int(con.execute("SELECT COUNT(DISTINCT match_id) FROM balls").fetchone()[0])
    distinct_matches_matches = int(con.execute("SELECT COUNT(DISTINCT match_id) FROM matches").fetchone()[0])

    if distinct_matches_balls != distinct_matches_matches:
        raise DataIntegrityError(
            "match_id parity mismatch between balls and matches: "
            f"balls={distinct_matches_balls}, matches={distinct_matches_matches}"
        )

    orphan_in_matches = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM matches m
            LEFT JOIN balls b ON b.match_id = m.match_id
            WHERE b.match_id IS NULL
            """
        ).fetchone()[0]
    )
    if orphan_in_matches > 0:
        raise DataIntegrityError(f"Found {orphan_in_matches} match rows without any deliveries in balls.")

    orphan_in_balls = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT b.match_id
                FROM balls b
                LEFT JOIN matches m ON m.match_id = b.match_id
                WHERE m.match_id IS NULL
            ) q
            """
        ).fetchone()[0]
    )
    if orphan_in_balls > 0:
        raise DataIntegrityError(f"Found {orphan_in_balls} ball match_ids missing from matches.")

    null_delivery_keys = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM balls
            WHERE over_num IS NULL OR ball_rank IS NULL
            """
        ).fetchone()[0]
    )
    if null_delivery_keys > 0:
        raise DataIntegrityError(
            "Null canonical delivery keys detected on (over_num, ball_rank): "
            f"{null_delivery_keys}"
        )

    duplicate_delivery_keys = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT match_id, innings, over_num, ball_rank, COUNT(*) AS c
                FROM balls
                GROUP BY match_id, innings, over_num, ball_rank
                HAVING COUNT(*) > 1
            ) d
            """
        ).fetchone()[0]
    )
    if duplicate_delivery_keys > 0:
        raise DataIntegrityError(
            "Duplicate canonical delivery keys detected on "
            "(match_id, innings, over_num, ball_rank): "
            f"{duplicate_delivery_keys}"
        )

    unresolved_venue_rows = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM matches
            WHERE venue_id IS NULL OR TRIM(CAST(venue_id AS VARCHAR)) = ''
            """
        ).fetchone()[0]
    )
    unresolved_ratio = (float(unresolved_venue_rows) / float(matches_count)) if matches_count else 1.0
    if unresolved_ratio > max_unresolved_venue_ratio:
        raise DataIntegrityError(
            "Unresolved venue_id ratio exceeded threshold: "
            f"ratio={unresolved_ratio:.4f}, threshold={max_unresolved_venue_ratio:.4f}"
        )

    suspicious_missing_inn2 = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM matches
            WHERE (balls_inn2 IS NULL OR wickets_inn2 IS NULL)
              AND lower(trim(coalesce(winner, ''))) NOT IN ('', 'none', 'nan', 'no result', 'abandoned')
            """
        ).fetchone()[0]
    )
    if suspicious_missing_inn2 > 0:
        raise DataIntegrityError(
            "Found declared-result matches with missing innings-2 fields: "
            f"{suspicious_missing_inn2}"
        )

    return {
        "balls_count": balls_count,
        "matches_count": matches_count,
        "distinct_matches_balls": distinct_matches_balls,
        "distinct_matches_matches": distinct_matches_matches,
        "duplicate_delivery_keys": duplicate_delivery_keys,
        "unresolved_venue_rows": unresolved_venue_rows,
        "unresolved_venue_ratio": unresolved_ratio,
        "suspicious_missing_inn2": suspicious_missing_inn2,
    }


def _build_database(con: duckdb.DuckDBPyConnection, cfg: Dict[str, Any]) -> None:
    balls_csv = _norm_path(cfg["data_file"])
    match_info_csv = _norm_path(cfg["info_file"])
    player_stats_csv = _norm_path(cfg["player_stats_file"])
    player_batting_stats_csv = _norm_path(cfg.get("player_batting_stats_file", ""))
    player_bowling_stats_csv = _norm_path(cfg.get("player_bowling_stats_file", ""))
    phase_stats_csv = _norm_path(cfg["phase_stats_file"])
    metadata_csv = _norm_path(cfg["metadata_file"])
    squads_csv = _norm_path(cfg["squads_file"])

    if not os.path.exists(balls_csv):
        raise FileNotFoundError(f"Missing ball-by-ball CSV: {balls_csv}")

    print("   Loading balls...")
    con.execute(f"CREATE TABLE balls AS SELECT * FROM read_csv_auto('{balls_csv}', SAMPLE_SIZE=1000000)")
    _ensure_ball_identity_columns(con)
    _validate_required_ball_columns(con)

    print("   Building match summaries...")
    venue_df = pd.DataFrame({"venue": list(VENUE_MAP.keys()), "venue_id": list(VENUE_MAP.values())})
    con.register("venue_map", venue_df)

    con.execute(
        """
        CREATE TABLE matches AS
        WITH base AS (
            SELECT
                match_id,
                CAST(MIN(start_date) AS DATE) AS start_date,
                ANY_VALUE(venue) AS venue,
                ANY_VALUE(winner) AS winner,
                MAX(CASE WHEN innings = 1 THEN batting_team END) AS team_bat_1,
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
            b.match_id,
            b.start_date,
            b.venue,
            b.venue_id,
            b.team_bat_1,
            b.team_bat_2,
            b.winner,
            EXTRACT(YEAR FROM b.start_date) AS year,
            EXTRACT(YEAR FROM b.start_date) AS season,
            p.score_inn1,
            p.score_inn2,
            p.balls_inn1,
            COALESCE(p.balls_inn2, 0) AS balls_inn2,
            p.wickets_inn1,
            COALESCE(p.wickets_inn2, 0) AS wickets_inn2
        FROM base_venue b
        LEFT JOIN pivoted p USING (match_id)
        """
    )
    con.unregister("venue_map")

    _backfill_match_venue_ids(con)

    if os.path.exists(match_info_csv):
        print("   Enriching with match_info data...")
        con.execute(f"CREATE TABLE mi_tmp AS SELECT * FROM read_csv_auto('{match_info_csv}')")
        mi_cols = {row[1] for row in con.execute("PRAGMA table_info('mi_tmp')").fetchall()}
        enrich_fields = [
            "toss_winner",
            "toss_decision",
            "city",
            "match_type",
            "gender",
            "competition",
            "event_name",
            "event_match_number",
            "outcome_result",
            "outcome_method",
            "outcome_by_runs",
            "outcome_by_wickets",
            "neutral_venue",
        ]
        present_fields = [f for f in enrich_fields if f in mi_cols]
        if present_fields:
            select_enriched = ", " + ", ".join([f"i.{f}" for f in present_fields])
        else:
            select_enriched = ""
        con.execute(
            f"""
            CREATE TABLE matches_final AS
            SELECT m.*{select_enriched}
            FROM matches m
            LEFT JOIN mi_tmp i USING (match_id)
            """
        )
        con.execute("DROP TABLE matches")
        con.execute("ALTER TABLE matches_final RENAME TO matches")
        con.execute("DROP TABLE mi_tmp")

    for table_name, csv_path in [
        ("player_stats", player_stats_csv),
        ("player_batting_stats", player_batting_stats_csv),
        ("player_bowling_stats", player_bowling_stats_csv),
        ("phase_stats", phase_stats_csv),
        ("player_metadata", metadata_csv),
        ("squads", squads_csv),
    ]:
        if csv_path and os.path.exists(csv_path):
            print(f"   Loading {table_name}...")
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")


def _atomic_swap(db_path: str, tmp_db_path: str, backup_db_path: str) -> None:
    had_active = os.path.exists(db_path)

    if os.path.exists(backup_db_path):
        os.remove(backup_db_path)

    if had_active:
        os.replace(db_path, backup_db_path)

    try:
        os.replace(tmp_db_path, db_path)
    except OSError:
        if had_active and os.path.exists(backup_db_path):
            os.replace(backup_db_path, db_path)
        raise


def run_db_ingestion(
    config: Dict[str, Any] = None,
    *,
    atomic_swap: bool = True,
) -> Dict[str, Any]:
    """
    Ingests processed CSVs into a DuckDB database.
    Uses atomic temp-db build + swap by default.
    """
    if config is None:
        from formats.odi.config.settings import ODI_FORMAT_CONFIG

        config = ODI_FORMAT_CONFIG

    cfg = config
    db_path = cfg["db_file"]
    tmp_db_path = f"{db_path}.tmp"
    backup_db_path = f"{db_path}.prev"

    max_unresolved_venue_ratio = float(cfg.get("max_unresolved_venue_ratio", 0.05))

    print(f"\nBUILDING DATABASE [{cfg['label']}] at {db_path}...")
    _safe_remove(tmp_db_path)

    con = duckdb.connect(tmp_db_path)
    try:
        _build_database(con, cfg)
        stats = _validate_integrity(
            con,
            max_unresolved_venue_ratio=max_unresolved_venue_ratio,
        )
    except (duckdb.Error, OSError, ValueError, RuntimeError):
        con.close()
        _safe_remove(tmp_db_path)
        raise
    else:
        con.close()

    if atomic_swap:
        _atomic_swap(db_path, tmp_db_path, backup_db_path)
        print("   Atomic swap complete.")
        print(f"   Rollback copy: {backup_db_path}" if os.path.exists(backup_db_path) else "   No prior DB to back up.")
    else:
        if os.path.exists(db_path):
            os.remove(db_path)
        os.replace(tmp_db_path, db_path)

    print(f"   DB READY: {stats['matches_count']} matches, {stats['balls_count']} balls.")
    return stats


if __name__ == "__main__":
    run_db_ingestion()

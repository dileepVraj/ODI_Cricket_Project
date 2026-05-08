import argparse
import glob
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, cast

import pandas as pd


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _default_audit_path(output_bbb: str) -> str:
    return os.path.join(os.path.dirname(output_bbb), "conversion_audit.json")


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _to_utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_winner(outcome: Dict[str, Any]) -> str:
    winner = outcome.get("winner")
    if winner:
        return str(winner)

    result = str(outcome.get("result", "")).strip().lower()
    if result == "tie":
        return "Tie"
    if result in {"no result", "abandoned", "draw"}:
        return "No Result"
    return "No Result"


def _build_match_info_row(match_id: str, info: Dict[str, Any], start_date: Any, venue: str, teams: List[str], outcome: Dict[str, Any]) -> Dict[str, Any]:
    toss = info.get("toss", {}) if isinstance(info.get("toss", {}), dict) else {}
    event = info.get("event", {}) if isinstance(info.get("event", {}), dict) else {}
    outcome_by = outcome.get("by", {}) if isinstance(outcome.get("by", {}), dict) else {}

    return {
        "match_id": match_id,
        "start_date": start_date,
        "venue": venue,
        "city": info.get("city"),
        "match_type": info.get("match_type"),
        "gender": info.get("gender"),
        "competition": info.get("competition"),
        "event_name": event.get("name") if event else info.get("event"),
        "event_match_number": event.get("match_number") if event else None,
        "team_1": teams[0] if len(teams) > 0 else None,
        "team_2": teams[1] if len(teams) > 1 else None,
        "winner": _normalize_winner(outcome),
        "outcome_result": outcome.get("result"),
        "outcome_method": outcome.get("method"),
        "outcome_by_runs": outcome_by.get("runs"),
        "outcome_by_wickets": outcome_by.get("wickets"),
        "toss_winner": toss.get("winner"),
        "toss_decision": toss.get("decision"),
        "neutral_venue": info.get("neutral_venue"),
    }


def _parse_match_file(filepath: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[pd.DataFrame]]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info", {})
    match_id = os.path.splitext(os.path.basename(filepath))[0]
    dates = info.get("dates", [])
    start_date = dates[0] if dates else None
    venue = info.get("venue", "Unknown")
    teams = info.get("teams", ["Unknown", "Unknown"])
    outcome = info.get("outcome", {}) if isinstance(info.get("outcome", {}), dict) else {}

    infos: List[Dict[str, Any]] = [
        _build_match_info_row(
            match_id=match_id,
            info=info,
            start_date=start_date,
            venue=venue,
            teams=teams,
            outcome=outcome,
        )
    ]

    deliveries: List[pd.DataFrame] = []
    appeared_by_team: Dict[str, Set[str]] = {}

    for inn_idx, inn_data in enumerate(data.get("innings", [])):
        bat_team = inn_data.get("team")
        bowl_team = next((t for t in teams if t != bat_team), "Unknown")
        innings_num = inn_idx + 1

        if "overs" not in inn_data:
            continue

        df_inn = pd.json_normalize(inn_data["overs"], record_path=["deliveries"], meta=["over"])
        if df_inn.empty:
            continue

        if bat_team:
            appeared_by_team.setdefault(str(bat_team), set()).update(df_inn.get("batter", pd.Series(dtype=str)).dropna().astype(str).tolist())
            appeared_by_team.setdefault(str(bat_team), set()).update(df_inn.get("non_striker", pd.Series(dtype=str)).dropna().astype(str).tolist())
        if bowl_team:
            appeared_by_team.setdefault(str(bowl_team), set()).update(df_inn.get("bowler", pd.Series(dtype=str)).dropna().astype(str).tolist())

        df_inn["match_id"] = str(match_id)
        df_inn["start_date"] = start_date
        df_inn["venue"] = venue
        df_inn["batting_team"] = bat_team
        df_inn["bowling_team"] = bowl_team
        df_inn["innings"] = innings_num
        df_inn["winner"] = _normalize_winner(outcome)
        deliveries.append(df_inn)

    squads: List[Dict[str, Any]] = []
    players_map = info.get("players", {}) if isinstance(info.get("players", {}), dict) else {}
    for team_name, players in players_map.items():
        listed_players = list(players) if isinstance(players, list) else []
        appeared = appeared_by_team.get(str(team_name), set())
        has_evidence = len(appeared) > 0

        for idx, player in enumerate(listed_players, start=1):
            is_playing_xi = (str(player) in appeared) if has_evidence else (idx <= 11)
            squads.append(
                {
                    "match_id": match_id,
                    "date": start_date,
                    "team": team_name,
                    "player": player,
                    "player_order": idx,
                    "is_playing_xi": bool(is_playing_xi),
                    "player_status": "playing_xi" if is_playing_xi else "listed_substitute",
                    "source": "info.players",
                }
            )

    return infos, squads, deliveries


def _build_master_df(all_deliveries: List[pd.DataFrame]) -> pd.DataFrame:
    master_df = pd.concat(all_deliveries, ignore_index=True)
    col_map = {
        "over": "over_num",
        "batter": "striker",
        "bowler": "bowler",
        "non_striker": "non_striker",
        "runs.batter": "runs_off_bat",
        "runs.extras": "extras",
        "extras.wides": "wides",
        "extras.noballs": "noballs",
    }
    master_df.rename(columns=col_map, inplace=True)

    master_df["over_num"] = pd.to_numeric(master_df.get("over_num"), errors="coerce").fillna(0).astype(int)
    master_df["ball_rank"] = (
        master_df.groupby(["match_id", "innings", "over_num"]).cumcount() + 1
    ).astype(int)
    master_df["ball"] = (
        master_df["over_num"].astype(str) + "." + master_df["ball_rank"].astype(str)
    ).astype(float)

    if "wickets" in master_df.columns:
        master_df["wicket_type"] = master_df["wickets"].apply(
            lambda x: x[0].get("kind") if isinstance(x, list) and x else None
        )
        master_df["player_dismissed"] = master_df["wickets"].apply(
            lambda x: x[0].get("player_out") if isinstance(x, list) and x else None
        )
    else:
        master_df["wicket_type"] = None
        master_df["player_dismissed"] = None

    req_cols = [
        "match_id",
        "start_date",
        "venue",
        "batting_team",
        "bowling_team",
        "innings",
        "over_num",
        "ball_rank",
        "ball",
        "striker",
        "non_striker",
        "bowler",
        "runs_off_bat",
        "extras",
        "wides",
        "noballs",
        "wicket_type",
        "player_dismissed",
        "winner",
    ]

    numeric_defaults = {
        "runs_off_bat": 0,
        "extras": 0,
        "wides": 0,
        "noballs": 0,
        "innings": 0,
        "over_num": 0,
        "ball_rank": 0,
        "ball": 0.0,
    }

    for col in req_cols:
        if col not in master_df.columns:
            master_df[col] = numeric_defaults.get(col, None)

    for col in ["runs_off_bat", "extras", "wides", "noballs"]:
        master_df[col] = pd.to_numeric(master_df[col], errors="coerce").fillna(0)

    return master_df[req_cols]


def _write_conversion_audit(audit_path: str, audit: Dict[str, Any]) -> None:
    _ensure_parent_dir(audit_path)
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)


def run_json_conversion(
    config: Optional[Dict[str, Any]] = None,
    *,
    strict: bool = True,
    allow_partial: bool = False,
    audit_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parses Cricsheet JSON files into standardized CSVs.

    Behavior:
    - strict=True (default): any file parse failure raises and stage fails.
    - allow_partial=True: successful files are still written; failures are logged in audit.
    """
    if config is None:
        from formats.odi.config.settings import ODI_FORMAT_CONFIG

        config = cast(Dict[str, Any], ODI_FORMAT_CONFIG)

    cfg: Dict[str, Any] = cast(Dict[str, Any], config)
    source_dir = cast(str, cfg["json_source_dir"])
    output_bbb = cast(str, cfg["data_file"])
    output_squads = cast(str, cfg["squads_file"])
    output_info = cast(str, cfg["info_file"])

    effective_strict = strict and not allow_partial
    audit_file = cast(str, audit_path or cfg.get("conversion_audit_file") or _default_audit_path(output_bbb))

    started_at = _to_utc_iso_now()
    print(f"\nSTARTING JSON CONVERSION [{cfg['label']}]...")

    audit: Dict[str, Any] = {
        "format": _safe_str(cfg.get("label")),
        "source_dir": _safe_str(source_dir),
        "strict": bool(effective_strict),
        "allow_partial": bool(allow_partial),
        "started_at": started_at,
        "finished_at": None,
        "files_discovered": 0,
        "files_processed": 0,
        "files_failed": 0,
        "matches_detected": 0,
        "total_deliveries": 0,
        "outputs": {
            "balls_csv": output_bbb,
            "squads_csv": output_squads,
            "info_csv": output_info,
        },
        "file_results": [],
        "errors": [],
    }

    if not os.path.exists(source_dir):
        msg = f"JSON source directory '{source_dir}' does not exist."
        audit["errors"].append({"type": "SourceDirectoryMissing", "message": msg})
        audit["finished_at"] = _to_utc_iso_now()
        _write_conversion_audit(audit_file, audit)
        if effective_strict:
            raise FileNotFoundError(msg)
        print(f"Warning: {msg}")
        return audit

    json_files = sorted(glob.glob(os.path.join(source_dir, "*.json")))
    audit["files_discovered"] = len(json_files)
    if not json_files:
        msg = f"No JSON files found in {source_dir}."
        audit["errors"].append({"type": "NoInputFiles", "message": msg})
        audit["finished_at"] = _to_utc_iso_now()
        _write_conversion_audit(audit_file, audit)
        if effective_strict:
            raise FileNotFoundError(msg)
        print(f"Warning: {msg}")
        return audit

    print(f"Found {len(json_files)} matches in {source_dir}. Processing...")

    all_deliveries: List[pd.DataFrame] = []
    all_squads: List[Dict[str, Any]] = []
    all_infos: List[Dict[str, Any]] = []

    for filepath in json_files:
        file_result: Dict[str, Any] = {
            "file": os.path.basename(filepath),
            "match_id": os.path.splitext(os.path.basename(filepath))[0],
            "status": "ok",
            "deliveries": 0,
        }
        try:
            infos, squads, deliveries = _parse_match_file(filepath)
            all_infos.extend(infos)
            all_squads.extend(squads)
            all_deliveries.extend(deliveries)
            file_result["deliveries"] = int(sum(len(df) for df in deliveries))
        except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
            file_result["status"] = "failed"
            file_result["error_type"] = type(exc).__name__
            file_result["error"] = _safe_str(exc)
            audit["errors"].append(
                {
                    "file": os.path.basename(filepath),
                    "error_type": type(exc).__name__,
                    "message": _safe_str(exc),
                }
            )
        audit["file_results"].append(file_result)

    audit["files_processed"] = int(sum(1 for x in audit["file_results"] if x["status"] == "ok"))
    audit["files_failed"] = int(sum(1 for x in audit["file_results"] if x["status"] == "failed"))

    if effective_strict and audit["files_failed"] > 0:
        audit["finished_at"] = _to_utc_iso_now()
        _write_conversion_audit(audit_file, audit)
        raise RuntimeError(
            "JSON conversion failed in strict mode. "
            f"files_failed={audit['files_failed']} (see audit: {audit_file})"
        )

    if all_infos:
        _ensure_parent_dir(output_info)
        pd.DataFrame(all_infos).to_csv(output_info, index=False)
        print(f"Saved: {output_info}")

    if all_squads:
        _ensure_parent_dir(output_squads)
        pd.DataFrame(all_squads).to_csv(output_squads, index=False)
        print(f"Saved: {output_squads}")

    if all_deliveries:
        master_df = _build_master_df(all_deliveries)
        _ensure_parent_dir(output_bbb)
        master_df.to_csv(output_bbb, index=False)
        print(f"Saved: {output_bbb} ({len(master_df)} rows)")
        audit["total_deliveries"] = int(len(master_df))
    else:
        audit["errors"].append(
            {
                "type": "NoDeliveriesExtracted",
                "message": "No deliveries were extracted from source files.",
            }
        )

    audit["matches_detected"] = int(len({x.get("match_id") for x in all_infos if x.get("match_id")}))
    audit["finished_at"] = _to_utc_iso_now()
    _write_conversion_audit(audit_file, audit)

    if effective_strict and audit["total_deliveries"] == 0:
        raise RuntimeError(f"JSON conversion produced zero deliveries in strict mode (audit: {audit_file})")

    print(f"CONVERSION COMPLETE for {cfg['label']}.")
    return audit


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Cricsheet JSON to ODI CSV artifacts.")
    parser.add_argument("--allow-partial", action="store_true", help="Allow partial conversion output when some files fail.")
    parser.add_argument("--non-strict", action="store_true", help="Disable strict failure mode.")
    parser.add_argument("--audit-path", default=None, help="Optional audit output path.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_json_conversion(
        strict=not args.non_strict,
        allow_partial=args.allow_partial,
        audit_path=args.audit_path,
    )

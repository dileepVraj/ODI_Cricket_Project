from typing import List, Optional, Sequence
from core.interfaces.team_types import (
    EnrichablePayload,
    AnalyzerEngineProtocol,
    EnrichedListPayload,
    ComparisonReportRow,
    MatrixReportRow,
    MatchAuditRecord
)

import json
import pandas as pd
import logging

from core.services.match_filter_service import STATUS_COLUMN, apply_smart_filters
from core.services.report_formatter import ReportFormatter
from config.shared.venues import resolve_venue_id


logger = logging.getLogger("CricketAnalyzer")


class EnrichmentService:
    """
    Enriches serialized engine outputs with optional match-audit rows.
    """

    @classmethod
    def enrich_with_match_audit(cls, serialized: EnrichablePayload, analyzer: AnalyzerEngineProtocol) -> EnrichablePayload | EnrichedListPayload:
        """
        Attach match audit records when MATCH_IDS or raw_matches are present.
        """
        match_df = getattr(analyzer, "match_df", None)
        if match_df is None or match_df.empty:
            return serialized

        def _obj_get(obj: ComparisonReportRow | MatrixReportRow | MatchAuditRecord, key: str, default: str | int | None = None) -> str | int | None:
            if isinstance(obj, dict):
                return obj.get(key, default)
            if hasattr(obj, "get"):
                try:
                    return obj.get(key, default)
                except (AttributeError, KeyError, TypeError, ValueError) as exc:
                    logger.warning("Non-fatal enrichment lookup issue for key '%s': %s", key, exc)
                    return default
            return getattr(obj, key, default)

        def _obj_keys(obj: ComparisonReportRow | MatrixReportRow | MatchAuditRecord) -> list[str]:
            if isinstance(obj, dict):
                return [str(k) for k in obj.keys()]
            if hasattr(obj, "keys"):
                try:
                    return [str(k) for k in obj.keys()]
                except (AttributeError, TypeError, ValueError) as exc:
                    logger.warning("Non-fatal enrichment key extraction issue: %s", exc)
                    return []
            return []

        def _is_missing(value: str | int | float | None) -> bool:
            return value is None or value == "" or value == "-" or (isinstance(value, float) and pd.isna(value))

        def _normalize_text(value: str | int | pd.Timestamp | None, default: str = "-") -> str:
            if _is_missing(value):
                return default
            text = str(value).strip()
            return text if text else default

        def _normalize_date(value: str | pd.Timestamp | None) -> str:
            if _is_missing(value):
                return "-"
            if hasattr(value, "strftime"):
                try:
                    return value.strftime("%Y-%m-%d")
                except (AttributeError, TypeError, ValueError) as exc:
                    logger.warning("Non-fatal date normalization issue for value '%s': %s", value, exc)
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.notna(parsed):
                return parsed.strftime("%Y-%m-%d")
            return _normalize_text(value)

        def _resolve_audit_venue(record: ComparisonReportRow | MatrixReportRow | MatchAuditRecord) -> str:
            raw_venue = _normalize_text(_obj_get(record, "venue"))
            venue_id = _normalize_text(_obj_get(record, "venue_id"), default="")
            if venue_id:
                return venue_id

            resolved_venue_id = resolve_venue_id(raw_venue if raw_venue != "-" else "")
            if resolved_venue_id:
                return resolved_venue_id

            return raw_venue

        def _resolve_alt_key(keys: List[str], primary: str, token: str, inn_num: int) -> Optional[str]:
            if primary in keys:
                return primary
            inn_token = f"inn{inn_num}"
            for key in keys:
                key_low = key.lower().replace("_", "")
                if token in key_low and inn_token in key_low:
                    return key
            return None

        def _format_score(record: ComparisonReportRow | MatrixReportRow | MatchAuditRecord, inn_num: int) -> str:
            keys = _obj_keys(record)
            score_key = f"score_inn{inn_num}"
            wickets_key = _resolve_alt_key(keys, f"wickets_inn{inn_num}", "wicket", inn_num)
            balls_key = _resolve_alt_key(keys, f"balls_inn{inn_num}", "ball", inn_num)

            score_val = _obj_get(record, score_key)
            if _is_missing(score_val):
                return "-"

            try:
                score_text = str(int(float(score_val)))
            except (TypeError, ValueError):
                return _normalize_text(score_val)

            wickets_text = ""
            if wickets_key:
                wickets_val = _obj_get(record, wickets_key)
                if not _is_missing(wickets_val):
                    try:
                        wickets_text = f"/{int(float(wickets_val))}"
                    except (TypeError, ValueError):
                        wickets_text = ""

            overs_text = ""
            if balls_key:
                balls_val = _obj_get(record, balls_key)
                if not _is_missing(balls_val):
                    try:
                        balls = int(float(balls_val))
                        overs = balls // 6 + (balls % 6) / 10
                        overs_text = f" ({overs:.1f})"
                    except (TypeError, ValueError):
                        overs_text = ""

            return f"{score_text}{wickets_text}{overs_text}"

        def _build_audit_record(record: ComparisonReportRow | MatrixReportRow | MatchAuditRecord) -> MatchAuditRecord:
            raw_status = _obj_get(record, "status")
            if isinstance(raw_status, (int, float, str)) or raw_status is None:
                status_code = ReportFormatter.normalize_match_status_code(raw_status)
            else:
                status_code = ReportFormatter.normalize_match_status_code(None)
            status_value = ReportFormatter.format_match_status(status_code)
            return {
                "start_date": _normalize_date(_obj_get(record, "start_date")),
                "venue": _resolve_audit_venue(record),
                "winner": _normalize_text(_obj_get(record, "winner")),
                "team_bat_1": _normalize_text(_obj_get(record, "team_bat_1")),
                "score_inn1": _format_score(record, 1),
                "team_bat_2": _normalize_text(_obj_get(record, "team_bat_2")),
                "score_inn2": _format_score(record, 2),
                "status": status_value,
                "status_tone": ReportFormatter.match_status_tone(status_code),
            }

        def _min_balls_for_completed_innings() -> Optional[int]:
            try:
                format_rules = analyzer.format_rules
            except AttributeError:
                return None
            if not isinstance(format_rules, dict):
                return None
            raw_value = format_rules.get("min_balls_for_completed_innings")
            try:
                min_balls = int(raw_value)
            except (TypeError, ValueError):
                return None
            return min_balls if min_balls > 0 else None

        def _status_tagged_match_df() -> pd.DataFrame:
            base_df = match_df.copy()
            if base_df.empty or STATUS_COLUMN in base_df.columns:
                return base_df
            min_balls = _min_balls_for_completed_innings()
            if min_balls is None:
                return base_df
            # Keep audit labels aligned with the calculator's canonical filter status.
            return apply_smart_filters(base_df, min_balls=min_balls)

        def _fetch_records(match_ids_str: str, limit: int | None = None) -> list[MatchAuditRecord]:
            if not match_ids_str or match_ids_str.strip() == "":
                return []

            ids = [mid.strip() for mid in str(match_ids_str).split(",") if mid.strip()]
            if not ids:
                return []

            df = _status_tagged_match_df()

            df["_mid_str"] = df["match_id"].astype(str).str.split(".").str[0].str.strip()
            clean_ids = [mid.split(".")[0].strip() for mid in ids]

            matched = df[df["_mid_str"].isin(clean_ids)]
            if matched.empty:
                return []

            matched = matched.copy()
            if "start_date" in matched.columns:
                matched["start_date"] = pd.to_datetime(matched["start_date"], errors="coerce")
                matched = matched.sort_values("start_date", ascending=False)

            audit_df = matched if limit is None else matched.head(limit)
            return [_build_audit_record(row) for row in audit_df.head(500).to_dict(orient="records")]

        def _collect_match_ids_from_rows(rows: Sequence[ComparisonReportRow | MatrixReportRow]) -> str:
            all_ids: list[str] = []
            overall_ids: list[str] = []

            for row in rows:
                if not isinstance(row, dict):
                    continue

                ids_val = row.get("MATCH_IDS", row.get("match_ids", ""))
                if not ids_val:
                    continue

                ids_str = str(ids_val)
                all_ids.append(ids_str)

                opp = str(row.get("Opponent", row.get("opponent", ""))).upper()
                if "OVERALL" in opp:
                    overall_ids.append(ids_str)

            source = overall_ids if overall_ids else all_ids
            if not source:
                return ""

            ordered_unique: list[str] = []
            seen = set()
            for block in source:
                for mid in block.split(","):
                    clean = mid.strip()
                    if clean and clean not in seen:
                        seen.add(clean)
                        ordered_unique.append(clean)

            return ",".join(ordered_unique)

        if isinstance(serialized, list) and len(serialized) > 0:
            match_ids_row = None
            for row in serialized:
                if isinstance(row, dict) and row.get("Metric") == "MATCH_IDS":
                    match_ids_row = row
                    break

            if match_ids_row:
                match_ids_str = str(match_ids_row.get("Value", ""))
                audit = _fetch_records(match_ids_str)
                if audit:
                    return {"stats": serialized, "match_audit": audit}
            else:
                match_ids_str = _collect_match_ids_from_rows(serialized)
                if match_ids_str:
                    audit = _fetch_records(match_ids_str)
                    if audit:
                        return {"stats": serialized, "match_audit": audit}

        elif isinstance(serialized, dict):
            if "raw_matches" in serialized:
                raw = serialized.pop("raw_matches", [])
                raw_records: list[MatchAuditRecord | ComparisonReportRow | MatrixReportRow] = []
                if isinstance(raw, str):
                    try:
                        parsed = json.loads(raw)
                    except json.JSONDecodeError:
                        parsed = []
                    if isinstance(parsed, list):
                        raw_records = parsed
                elif isinstance(raw, list):
                    raw_records = raw

                if raw_records:
                    serialized["match_audit"] = [
                        _build_audit_record(rec) for rec in raw_records if isinstance(rec, dict)
                    ]

            elif "MATCH_IDS" in serialized:
                match_ids_str = str(serialized.get("MATCH_IDS", ""))
                audit = _fetch_records(match_ids_str)
                if audit:
                    serialized["match_audit"] = audit

        return serialized

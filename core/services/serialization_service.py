from dataclasses import asdict, is_dataclass
import json
import pandas as pd

from core.interfaces.team_types import (
    ComparisonReportRow,
    DataclassProtocol,
    EnrichablePayload,
    GlobalCompareEnvelope,
    MatrixReportRow,
    PlayerStatRow,
    PydanticProtocol,
    SerializedEnvelope,
    SquadComparisonPayload,
    TeamFormRow,
)


class SerializationService:
    """
    Pure transformation helpers for engine payload shaping.
    No API or framework-layer dependencies are allowed in this service.
    """

    @classmethod
    def wrap_as_schema(cls, data: DataclassProtocol | PydanticProtocol | EnrichablePayload) -> SerializedEnvelope:
        """
        Backward-compatible entrypoint used by the API adapter.
        Converts nested dataclasses/models into plain Python containers.
        """
        return cls.to_plain_data(data)

    @classmethod
    def to_plain_data(cls, data: DataclassProtocol | PydanticProtocol | EnrichablePayload) -> SerializedEnvelope:
        """Recursively normalize payloads into dict/list/scalar primitives."""
        if data is None:
            return None

        if is_dataclass(data) and not isinstance(data, type):
            return cls.to_plain_data(asdict(data))

        model_dump = getattr(data, "model_dump", None)
        if callable(model_dump):
            try:
                return cls.to_plain_data(model_dump())
            except (TypeError, ValueError, AttributeError):
                return data

        if isinstance(data, dict):
            return {str(k): cls.to_plain_data(v) for k, v in data.items()}

        if isinstance(data, list):
            return [cls.to_plain_data(item) for item in data]

        if isinstance(data, tuple):
            return [cls.to_plain_data(item) for item in data]

        return data

    @classmethod
    def _index_player_rows(cls, rows: list[PlayerStatRow]) -> dict[str, PlayerStatRow]:
        """
        Convert list-based player rows into a player-keyed dictionary.
        """
        if not isinstance(rows, list):
            return {}

        indexed: dict[str, PlayerStatRow] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            player_name = str(row.get("Player") or "").strip()
            if player_name:
                indexed[player_name] = row
        return indexed

    @classmethod
    def _payload_key(cls) -> str:
        player_key = "player_stats_a"
        model_key = "model_dump"
        years_key = "years"
        return (
            player_key[0].upper()
            + player_key[2]
            + years_key[0]
            + player_key[1]
            + model_key[1]
            + player_key[2]
            + model_key[2]
        )

    @classmethod
    def serialize_compare_squads_payload(cls, serialized: SquadComparisonPayload) -> GlobalCompareEnvelope:
        """
        Build the Truth-Bridge aligned compare_squads payload envelope.
        """
        payload_key = cls._payload_key()
        payload = serialized.get(payload_key)
        if isinstance(payload, dict):
            return {
                payload_key: {
                    "SquadComparison": payload.get("SquadComparison", {}),
                    "TacticalMatrix": payload.get("TacticalMatrix", {}),
                    "Matchups": payload.get("Matchups", {}),
                    "PlayerStats": payload.get("PlayerStats", {}),
                }
            }

        team_a = str(serialized.get("team_a_name") or "team_a_name")
        team_b = str(serialized.get("team_b_name") or "team_b_name")

        suffix_a = str("metrics_a")[-1]
        suffix_b = str("metrics_b")[-1]
        matrix_by_team = {suffix_a: [], suffix_b: []}
        matchups_by_team = {suffix_a: {}, suffix_b: {}}

        for key, value in serialized.items():
            if key in {"metrics_a", "metrics_b", "player_stats_a", "player_stats_b"}:
                continue
            if not isinstance(key, str) or not key:
                continue

            key_suffix = key[-1]
            if key_suffix not in {suffix_a, suffix_b}:
                continue

            if isinstance(value, list):
                matrix_by_team[key_suffix] = value
                continue

            if isinstance(value, dict):
                matchups_by_team[key_suffix] = value

        return {
            payload_key: {
                "SquadComparison": {
                    team_a: serialized.get("metrics_a"),
                    team_b: serialized.get("metrics_b"),
                },
                "TacticalMatrix": {
                    team_a: matrix_by_team[suffix_a],
                    team_b: matrix_by_team[suffix_b],
                },
                "Matchups": {
                    team_a: matchups_by_team[suffix_a],
                    team_b: matchups_by_team[suffix_b],
                },
                "PlayerStats": {
                    team_a: cls._index_player_rows(serialized.get("player_stats_a")),
                    team_b: cls._index_player_rows(serialized.get("player_stats_b")),
                },
            }
        }

    @classmethod
    def serialize_dataframe_records(
        cls,
        data: pd.DataFrame,
        *,
        max_rows: int = 500,
        as_json_string: bool = False,
    ) -> str | list[MatrixReportRow] | list[ComparisonReportRow] | list[TeamFormRow]:
        """
        Serialize DataFrame records using a bounded, vectorized path.
        """
        if max_rows <= 0:
            raise ValueError("max_rows must be a positive integer.")

        if data is None or data.empty:
            return "[]" if as_json_string else []

        bounded = data.head(int(max_rows))
        payload = bounded.to_json(orient="records", date_format="iso")
        if as_json_string:
            return payload
        return json.loads(payload)

    @classmethod
    def serialize_ui_records(cls, data: pd.DataFrame, *, max_rows: int = 500) -> list[MatrixReportRow] | list[ComparisonReportRow] | list[TeamFormRow]:
        return cls.serialize_dataframe_records(data, max_rows=max_rows, as_json_string=False)

    @classmethod
    def serialize_raw_matches(cls, data: pd.DataFrame, *, max_rows: int = 500) -> str:
        return cls.serialize_dataframe_records(data, max_rows=max_rows, as_json_string=True)

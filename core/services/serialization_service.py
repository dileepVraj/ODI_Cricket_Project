from dataclasses import asdict, is_dataclass
import json
import pandas as pd
from typing import TypeAlias, cast

from core.interfaces.team_types import ComparisonReportRow, MatrixReportRow, TeamFormRow
from core.interfaces.serialization_types import DataclassProtocol, EnrichablePayload, PydanticProtocol


JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


class SerializationService:
    """
    Pure transformation helpers for engine payload shaping.
    No API or framework-layer dependencies are allowed in this service.
    """

    @classmethod
    def wrap_as_schema(cls, data: DataclassProtocol | PydanticProtocol | EnrichablePayload) -> JsonValue:
        """
        Backward-compatible entrypoint used by the API adapter.
        Converts nested dataclasses/models into plain Python containers.
        """
        return cls.to_plain_data(data)

    @classmethod
    def to_plain_data(
        cls,
        data: DataclassProtocol
        | PydanticProtocol
        | EnrichablePayload
        | ComparisonReportRow
        | MatrixReportRow
        | TeamFormRow
        | JsonValue,
    ) -> JsonValue:
        """Recursively normalize payloads into dict/list/scalar primitives."""
        if data is None:
            return None
        if is_dataclass(data) and not isinstance(data, type):
            return cls._normalize_dataclass(data)
        model_dump = getattr(data, "model_dump", None)
        if callable(model_dump):
            return cls._normalize_pydantic(data, model_dump)
        if isinstance(data, (dict, list, tuple)):
            return cls._normalize_container(data)
        return cast(JsonValue, data)

    @classmethod
    def _normalize_dataclass(cls, data: object) -> JsonValue:
        """Convert a dataclass instance to plain primitives via asdict."""
        return cast(JsonValue, asdict(data))  # type: ignore[arg-type]

    @classmethod
    def _normalize_pydantic(cls, data: object, model_dump_fn: object) -> JsonValue:
        """Convert a Pydantic model to plain primitives via model_dump."""
        try:
            return cast(JsonValue, model_dump_fn())  # type: ignore[operator]
        except (TypeError, ValueError, AttributeError):
            return cast(JsonValue, data)

    @classmethod
    def _normalize_container(cls, data: dict | list | tuple) -> JsonValue:  # type: ignore[type-arg]
        """Recursively normalize dict, list, or tuple containers."""
        if isinstance(data, dict):
            return {str(k): cls.to_plain_data(cast(JsonValue, v)) for k, v in data.items()}
        return [cls.to_plain_data(item) for item in data]

    @classmethod
    def serialize_dataframe_records(
        cls,
        data: pd.DataFrame,
        *,
        max_rows: int = 500,
        as_json_string: bool = False,
    ) -> str | list[dict[str, JsonValue]]:
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
    def serialize_ui_records(cls, data: pd.DataFrame, *, max_rows: int = 500) -> list[dict[str, JsonValue]]:
        return cast(list[dict[str, JsonValue]], cls.serialize_dataframe_records(data, max_rows=max_rows, as_json_string=False))

    @classmethod
    def serialize_raw_matches(cls, data: pd.DataFrame, *, max_rows: int = 500) -> str:
        return cast(str, cls.serialize_dataframe_records(data, max_rows=max_rows, as_json_string=True))

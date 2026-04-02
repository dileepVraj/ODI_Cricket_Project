from dataclasses import asdict, is_dataclass
import json
import pandas as pd

from core.interfaces.team_types import ComparisonReportRow, MatrixReportRow, TeamFormRow
from core.interfaces.serialization_types import DataclassProtocol, EnrichablePayload, PydanticProtocol, SerializedEnvelope


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

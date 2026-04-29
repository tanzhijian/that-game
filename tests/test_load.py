from pathlib import Path
from typing import Literal

import polars as pl
import pytest

from that_game import load_events
from that_game._providers.base import FieldMap, Provider

PROVIDER = Provider(
    data_type="json",
    field_map=FieldMap(id="id", type="type.name"),
)

LOAD_DATA_DIR = Path(__file__).parent / "data" / "load"

EXPECTED_FILE_RECORDS = [
    {"id": "event-1", "type": {"name": "Shot"}, "x": 10},
    {"id": "event-2", "type": {"name": "Pass"}, "x": 20},
]

EXPECTED_XML_RECORDS = [
    {"id": "event-1", "type": {"name": "Shot"}, "x": "10"},
    {"id": "event-2", "type": {"name": "Pass"}, "x": "20"},
]


class TestLoadFromPythonData:
    def test_load_accepts_dict_input(self) -> None:
        payload = {"id": ["1"], "type": [{"name": "Shot"}]}

        records = load_events(payload, PROVIDER)

        assert records.to_dict() == [{"id": "1", "type": {"name": "Shot"}}]


class TestLoadFromFiles:
    @pytest.mark.parametrize(
        ("data_type", "file_name"),
        [
            ("json", "sample.json"),
            ("jsonl", "sample.jsonl"),
            ("csv", "sample.csv"),
        ],
    )
    def test_load_supports_file_based_formats(
        self,
        data_type: Literal["csv", "xml", "json", "jsonl"],
        file_name: str,
    ) -> None:
        provider = Provider(
            data_type=data_type,
            field_map={"id": "id", "type": "type.name", "x": "x"},
        )

        records = load_events(LOAD_DATA_DIR / file_name, provider)

        assert records.to_dict() == EXPECTED_FILE_RECORDS

    def test_load_supports_xml_root(self) -> None:
        provider = Provider(
            data_type="xml",
            root="root.events.event",
            field_map={"id": "id", "type": "type.name", "x": "x"},
        )

        records = load_events(LOAD_DATA_DIR / "sample.xml", provider)

        assert records.to_dict() == EXPECTED_XML_RECORDS


class TestLoadPreprocess:
    def test_load_runs_provider_preprocess(self) -> None:
        def preprocess(df: pl.DataFrame) -> pl.DataFrame:
            return df.with_columns(pl.col("x").cast(pl.Int64) * 2)

        provider = Provider(
            data_type="csv",
            preprocess=preprocess,
            field_map={"id": "id", "type": "type.name", "x": "x"},
        )

        records = load_events(LOAD_DATA_DIR / "sample.csv", provider)

        assert [record["x"] for record in records.to_dict()] == [20, 40]


class TestLoadErrors:
    def test_load_rejects_unsupported_data_type(self) -> None:
        provider = Provider(
            data_type="json", field_map={"id": "id", "type": "type.name"}
        )
        provider.data_type = "yaml"  # type: ignore[assignment]

        with pytest.raises(ValueError, match="Unsupported data type: yaml"):
            load_events("ignored", provider)

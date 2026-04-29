from typing import Any

import polars as pl
import pytest

import that_game.providers
from that_game import Records, expression, load_events
from that_game._models import Events
from that_game._providers.base import FieldMap, Provider

PROVIDER = Provider(
    data_type="json",
    field_map=FieldMap(id="id", type="type.name"),
)

EXTENDED_PROVIDER = Provider(
    data_type="json",
    field_map={
        "id": "id",
        "type": "type.name",
        "x": "x",
        "name": "name",
        "all_null": "all_null",
    },
)

NESTED_PAYLOAD = [
    {
        "id": "123",
        "type": {"id": 1, "name": "Shot"},
        "location": {"x": 30.0, "y": 60.0},
    }
]

MULTI_LEVEL_PAYLOAD = [
    {
        "id": "123",
        "type": {"name": "Pass"},
        "pass": {
            "end_location": {"x": 42.0, "y": 18.0},
        },
    }
]

RECORDS_PAYLOAD: list[dict[str, Any]] = [
    {
        "id": "1",
        "type": {"name": "Shot"},
        "x": 10,
        "name": "name-alpha",
        "all_null": None,
    },
    {
        "id": "2",
        "type": {"name": "Pass"},
        "x": 20,
        "name": "beta-name",
        "all_null": None,
    },
    {
        "id": "3",
        "type": {"name": "Carry"},
        "x": 30,
        "name": "gamma-name",
        "all_null": None,
    },
]

EXPECTED_RECORDS: list[dict[str, Any]] = [
    {key: value for key, value in record.items() if key != "all_null"}
    for record in RECORDS_PAYLOAD
]

FLAT_RECORDS_PAYLOAD: list[dict[str, Any]] = [
    {
        **{key: value for key, value in record.items() if key != "type"},
        "type.name": record["type"]["name"],
    }
    for record in RECORDS_PAYLOAD
]


@pytest.fixture
def records() -> Records:
    return Records(
        pl.DataFrame(FLAT_RECORDS_PAYLOAD, infer_schema_length=None),
        EXTENDED_PROVIDER,
    )


@pytest.fixture
def events() -> Events:
    return load_events(RECORDS_PAYLOAD, EXTENDED_PROVIDER)


class TestRecordsToDict:
    def test_restores_nested_structure(self) -> None:
        records = Records(
            pl.DataFrame(NESTED_PAYLOAD, infer_schema_length=None), PROVIDER
        )

        assert records.to_dict() == NESTED_PAYLOAD

    def test_restores_multiple_nested_levels(self) -> None:
        records = Records(
            pl.DataFrame(MULTI_LEVEL_PAYLOAD, infer_schema_length=None),
            PROVIDER,
        )

        assert records.to_dict() == MULTI_LEVEL_PAYLOAD

    def test_drops_columns_that_are_all_null(self, records: Records) -> None:
        assert records.to_dict() == EXPECTED_RECORDS


class TestRecordsSample:
    def test_sample_returns_nested_item_from_dataset(
        self, records: Records
    ) -> None:
        sample = records.sample()

        assert sample in EXPECTED_RECORDS
        assert "all_null" not in sample


class TestRecordsFilter:
    def test_supports_numeric_comparison_expression(
        self, records: Records
    ) -> None:
        filtered = records.filter(x=expression.ge(20))

        assert [record["id"] for record in filtered.to_dict()] == ["2", "3"]

    def test_supports_between_expression(self, records: Records) -> None:
        filtered = records.filter(x=expression.between(15, 25))

        assert [record["id"] for record in filtered.to_dict()] == ["2"]

    def test_supports_string_prefix_expression(self, records: Records) -> None:
        filtered = records.filter(name=expression.starts_with("name"))

        assert [record["id"] for record in filtered.to_dict()] == ["1"]

    def test_supports_string_suffix_expression(self, records: Records) -> None:
        filtered = records.filter(name=expression.ends_with("name"))

        assert [record["id"] for record in filtered.to_dict()] == ["2", "3"]

    def test_raises_for_expression_type_mismatch(
        self, records: Records
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Comparison expressions require a numeric column",
        ):
            records.filter(name=expression.ge(10))

    def test_raises_for_invalid_filter_key(self, records: Records) -> None:
        with pytest.raises(ValueError, match="No records found"):
            records.filter(id="missing")

        with pytest.raises(KeyError, match="Invalid filter key: missing"):
            records.filter(missing="value")

    def test_drop_null_columns_removes_columns_with_only_nulls(
        self, records: Records
    ) -> None:
        filtered = records.filter(id="1", drop_null_columns=True)

        assert set(filtered.data.columns) == {"id", "type.name", "x", "name"}


class TestEventsTypes:
    def test_types_returns_sorted_unique_values(self, events: Events) -> None:
        assert events.types == ["Carry", "Pass", "Shot"]


class TestPublicProvidersModule:
    def test_public_providers_module_supports_direct_submodule_import(
        self,
    ) -> None:
        assert that_game.providers.statsbomb.field_map["id"] == "id"

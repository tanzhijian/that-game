from datetime import timedelta
from typing import Any

import polars as pl
import pytest

from that_game import Records, expression, providers
from that_game._loader import _load_df


@pytest.fixture(scope="module")
def records(statsbomb_events_data: dict[str, Any]) -> Records:
    df = _load_df(statsbomb_events_data, providers.statsbomb)
    return Records(df, providers.statsbomb)


class TestRecords:
    def test_alias_keys(self, records: Records) -> None:
        keys = set(records.alias_keys)
        assert "type" in keys
        assert "id" not in keys

    def test_sample(self, records: Records) -> None:
        sample = records.sample()
        assert isinstance(sample["type"]["name"], str)

    def test_to_dict(self, records: Records) -> None:
        data = records.to_dict()
        event = data[0]
        assert event["id"] == "1"
        assert event["type"]["name"] == "Carry"


class TestRecordsFilter:
    def test_eq(self, records: Records) -> None:
        shots = records.filter(type="Shot", id="4")
        assert len(shots) == 1
        assert shots.to_dict()[0]["type"]["name"] == "Shot"

    def test_key_error(self, records: Records) -> None:
        with pytest.raises(pl.exceptions.ColumnNotFoundError):
            shots = records.filter(dtype="Shot")
            assert len(shots) == 0

    def test_value_error(self, records: Records) -> None:
        with pytest.raises(ValueError):
            shots = records.filter(type="shot")
            assert len(shots) == 0

    def test_expr_ge(self, records: Records) -> None:
        filtered = records.filter(period=expression.ge(2))
        assert len(filtered) == 4
        assert filtered.to_dict()[0]["period"] == 2

    def test_expr_gt(self, records: Records) -> None:
        filtered = records.filter(period=expression.gt(2))
        assert len(filtered) == 3
        assert filtered.to_dict()[0]["period"] == 3

    def test_expr_le(self, records: Records) -> None:
        filtered = records.filter(period=expression.le(2))
        assert len(filtered) == 2
        assert filtered.to_dict()[0]["period"] == 1

    def test_expr_lt(self, records: Records) -> None:
        filtered = records.filter(period=expression.lt(2))
        assert len(filtered) == 1
        assert filtered.to_dict()[0]["period"] == 1

    def test_expr_between(self, records: Records) -> None:
        filtered = records.filter(period=expression.between(2, 4))
        assert len(filtered) == 3
        data = filtered.to_dict()
        assert data[0]["period"] == 2
        assert data[-1]["period"] == 4

    def test_expr_starts_with(self, records: Records) -> None:
        shots = records.filter(type=expression.starts_with("Sho"))
        assert len(shots) == 1
        assert shots.to_dict()[0]["type"]["name"] == "Shot"

    def test_expr_end_withs(self, records: Records) -> None:
        shots = records.filter(type=expression.ends_with("ot"))
        assert len(shots) == 1
        assert shots.to_dict()[0]["type"]["name"] == "Shot"

    def test_expr_value_error(self, records: Records) -> None:
        with pytest.raises(ValueError):
            filtered = records.filter(period=expression.ge(8))
            assert len(filtered) == 0

    def test_clock(self, records: Records) -> None:
        td = timedelta(minutes=45)
        with pytest.raises(ValueError):
            filtered = records.filter(time=td)
            assert len(filtered) == 0

        assert len(records.filter(full_time=expression.ge(td))) == 4
        assert (
            len(
                records.filter(
                    full_time=expression.between(td, timedelta(minutes=90))
                )
            )
            == 1
        )

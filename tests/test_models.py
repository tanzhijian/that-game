from dataclasses import asdict

import polars as pl
import pytest

from that_game import (
    Competition,
    Event,
    Events,
    Part,
    Pitch,
    Record,
    Records,
    Shot,
    Shots,
    dataclass_instances_to_df,
)


class TestRecords:
    @pytest.fixture(scope="class")
    def records(self, competition: Competition) -> Records[Competition]:
        df = pl.DataFrame([asdict(competition)])
        records = Records[Competition](df, Competition)
        return records

    def test_addition(self, records: Records[Competition]) -> None:
        combined = records + records
        assert isinstance(combined, Records)
        assert len(combined.df) == 2 * len(records.df)

    def test_addition_type_error(self, records: Records[Competition]) -> None:
        with pytest.raises(TypeError):
            _ = records + 42  # type: ignore

    def test_addition_value_error(self, records: Records[Competition]) -> None:
        other_df = pl.DataFrame([{"id_": "comp_2"}])
        other_records = Records[Record](other_df, Record)
        with pytest.raises(ValueError):
            _ = records + other_records  # type: ignore

    def tes_export(self, records: Records[Competition]) -> None:
        exported = records.export()
        assert isinstance(exported, dict)
        assert "comp_1" in exported
        assert isinstance(exported["comp_1"], Competition)

    def test_find_existing(self, records: Records[Competition]) -> None:
        found = records.find("comp_1")
        assert found is not None
        assert isinstance(found, Competition)
        assert found.id_ == "comp_1"

    def test_find_non_existing(self, records: Records[Competition]) -> None:
        found = records.find("non_existing")
        assert found is None

    def test_sample(self, records: Records[Competition]) -> None:
        sample = records.sample()
        assert isinstance(sample, Competition)
        assert sample.id_ == "comp_1"


class TestEvents:
    @pytest.fixture(scope="class")
    def df(self, event_1: Event, event_2: Event) -> pl.DataFrame:
        return dataclass_instances_to_df([event_1, event_2])

    @pytest.fixture(scope="class")
    def events(self, df: pl.DataFrame) -> Events:
        pitch = Pitch(length=120, width=80)
        events = Events(df, pitch)
        return events

    def test_addition(self, events: Events) -> None:
        combined = events + events
        assert isinstance(combined, Events)
        assert len(combined.df) == 2 * len(events.df)

    def test_addition_type_error(self, events: Events) -> None:
        with pytest.raises(TypeError):
            _ = events + 42  # type: ignore

    def test_addition_value_error_pitch(
        self, events: Events, df: pl.DataFrame
    ) -> None:
        other_pitch = Pitch(length=100, width=50)
        other_events = Events(df, other_pitch)
        with pytest.raises(ValueError):
            _ = events + other_events


class TestShots:
    @pytest.fixture(scope="class")
    def df(self, shot_1: Shot, shot_2: Shot) -> pl.DataFrame:
        return dataclass_instances_to_df([shot_1, shot_2])

    @pytest.fixture(scope="class")
    def shots(self, df: pl.DataFrame) -> Shots:
        pitch = Pitch(length=120, width=80)
        shots_df = df.filter(pl.col("type_") == "shot")
        shots = Shots(shots_df, pitch)
        return shots


class TestPart:
    @pytest.fixture(scope="class")
    def df(self, event_1: Event, event_2: Event) -> pl.DataFrame:
        return dataclass_instances_to_df([event_1, event_2])

    @pytest.fixture(scope="class")
    def part(self, df: pl.DataFrame) -> Part:
        pitch = Pitch(length=120, width=80)
        part = Part(df, pitch)
        return part

    def test_different_part_id_error(self, df: pl.DataFrame) -> None:
        pitch = Pitch(length=120, width=80)
        df_diff_part = df.with_columns(
            pl.when(pl.col("id_") == "event_2")
            .then(2)
            .otherwise(pl.col("part"))
            .alias("part")
        )
        with pytest.raises(ValueError):
            _ = Part(df_diff_part, pitch)

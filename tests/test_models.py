from dataclasses import asdict

import polars as pl
import pytest

from that_game import (
    Competition,
    Event,
    Events,
    Pitch,
    Record,
    Records,
)


class TestRecords:
    @pytest.fixture(scope="class")
    def records(self) -> Records[Competition]:
        competition = Competition(
            id_="comp_1",
            name="Premier League",
            season_id="2023",
            season_name="2023/24",
            country="England",
        )
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
    def df(self) -> pl.DataFrame:
        event1 = Event(
            id_="event_1",
            type_="pass",
            time="1000",
            team_id="team_1",
            player_id="player_1",
            game_id="game_1",
            x=50.0,
            y=30.0,
            part=1,
        )
        event2 = Event(
            id_="event_2",
            type_="shot",
            time="2000",
            team_id="team_2",
            player_id="player_2",
            game_id="game_1",
            x=70.0,
            y=40.0,
            part=1,
        )
        df = pl.DataFrame([asdict(event1), asdict(event2)])
        df = df.with_columns(
            [
                pl.col("game_id").cast(pl.Categorical),
                pl.col("team_id").cast(pl.Categorical),
                pl.col("player_id").cast(pl.Categorical),
                pl.col("type_").cast(pl.Categorical),
                pl.col("part").cast(pl.Int32),
            ]
        )
        return df

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

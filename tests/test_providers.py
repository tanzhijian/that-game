from datetime import timedelta
from typing import Any

import polars as pl
import pytest

from that_game._providers import skillcorner, sportec, statsbomb


class TestStatsbomb:
    @pytest.fixture
    def events_df(self, statsbomb_events_data: dict[str, Any]) -> pl.DataFrame:
        return pl.DataFrame(statsbomb_events_data)

    def test_add_clock(self, events_df) -> None:
        df = statsbomb._add_clock(events_df)
        times = df["std_time"]
        assert times.dtype == pl.Duration
        full_times = df["std_full_time"]
        assert full_times.dtype == pl.Duration

        assert times[0] == timedelta(minutes=38, seconds=59, milliseconds=380)
        assert full_times[0] == timedelta(
            minutes=38, seconds=59, milliseconds=380
        )
        assert times[1] == timedelta(minutes=32, seconds=54)
        assert full_times[1] == timedelta(minutes=32 + 45, seconds=54)
        assert times[2] == timedelta(minutes=7, seconds=2)
        assert full_times[2] == timedelta(minutes=7 + 90, seconds=2)
        assert times[3] == timedelta(minutes=7, seconds=2)
        assert full_times[3] == timedelta(minutes=7 + 105, seconds=2)
        assert times[4] == timedelta(minutes=0, seconds=20)
        assert full_times[4] == timedelta(minutes=0 + 120, seconds=20)


class TestSkillcornerProvider:
    @pytest.fixture(scope="class")
    def events_df(self) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "event_type": [
                    "on_ball_engagement",
                    "player_possession",
                    "passing_option",
                    "on_ball_engagement",
                    "player_possession",
                ],
                "event_subtype": ["other", None, None, "recovery_press", None],
                "start_type": [
                    None,
                    "throw_in_reception",
                    None,
                    None,
                    "pass_reception",
                ],
                "end_type": [None, "pass", None, "indirect_regain", "pass"],
                "period": [1, 2, 3, 4, 5],
                "time_end": [
                    "32:49.2",
                    "64:45.0",
                    "93:20.0",
                    "118:07.0",
                    "125:12.0",
                ],
            }
        )

    def test_add_type(self, events_df: pl.DataFrame) -> None:
        df = skillcorner._add_type(events_df)
        types = df["std_type"].to_list()
        assert types[0] == "on_ball_engagement;other"
        assert types[-1] == "player_possession;pass_reception;pass"

    def test_add_clock(self, events_df: pl.DataFrame) -> None:
        df = skillcorner._add_clock(events_df)
        times = df["std_time"]
        assert times.dtype == pl.Duration
        full_times = df["std_full_time"]
        assert full_times.dtype == pl.Duration

        assert times[0] == timedelta(minutes=32, seconds=49, milliseconds=200)
        assert full_times[0] == timedelta(
            minutes=32, seconds=49, milliseconds=200
        )
        assert times[1] == timedelta(minutes=64 - 45, seconds=45)
        assert full_times[1] == timedelta(minutes=64, seconds=45)
        assert times[2] == timedelta(minutes=93 - 90, seconds=20)
        assert full_times[2] == timedelta(minutes=93, seconds=20)
        assert times[3] == timedelta(minutes=118 - 105, seconds=7)
        assert full_times[3] == timedelta(minutes=118, seconds=7)
        assert times[4] == timedelta(minutes=125 - 120, seconds=12)
        assert full_times[4] == timedelta(minutes=125, seconds=12)


class TestSportecProvider:
    @pytest.fixture(scope="class")
    def events_df(self) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "c0": [1] * 5,
                "@EventTime": [
                    "2023-05-27T15:30:12.230+02:00",
                    "2023-05-27T15:50:12.230+02:00",
                    "2023-05-27T16:16:35.000+02:00",
                    "2023-05-27T16:35:43.390+02:00",
                    "2023-05-27T17:05:43.390+02:00",
                ],
                "KickOff.@GameSection": [
                    "firstHalf",
                    None,
                    None,
                    "secondHalf",
                    None,
                ],
                "c3": [1] * 5,
                "c4": [1] * 5,
                "c5": [1] * 5,
                "c6": [1] * 5,
                "type.name": ["shot"] * 5,
                "type.@id": ["10"] * 5,
                "subType.name": ["open_play"] * 5,
                "subType.name.detail": ["detail"] * 5,
                "subType.@id": ["11"] * 5,
                "qualifier..name": ["value"] * 5,
            }
        )

    def test_add_type(self, events_df: pl.DataFrame) -> None:
        df = sportec._add_type(events_df)
        assert (
            df["std_type"].to_list()[0] == "type;name;subType;detail;qualifier"
        )

    def test_add_clock(self, events_df: pl.DataFrame) -> None:
        df = sportec._add_clock(events_df)
        periods = df["std_period"]
        assert periods.dtype == pl.Int8
        assert periods[0] == 1
        assert periods[1] == 1
        assert periods[3] == 2
        assert periods[4] == 2

        times = df["std_time"]
        assert times.dtype == pl.Duration
        full_times = df["std_full_time"]
        assert full_times.dtype == pl.Duration
        assert times[1] == timedelta(minutes=20)
        assert full_times[1] == timedelta(minutes=20)
        assert times[4] == timedelta(minutes=30)
        assert full_times[4] == timedelta(minutes=30 + 45)

import io
import json
import uuid
from pathlib import Path
from typing import Any

import polars as pl

from .._models import (
    Competition,
    Events,
    GameInfo,
    Pitch,
    Player,
    Records,
    Team,
)
from .base import EventsParser, Parser


class StatsBombEventsParser(EventsParser):
    _pitch = Pitch(
        length=120,
        width=80,
    )

    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        return pl.read_json(source, infer_schema_length=None)

    def _process(
        self,
        df: pl.DataFrame,
        game_id: str | None = None,
    ) -> pl.DataFrame:
        game_id = game_id if game_id is not None else uuid.uuid4().hex
        return df.select(
            [
                pl.col("id").alias("id_"),
                pl.col("type")
                .struct.field("name")
                .cast(pl.Categorical)
                .alias("type_"),
                pl.col("timestamp").alias("time"),
                pl.col("player")
                .struct.field("id")
                .cast(pl.String)
                .cast(pl.Categorical)
                .alias("player_id"),
                pl.col("team")
                .struct.field("id")
                .cast(pl.String)
                .cast(pl.Categorical)
                .alias("team_id"),
                pl.lit(game_id).alias("game_id").cast(pl.Categorical),
                pl.col("location").list.get(0).alias("x"),
                pl.col("location").list.get(1).alias("y"),
                pl.col("possession").cast(pl.Int64).alias("part"),
            ]
        )

    def parse(
        self,
        source: str | bytes | io.IOBase | Path,
        game_id: str | None = None,
    ) -> Events:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df, game_id=game_id)
        return Events(df, self._pitch)


class StatsBombCompetitionsParser(Parser):
    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        return pl.read_json(source, infer_schema_length=None)

    def _process(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.select(
            [
                pl.col("competition_id").alias("id_").cast(pl.String),
                pl.col("competition_name").alias("name"),
                pl.col("season_id").cast(pl.String),
                pl.col("season_name"),
                pl.col('country_name').alias('country'),
            ]
        )

    def parse(
        self, source: str | bytes | io.IOBase | Path
    ) -> Records[Competition]:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df)
        return Records[Competition](df, Competition)


class StatsBombTeamsParser(Parser):
    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        return pl.read_json(source, infer_schema_length=None)

    def _process(self, df: pl.DataFrame) -> pl.DataFrame:
        home_teams_df = df.select(
            [
                pl.col("home_team")
                .struct.field("home_team_id")
                .cast(pl.String)
                .alias("id_"),
                pl.col("home_team")
                .struct.field("home_team_name")
                .cast(pl.String)
                .alias("name"),
            ]
        )
        away_teams_df = df.select(
            [
                pl.col("away_team")
                .struct.field("away_team_id")
                .cast(pl.String)
                .alias("id_"),
                pl.col("away_team")
                .struct.field("away_team_name")
                .cast(pl.String)
                .alias("name"),
            ]
        )
        return (
            pl.concat([home_teams_df, away_teams_df], how="vertical")
            .unique(subset=["id_"])
            .with_columns(pl.lit(None).cast(pl.String).alias("color"))
        )

    def parse(self, source: str | bytes | io.IOBase | Path) -> Records[Team]:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df)
        return Records[Team](df, Team)


class StatsBombGamesInfoParser(Parser):
    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        return pl.read_json(source, infer_schema_length=None)

    def _process(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.select(
            [
                pl.col("match_id").alias("id_").cast(pl.String),
                pl.col("match_date").alias("date"),
                pl.col("kick_off").alias("time"),
                pl.col("home_team")
                .struct.field("home_team_id")
                .cast(pl.String)
                .alias("home_team_id"),
                pl.col("away_team")
                .struct.field("away_team_id")
                .cast(pl.String)
                .alias("away_team_id"),
                pl.col("competition")
                .struct.field("competition_id")
                .cast(pl.String)
                .alias("competition_id"),
                pl.col("season")
                .struct.field("season_id")
                .cast(pl.String)
                .alias("season_id"),
                pl.col("home_score").cast(pl.Int8),
                pl.col("away_score").cast(pl.Int8),
            ]
        )

    def parse(
        self, source: str | bytes | io.IOBase | Path
    ) -> Records[GameInfo]:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df)
        return Records[GameInfo](df, GameInfo)
    

class StatsBombPlayersParser(Parser):
    def _read_json(self, source: bytes | io.IOBase | Path) -> Any:
        if isinstance(source, Path):
            return json.load(source.open())
        elif isinstance(source, bytes):
            return json.load(io.BytesIO(source))
        elif isinstance(source, io.IOBase):
            return json.load(source)
        else:
            raise TypeError("Unsupported source type")

    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        lineups = self._read_json(source)
        players = []
        for team in lineups:
            for player in team["lineup"]:
                player["team_id"] = team["team_id"]
                players.append(player)
        return pl.DataFrame(players).unique(subset=["player_id"])

    def _process(self, df: pl.DataFrame) -> pl.DataFrame:
        return df.select(
            [
                pl.col("player_id").cast(pl.String).alias("id_"),
                pl.col("team_id").cast(pl.String),
                pl.col("player_name").cast(pl.String).alias("name"),
                pl.col("jersey_number").cast(pl.Int8).alias("number"),
                pl.col("positions")
                .list.get(0, null_on_oob=True)
                .struct.field("position")
                .alias("position"),
            ]
        )

    def parse(self, source: str | bytes | io.IOBase | Path) -> Records[Player]:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df)
        return Records[Player](df, Player)

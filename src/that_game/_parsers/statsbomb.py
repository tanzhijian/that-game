import io
import uuid
from pathlib import Path

import polars as pl

from .._models import Events, Pitch
from .base import EventsParser


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

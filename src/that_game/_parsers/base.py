import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import polars as pl

from .._models import Event, Events, Pitch, Record, Records
from .._utils import transform_schema


class Parser(ABC):
    required_schema = transform_schema(Record)

    def _df_source_parameterization(
        self, source: str | bytes | io.IOBase | Path
    ) -> bytes | io.IOBase | Path:
        if isinstance(source, str):
            return io.StringIO(source)
        else:
            return source

    @abstractmethod
    def _read(self, source: bytes | io.IOBase | Path) -> pl.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def _process(self, df: pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError

    def parse_raw_df(
        self, source: str | bytes | io.IOBase | Path
    ) -> pl.DataFrame:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        return df

    def _parse_df(
        self, source: str | bytes | io.IOBase | Path
    ) -> pl.DataFrame:
        df = self.parse_raw_df(source)
        df = self._process(df)
        return df

    @abstractmethod
    def parse(self, source: str | bytes | io.IOBase | Path) -> Records[Any]:
        raise NotImplementedError


class EventsParser(Parser, ABC):
    required_schema = transform_schema(Event)
    _pitch = Pitch()

    def parse(self, source: str | bytes | io.IOBase | Path) -> Events:
        df = self._parse_df(source)
        return Events(df, self._pitch)

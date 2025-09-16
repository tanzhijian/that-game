import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import polars as pl

from .._models import Events, Pitch, Records


class Parser(ABC):
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

    @abstractmethod
    def parse(self, source: str | bytes | io.IOBase | Path) -> Records[Any]:
        raise NotImplementedError


class EventsParser(Parser, ABC):
    _pitch = Pitch()

    def parse(self, source: str | bytes | io.IOBase | Path) -> Events:
        source = self._df_source_parameterization(source)
        df = self._read(source)
        df = self._process(df)
        return Events(df, self._pitch)

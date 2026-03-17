from typing import Any

import polars as pl

from ._providers import Provider


class Record:
    def __init__(self, data: dict[str, Any]) -> None:
        pass


class Records:
    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider

from typing import Any

import polars as pl

from ._providers.base import Provider


class Schema(dict):
    pass


class Record:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data


class Records:
    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider
        self.index = provider.index

    def __len__(self) -> int:
        return len(self.data)

    @property
    def fields(self) -> list[str]: ...

    @property
    def schema(self) -> Schema: ...

    def filter(self, **kwargs: Any) -> "Records":
        mask = pl.lit(True)
        for key, value in kwargs.items():
            if key not in self.index:
                raise KeyError(
                    f"Invalid filter key: {key}, "
                    f"expected one of {list(self.index.keys())}"
                )

            mask &= pl.col(self.index[key]) == value
        records = Records(self.data.filter(mask), self.provider)
        if len(records) < 1:
            raise ValueError(f"No records found for criteria: {kwargs}")
        return records

    def select(self, *args: str) -> pl.DataFrame:
        return self.data.select(args)

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
        self.field_map = provider.field_map

    def __len__(self) -> int:
        return len(self.data)

    @property
    def types(self) -> list[str]:
        return sorted(self.data[self.field_map["type_"]].unique().to_list())

    @property
    def schema(self) -> Schema: ...

    def filter(
        self,
        *,
        drop_null_columns: bool = False,
        **kwargs: Any,
    ) -> "Records":
        mask = pl.lit(True)
        for key, value in kwargs.items():
            if key not in self.field_map:
                raise KeyError(
                    f"Invalid filter key: {key}, "
                    f"expected one of {list(self.field_map.keys())}"
                )

            mask &= pl.col(self.field_map[key]) == value
        data = self.data.filter(mask)

        if drop_null_columns:
            drop_cols = [
                c for c in data.columns if data[c].null_count() == data.height
            ]
            data = data.drop(drop_cols)

        records = Records(data, self.provider)
        if len(records) < 1:
            raise ValueError(f"No records found for criteria: {kwargs}")
        return records

from typing import Any, Self

import polars as pl

from ._expression import FilterExpression
from ._providers.base import Provider


def _set_nested_value(
    data: dict[str, Any],
    key: str,
    value: Any,
    separator: str,
) -> None:
    keys = key.split(separator)
    current = data
    for part in keys[:-1]:
        current = current.setdefault(part, {})
    current[keys[-1]] = value


def _to_nested_dicts(
    df: pl.DataFrame, separator: str = "."
) -> list[dict[str, Any]]:
    items = df.to_dicts()
    nested_items: list[dict[str, Any]] = []

    for item in items:
        nested_item: dict[str, Any] = {}
        for key, value in item.items():
            if separator in key:
                _set_nested_value(nested_item, key, value, separator)
            else:
                nested_item[key] = value
        nested_items.append(nested_item)

    return nested_items


def _drop_null_columns(df: pl.DataFrame) -> pl.DataFrame:
    null_cols = [c for c in df.columns if df[c].null_count() == df.height]
    return df.drop(null_cols)


class Records:
    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider
        self.field_map = self.provider.field_map

    def __len__(self) -> int:
        return len(self.data)

    def to_dict(self, separator: str = ".") -> list[dict[str, Any]]:
        data = _drop_null_columns(self.data)
        return _to_nested_dicts(data, separator=separator)

    def sample(self) -> dict[str, Any]:
        row = self.data.sample(1)
        row = _drop_null_columns(row)
        return _to_nested_dicts(row)[0]

    def filter(
        self,
        *,
        drop_null_columns: bool = False,
        **kwargs: Any,
    ) -> Self:
        mask = pl.lit(True)
        for key, value in kwargs.items():
            if key not in self.field_map:
                raise KeyError(
                    f"Invalid filter key: {key}, "
                    f"expected one of {list(self.field_map.keys())}"
                )

            column_name = self.field_map[key]
            column = pl.col(column_name)
            if isinstance(value, FilterExpression):
                dtype = self.data.schema[column_name]
                mask &= value.build(column, dtype)
            else:
                mask &= column == value
        data = self.data.filter(mask)

        if drop_null_columns:
            data = _drop_null_columns(data)

        records = type(self)(data, self.provider)
        if len(records) < 1:
            raise ValueError(f"No records found for criteria: {kwargs}")
        return records


class Events(Records):
    @property
    def types(self) -> list[str]:
        values = self.data[self.field_map["type"]].unique().to_list()
        return sorted(values, key=lambda x: (x is None, x))


class Tracking(Records):
    pass

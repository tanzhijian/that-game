from typing import Any

import polars as pl

from ._providers.base import Provider
from .expression import (
    Between,
    Compare,
    EndsWith,
    FilterExpression,
    StartsWith,
)


def _is_numeric_dtype(dtype: pl.DataType) -> bool:
    return dtype.is_numeric()


def _build_filter_expr(
    column: pl.Expr, value: Any, dtype: pl.DataType
) -> pl.Expr:
    if isinstance(value, FilterExpression):
        if isinstance(value, Compare):
            if not _is_numeric_dtype(dtype):
                raise ValueError(
                    "Comparison expressions require a numeric column"
                )
            if value.operator == ">":
                return column > value.value
            if value.operator == ">=":
                return column >= value.value
            if value.operator == "<":
                return column < value.value
            if value.operator == "<=":
                return column <= value.value
            raise ValueError(
                f"Unsupported comparison operator: {value.operator}"
            )

        if isinstance(value, Between):
            if not _is_numeric_dtype(dtype):
                raise ValueError(
                    "Between expressions require a numeric column"
                )
            return column.is_between(value.lower, value.upper, closed="both")

        if isinstance(value, StartsWith):
            if dtype != pl.String:
                raise ValueError(
                    "starts_with expressions require a string column"
                )
            return column.str.starts_with(value.value)

        if isinstance(value, EndsWith):
            if dtype != pl.String:
                raise ValueError(
                    "ends_with expressions require a string column"
                )
            return column.str.ends_with(value.value)

        raise ValueError(
            f"Unsupported filter expression: {type(value).__name__}"
        )

    return column == value


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


class Records:
    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider
        self.field_map = provider.field_map

    def __len__(self) -> int:
        return len(self.data)

    @property
    def types(self) -> list[str]:
        values = self.data[self.field_map["type_"]].unique().to_list()
        return sorted(values, key=lambda x: (x is None, x))

    def to_dict(self, separator: str = ".") -> list[dict[str, Any]]:
        records = self.data.to_dicts()
        nested_records: list[dict[str, Any]] = []

        for record in records:
            nested_record: dict[str, Any] = {}
            for key, value in record.items():
                if separator in key:
                    _set_nested_value(nested_record, key, value, separator)
                else:
                    nested_record[key] = value
            nested_records.append(nested_record)

        return nested_records

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

            column_name = self.field_map[key]
            column = pl.col(column_name)
            dtype = self.data.schema[column_name]
            mask &= _build_filter_expr(column, value, dtype)
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

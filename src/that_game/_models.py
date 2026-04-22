from typing import Any

import polars as pl

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

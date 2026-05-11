from datetime import timedelta
from typing import Any, Self

import polars as pl

from ._expression import FilterExpression
from ._providers.base import PERIOD_TIME, IndexColumns, Provider


class Clock:
    def __init__(
        self,
        period: int | None,
        time: str | None,
        full_time: str | None,
    ) -> None:
        """Supported formats:
        - "MM:SS" (e.g., "05:49")
        - "MM:SS.mmm" (e.g., "75:49.559")
        """
        self._period = period
        self._time = self._parse_time(time) if time is not None else time
        self._full_time = (
            self._parse_time(full_time) if full_time is not None else full_time
        )

    def _parse_time(self, time_str: str) -> timedelta:
        m_str, remainder = time_str.split(":")
        if "." in remainder:
            s_str, ms_str = remainder.split(".")
        else:
            s_str, ms_str = remainder, 0
        return timedelta(
            minutes=int(m_str), seconds=int(s_str), milliseconds=int(ms_str)
        )

    def _classify_timedelta(self, td: timedelta) -> int:
        mins = td.total_seconds() / 60
        for period, time in sorted(PERIOD_TIME.items(), reverse=True):
            if mins >= time:
                return period
        return 1

    def period(self) -> int:
        if self._period is not None:
            return self._period
        if self._full_time is not None:
            return self._classify_timedelta(self._full_time)
        raise ValueError("Cannot determine period without period or full_time")

    def time(self) -> timedelta:
        if self._time is not None:
            return self._time
        if self._period is not None and self._full_time is not None:
            period_time = timedelta(minutes=PERIOD_TIME[self._period])
            return self._full_time - period_time
        raise ValueError(
            "Cannot determine time without time or both period and full_time"
        )

    def full_time(self) -> timedelta:
        if self._full_time is not None:
            return self._full_time
        if self._period is not None and self._time is not None:
            period_time = timedelta(minutes=PERIOD_TIME[self._period])
            return period_time + self._time
        raise ValueError(
            "Cannot determine full_time without full_time or both "
            "period and time"
        )


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


def _drop_null_and_index_columns(df: pl.DataFrame) -> pl.DataFrame:
    null_cols = [c for c in df.columns if df[c].null_count() == df.height]
    return df.drop(null_cols, f"^{IndexColumns._PREFIX}.*$")


class Records:
    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider
        self.aliases = self.provider.field_aliases

    def __len__(self) -> int:
        return len(self.data)

    def to_dict(self, separator: str = ".") -> list[dict[str, Any]]:
        data = _drop_null_and_index_columns(self.data)
        return _to_nested_dicts(data, separator=separator)

    def sample(self) -> dict[str, Any]:
        row = self.data.sample(1)
        row = _drop_null_and_index_columns(row)
        return _to_nested_dicts(row)[0]

    def filter(
        self,
        *,
        drop_null_columns: bool = False,
        **kwargs: Any,
    ) -> Self:
        mask = pl.lit(True)
        for key, value in kwargs.items():
            if key not in self.aliases:
                raise KeyError(
                    f"Invalid filter key: {key}, "
                    f"expected one of {list(self.aliases.keys())}"
                )

            column_name = self.aliases[key]
            column = pl.col(column_name)
            if isinstance(value, FilterExpression):
                dtype = self.data.schema[column_name]
                mask &= value.build(column, dtype)
            else:
                mask &= column == value
        data = self.data.filter(mask)

        if drop_null_columns:
            data = _drop_null_and_index_columns(data)

        records = type(self)(data, self.provider)
        if len(records) < 1:
            raise ValueError(f"No records found for criteria: {kwargs}")
        return records


class Events(Records):
    @property
    def types(self) -> list[str]:
        values = self.data[self.aliases["type"]].unique().to_list()
        return sorted(values, key=lambda x: (x is None, x))


class Tracking(Records):
    pass

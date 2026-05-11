from collections.abc import Mapping
from dataclasses import dataclass
from typing import Callable, Iterator, Literal

import polars as pl

NAME_SEPARATOR = ";"
PERIOD_TIME = {
    1: 0,
    2: 45,
    3: 90,
    4: 105,
    5: 120,
}


class IndexColumns:
    _PREFIX = "std_"

    TYPE = f"{_PREFIX}type"
    PERIOD = f"{_PREFIX}period"
    TIME = f"{_PREFIX}time"
    FULL_TIME = f"{_PREFIX}full_time"

    __slots__ = ()


class FieldAliases(Mapping[str, str]):
    def __init__(
        self,
        *,
        id: str,
        type: str,
        period: str,
        time: str,
        full_time: str,
        **kwargs: str,
    ) -> None:
        self._aliases = {
            "id": id,
            "type": type,
            "period": period,
            "time": time,
            "full_time": full_time,
            **kwargs,
        }

    def __getitem__(self, key: str) -> str:
        return self._aliases[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._aliases)

    def __len__(self) -> int:
        return len(self._aliases)

    def __repr__(self) -> str:
        return f"FieldAliases({self._aliases})"


@dataclass(kw_only=True, frozen=True, slots=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None

    field_aliases: FieldAliases

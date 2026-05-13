from dataclasses import dataclass
from typing import Callable, Literal

import polars as pl

NAME_SEPARATOR = ";"
PERIOD_MINUTES = {
    1: 0,
    2: 45,
    3: 90,
    4: 105,
    5: 120,
}


class ExtraNames:
    _PREFIX = "std_"

    TYPE = f"{_PREFIX}type"
    PERIOD = f"{_PREFIX}period"
    TIME = f"{_PREFIX}time"
    FULL_TIME = f"{_PREFIX}full_time"

    __slots__ = ()


@dataclass(kw_only=True, frozen=True, slots=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None
    field_aliases: dict[str, str]

from dataclasses import dataclass
from typing import Callable, Literal

import polars as pl

NAME_SEPARATOR = ";"


class FieldMap(dict[str, str]):
    pass


@dataclass(kw_only=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None

    field_map: dict[str, str]

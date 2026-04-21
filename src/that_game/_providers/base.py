from dataclasses import dataclass
from typing import Callable, Literal, TypedDict

import polars as pl


class FieldMap(TypedDict):
    id_: str
    type_: str


@dataclass(kw_only=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None

    field_map: FieldMap

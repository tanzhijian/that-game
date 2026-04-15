from dataclasses import dataclass
from typing import Callable, Literal

import polars as pl


@dataclass(kw_only=True)
class Index:
    id_: str
    type_: str


@dataclass(kw_only=True)
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str = "."
    preprocess: Callable[[pl.DataFrame], pl.DataFrame] | None = None

    index: Index


def _sportec_events_add_type_field(df: pl.DataFrame) -> pl.DataFrame:
    return df


statsbomb = Provider(
    data_type="json",
    root=".",
    index=Index(id_="id", type_="type.name"),
)
sportec = Provider(
    data_type="xml",
    root="PutDataRequest.Event",
    preprocess=_sportec_events_add_type_field,
    index=Index(id_="id", type_="type.name"),
)

from typing import Any

import polars as pl

from ._providers import Provider


class Record:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data


class Records:
    indexable_fields = {"id", "type"}

    def __init__(self, data: pl.DataFrame, provider: Provider) -> None:
        self.data = data
        self.provider = provider

    def _get_routes(self, key: str) -> list[str]:
        match key:
            case "type":
                route = self.provider.type_route
            case _:
                raise ValueError(f"Unsupported filter key: {key}")
        return route.split(".")

    def _filter_df(
        self,
        df: pl.DataFrame,
        key: str,
        value: str | int | float | bool,
    ) -> pl.DataFrame:
        routes = self._get_routes(key)
        expr = pl.col(routes[0])
        if len(routes) > 1:
            for route in routes[1:]:
                expr = expr.struct.field(route)
        return df.filter(expr == value)

    def filter(self, **kwargs: str | int | float | bool) -> "Records":
        df = self.data
        for key, value in kwargs.items():
            if key not in self.indexable_fields:
                raise ValueError(f"Column '{key}' does not exist in DataFrame")
            df = self._filter_df(df, key, value)
        return Records(df, self.provider)

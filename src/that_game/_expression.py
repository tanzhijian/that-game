from dataclasses import dataclass
from datetime import timedelta

import polars as pl


class FilterExpression:
    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        raise NotImplementedError

    def _require_numeric(
        self, dtype: pl.DataType, message: str
    ) -> None:
        if not dtype.is_numeric():
            raise ValueError(message)

    def _require_string(
        self, dtype: pl.DataType, message: str
    ) -> None:
        if dtype != pl.String:
            raise ValueError(message)

    def _require_numeric_or_duration(
        self, dtype: pl.DataType, message: str
    ) -> None:
        if not dtype.is_numeric() and dtype.base_type() is not pl.Duration:
            raise ValueError(message)

    def _normalize_value(
        self, value: int | float | timedelta, dtype: pl.DataType
    ) -> int | float | timedelta:
        if isinstance(value, timedelta):
            if dtype.base_type() is not pl.Duration:
                raise ValueError(
                    "Timedelta expressions require a duration column"
                )
            return value
        return value


@dataclass(frozen=True)
class Compare(FilterExpression):
    operator: str
    value: int | float | timedelta

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_numeric_or_duration(
            dtype,
            "Comparison expressions require a numeric or duration column",
        )
        value = self._normalize_value(self.value, dtype)
        if self.operator == ">":
            return column > value
        if self.operator == ">=":
            return column >= value
        if self.operator == "<":
            return column < value
        if self.operator == "<=":
            return column <= value
        raise ValueError(
            f"Unsupported comparison operator: {self.operator}"
        )


@dataclass(frozen=True)
class Between(FilterExpression):
    lower: int | float | timedelta
    upper: int | float | timedelta

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_numeric_or_duration(
            dtype,
            "Between expressions require a numeric or duration column",
        )
        lower = self._normalize_value(self.lower, dtype)
        upper = self._normalize_value(self.upper, dtype)
        return column.is_between(lower, upper, closed="both")


@dataclass(frozen=True)
class StartsWith(FilterExpression):
    value: str

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_string(
            dtype, "starts_with expressions require a string column"
        )
        return column.str.starts_with(self.value)


@dataclass(frozen=True)
class EndsWith(FilterExpression):
    value: str

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_string(
            dtype, "ends_with expressions require a string column"
        )
        return column.str.ends_with(self.value)


def gt(value: int | float | timedelta) -> Compare:
    return Compare(">", value)


def ge(value: int | float | timedelta) -> Compare:
    return Compare(">=", value)


def lt(value: int | float | timedelta) -> Compare:
    return Compare("<", value)


def le(value: int | float | timedelta) -> Compare:
    return Compare("<=", value)


def between(
    lower: int | float | timedelta, upper: int | float | timedelta
) -> Between:
    return Between(lower, upper)


def starts_with(value: str) -> StartsWith:
    return StartsWith(value)


def ends_with(value: str) -> EndsWith:
    return EndsWith(value)

from dataclasses import dataclass

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


@dataclass(frozen=True)
class Compare(FilterExpression):
    operator: str
    value: int | float

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_numeric(
            dtype, "Comparison expressions require a numeric column"
        )
        if self.operator == ">":
            return column > self.value
        if self.operator == ">=":
            return column >= self.value
        if self.operator == "<":
            return column < self.value
        if self.operator == "<=":
            return column <= self.value
        raise ValueError(
            f"Unsupported comparison operator: {self.operator}"
        )


@dataclass(frozen=True)
class Between(FilterExpression):
    lower: int | float
    upper: int | float

    def build(self, column: pl.Expr, dtype: pl.DataType) -> pl.Expr:
        self._require_numeric(
            dtype, "Between expressions require a numeric column"
        )
        return column.is_between(self.lower, self.upper, closed="both")


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


def gt(value: int | float) -> Compare:
    return Compare(">", value)


def ge(value: int | float) -> Compare:
    return Compare(">=", value)


def lt(value: int | float) -> Compare:
    return Compare("<", value)


def le(value: int | float) -> Compare:
    return Compare("<=", value)


def between(lower: int | float, upper: int | float) -> Between:
    return Between(lower, upper)


def starts_with(value: str) -> StartsWith:
    return StartsWith(value)


def ends_with(value: str) -> EndsWith:
    return EndsWith(value)


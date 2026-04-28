from dataclasses import dataclass


class FilterExpression:
    pass


@dataclass(frozen=True)
class Compare(FilterExpression):
    operator: str
    value: int | float


@dataclass(frozen=True)
class Between(FilterExpression):
    lower: int | float
    upper: int | float


@dataclass(frozen=True)
class StartsWith(FilterExpression):
    value: str


@dataclass(frozen=True)
class EndsWith(FilterExpression):
    value: str


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


__all__ = (
    "Between",
    "Compare",
    "EndsWith",
    "FilterExpression",
    "StartsWith",
    "between",
    "ends_with",
    "ge",
    "gt",
    "le",
    "lt",
    "starts_with",
)

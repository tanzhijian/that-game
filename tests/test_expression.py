from datetime import timedelta

import polars as pl
import pytest

from that_game import expression

df = pl.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 28, 22],
        "score": [85.5, 90.0, 78.0, 92.5, 88.0],
        "td": [
            timedelta(minutes=1),
            timedelta(minutes=2),
            timedelta(minutes=3),
            timedelta(minutes=4),
            timedelta(minutes=5),
        ],
    }
)


@pytest.mark.parametrize(
    ("column_name", "value", "counts"),
    (
        ("age", 28, (2, 3, 2, 3)),
        ("score", 80.0, (4, 4, 1, 1)),
        ("td", timedelta(minutes=3), (2, 3, 2, 3)),
    ),
)
def test_compare(
    column_name: str,
    value: int | float | timedelta,
    counts: tuple[int, ...],
) -> None:
    column = pl.col(column_name)
    dtype = df.schema[column_name]
    factories = (expression.gt, expression.ge, expression.lt, expression.le)
    for i, factory in enumerate(factories):
        compare = factory(value)
        expr = compare.build(column, dtype)
        filtered = df.filter(expr)
        assert len(filtered) == counts[i]


def test_compare_error() -> None:
    compare = expression.gt(30)
    with pytest.raises(
        ValueError,
        match="Comparison expressions require a numeric or duration column",
    ):
        compare.build(pl.col("name"), df.schema["name"])


@pytest.mark.parametrize(
    ("column_name", "values", "count"),
    (
        ("age", (28, 35), 3),
        ("score", (80.0, 91.0), 3),
        ("td", (timedelta(minutes=2), timedelta(minutes=4)), 3),
    ),
)
def test_between(
    column_name: str,
    values: tuple[int | float | timedelta, int | float | timedelta],
    count: int,
) -> None:
    column = pl.col(column_name)
    dtype = df.schema[column_name]
    between = expression.between(*values)
    expr = between.build(column, dtype)
    filtered = df.filter(expr)
    assert len(filtered) == count


def test_between_error() -> None:
    between = expression.between(20, 30)
    with pytest.raises(
        ValueError,
        match="Between expressions require a numeric or duration column",
    ):
        between.build(pl.col("name"), df.schema["name"])


def test_starts_with() -> None:
    expr = expression.starts_with("A")
    filtered = df.filter(expr.build(pl.col("name"), df.schema["name"]))
    assert len(filtered) == 1


def test_starts_with_error() -> None:
    expr = expression.starts_with("A")
    with pytest.raises(
        ValueError, match="starts_with expressions require a string column"
    ):
        expr.build(pl.col("age"), df.schema["age"])


def test_ends_with() -> None:
    expr = expression.ends_with("e")
    filtered = df.filter(expr.build(pl.col("name"), df.schema["name"]))
    assert len(filtered) == 3


def test_ends_with_error() -> None:
    expr = expression.ends_with("e")
    with pytest.raises(
        ValueError, match="ends_with expressions require a string column"
    ):
        expr.build(pl.col("age"), df.schema["age"])

import polars as pl
import pytest

import that_game.expression
from that_game import expression


class TestComparisonExpressions:
    @pytest.mark.parametrize(
        ("factory", "value", "operator"),
        [
            (expression.gt, 1, ">"),
            (expression.ge, 10, ">="),
            (expression.lt, 3, "<"),
            (expression.le, 2, "<="),
        ],
    )
    def test_compare_factories_create_expected_operators(
        self,
        factory: object,
        value: int,
        operator: str,
    ) -> None:
        expr = factory(value)

        assert expr.operator == operator
        assert expr.value == value

    def test_between_stores_bounds(self) -> None:
        expr = expression.between(5, 10)

        assert expr.lower == 5
        assert expr.upper == 10

    @pytest.mark.parametrize(
        ("factory", "args", "message"),
        [
            (
                expression.ge,
                (10,),
                "Comparison expressions require a numeric column",
            ),
            (
                expression.between,
                (1, 2),
                "Between expressions require a numeric column",
            ),
        ],
    )
    def test_numeric_expressions_reject_non_numeric_columns(
        self,
        factory: object,
        args: tuple[int, ...],
        message: str,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=message,
        ):
            factory(*args).build(pl.col("name"), pl.String)


class TestStringExpressions:
    @pytest.mark.parametrize(
        ("factory", "value"),
        [
            (expression.starts_with, "prefix"),
            (expression.ends_with, "suffix"),
        ],
    )
    def test_string_factories_store_value(
        self,
        factory: object,
        value: str,
    ) -> None:
        expr = factory(value)

        assert expr.value == value

    @pytest.mark.parametrize(
        ("factory", "message"),
        [
            (
                expression.starts_with,
                "starts_with expressions require a string column",
            ),
            (
                expression.ends_with,
                "ends_with expressions require a string column",
            ),
        ],
    )
    def test_string_expressions_reject_non_string_columns(
        self,
        factory: object,
        message: str,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=message,
        ):
            factory("name").build(pl.col("x"), pl.Int64)


class TestPublicExpressionModule:
    def test_public_expression_module_supports_direct_submodule_import(
        self,
    ) -> None:
        assert that_game.expression.ge(1).value == 1

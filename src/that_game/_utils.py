import types
from dataclasses import fields
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

import polars as pl

_TYPES_MAP: dict[type, type[pl.DataType]] = {
    str: pl.String,
    int: pl.Int32,
    float: pl.Float64,
    bool: pl.Boolean,
}


def _unwrap_typing(type_: Any) -> Any:
    if get_origin(type_) is Annotated:
        type_ = get_args(type_)[0]

    origin = get_origin(type_)

    is_union = origin in {Union, getattr(types, "UnionType", None)}
    if is_union:
        args = [a for a in get_args(type_) if a is not type(None)]
        if len(args) == 1:
            return _unwrap_typing(args[0])
        raise TypeError(f"Unsupported union type: {type_}")

    return type_


def _transform_type(type_: Any) -> type[pl.DataType]:
    unwrapped = _unwrap_typing(type_)
    if isinstance(unwrapped, type) and unwrapped in _TYPES_MAP:
        return _TYPES_MAP[unwrapped]
    raise TypeError(f"Unsupported type: {type_}")


def _update_schema(
    base_schema: dict[str, type[pl.DataType]],
    override_schema: dict[str, type[pl.DataType]],
) -> dict[str, type[pl.DataType]]:
    for key, value in override_schema.items():
        if key not in base_schema:
            raise ValueError(f"Custom schema contains unknown field: {key}")
        base_schema[key] = value
    return base_schema


def transform_schema(data_class: type) -> dict[str, type[pl.DataType]]:
    hints = get_type_hints(data_class, include_extras=True)
    pl_schema = {
        f.name: _transform_type(hints.get(f.name, f.type))
        for f in fields(data_class)
    }
    if hasattr(data_class, "custom_pl_schema"):
        pl_schema = _update_schema(
            pl_schema, data_class.custom_pl_schema
        )
    return pl_schema


def validate_schema(
    validate_df: pl.DataFrame, required_schema: dict[str, type[pl.DataType]],
) -> None:
    validate_schema = validate_df.schema
    for key, value in required_schema.items():
        if key not in validate_schema:
            raise ValueError(f"Missing required column: {key}")
        if validate_schema[key] != value:
            raise TypeError(
                f"Column '{key}' has incorrect type: "
                f"expected {value}, got {validate_schema[key]}"
            )

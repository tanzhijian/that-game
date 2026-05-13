from pathlib import Path
from typing import Any

import polars as pl
import xmltodict

from ._models import Events, Tracking
from ._providers.base import Provider

_INLINE_TEXT_LIMIT = 4096


def _read_text_if_path(source: Any) -> str:
    if isinstance(source, Path):
        return source.read_text()
    if isinstance(source, str):
        if len(source) > _INLINE_TEXT_LIMIT:
            return source
        path = Path(source)
        if path.is_file():
            return path.read_text()
        return source
    raise ValueError(f"Unsupported input type: {type(source)}")


def _flatten_structs(df: pl.DataFrame, separator: str = ".") -> pl.DataFrame:
    struct_cols = [n for n, d in df.schema.items() if isinstance(d, pl.Struct)]
    if not struct_cols:
        return df

    exprs = []
    for col_name, dtype in df.schema.items():
        if isinstance(dtype, pl.Struct):
            for field in dtype.fields:
                exprs.append(
                    pl.col(col_name)
                    .struct.field(field.name)
                    .alias(f"{col_name}{separator}{field.name}")
                )
        else:
            exprs.append(pl.col(col_name))

    return _flatten_structs(df.select(exprs), separator)


def _get_nested_value(
    data: dict[str, Any],
    target: str,
    separator: str = ".",
) -> Any:
    # 暂时采用硬编码
    current: Any = data
    for key in target.split(separator):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _load_xml(source: Any, root: str) -> pl.DataFrame:
    # 以后为了性能，可以考虑使用 lxml 优化
    text = _read_text_if_path(source)
    data = xmltodict.parse(text)

    # 是否需要预处理
    # xml 需要的数据可能不在头部，需要向下获取
    if root != ".":
        data = _get_nested_value(data, root)

    return pl.DataFrame(data, infer_schema_length=None)


def _load_df(source: Any, provider: Provider) -> pl.DataFrame:
    if isinstance(source, (list, dict)):
        df = pl.DataFrame(source, infer_schema_length=None)
    else:
        match provider.data_type:
            case "json":
                df = pl.read_json(source, infer_schema_length=None)
            case "jsonl":
                df = pl.read_ndjson(source, infer_schema_length=None)
            case "csv":
                df = pl.read_csv(source, infer_schema_length=None)
            case "xml":
                df = _load_xml(source, provider.root)
            case _:
                raise ValueError(
                    f"Unsupported data type: {provider.data_type}"
                )

    df = _flatten_structs(df)

    if provider.preprocess is not None:
        df = provider.preprocess(df)
    return df


def load_events(source: Any, provider: Provider) -> Events:
    df = _load_df(source, provider)
    return Events(df, provider)


def load_tracking(source: Any, provider: Provider) -> Tracking:
    df = _load_df(source, provider)
    return Tracking(df, provider)

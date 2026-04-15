from functools import reduce
from pathlib import Path
from typing import Any

import polars as pl
import xmltodict

from ._models import Records
from ._providers import Provider

_MAX_PATH_LEN = 4096


def _maybe_read(input_: Any) -> str:
    if isinstance(input_, Path):
        return input_.read_text()
    if isinstance(input_, str):
        if len(input_) > _MAX_PATH_LEN:
            return input_
        path = Path(input_)
        if path.is_file():
            return path.read_text()
        return input_
    raise ValueError(f"Unsupported input type: {type(input_)}")


def _flatten_structs(df: pl.DataFrame, separator: str = ".") -> pl.DataFrame:
    # 检查当前是否还有结构体列
    struct_cols = [n for n, d in df.schema.items() if isinstance(d, pl.Struct)]

    if not struct_cols:
        return df

    exprs = []
    for col_name, dtype in df.schema.items():
        if isinstance(dtype, pl.Struct):
            # 一次性展开该结构体的所有子列
            for field in dtype.fields:
                exprs.append(
                    pl.col(col_name)
                    .struct.field(field.name)
                    .alias(f"{col_name}{separator}{field.name}")
                )
        else:
            exprs.append(pl.col(col_name))

    # 核心优化：一次 select 完成一层所有转换，减少中间 DataFrame 生成
    return _flatten_structs(df.select(exprs), separator)


def _get_dict(
    data: dict[str, Any],
    target: str,
    separator: str = ".",
) -> dict[str, Any]:
    # 暂时采用硬编码
    keys = target.split(separator)
    return reduce(dict.get, keys, data)


def _load_xml(input_: Any, root: str) -> pl.DataFrame:
    # 以后为了性能，可以考虑使用 lxml 优化
    text = _maybe_read(input_)
    data = xmltodict.parse(text)

    # 是否需要预处理
    # xml 需要的数据可能不在头部，需要向下获取
    if root != ".":
        data = _get_dict(data, root)

    return pl.DataFrame(data, infer_schema_length=None)


def load(input_: Any, provider: Provider) -> Records:
    if isinstance(input_, (list, dict)):
        df = pl.DataFrame(input_, infer_schema_length=None)
    else:
        match provider.data_type:
            case "json":
                df = pl.read_json(input_, infer_schema_length=None)
            case "jsonl":
                df = pl.read_ndjson(input_, infer_schema_length=None)
            case "csv":
                df = pl.read_csv(input_, infer_schema_length=None)
            case "xml":
                df = _load_xml(input_, provider.root)
            case _:
                raise ValueError(
                    f"Unsupported data type: {provider.data_type}"
                )

    # 碾平
    df = _flatten_structs(df)

    # 读取完成前，针对数据供应商的不同，特殊处理一些字段
    if provider.preprocess is not None:
        df = provider.preprocess(df)
    return Records(df, provider)

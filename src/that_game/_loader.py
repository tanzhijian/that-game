import json
from pathlib import Path

import polars as pl

from ._models import Records
from ._providers import Provider
from ._types import DataType, InputTypes, PreTypes, SupportedTypes


def _maybe_read(data: InputTypes) -> PreTypes:
    if isinstance(data, Path):
        return data.read_text()
    if isinstance(data, str):
        path = Path(data)
        if path.is_file():
            return path.read_text()
    return data


def _load_csv(pre: str) -> DataType: ...


def _load_xml(pre: str) -> DataType: ...


def _load_json(pre: str) -> DataType:
    return json.loads(pre)


def _load_jsonl(pre: str) -> DataType: ...


def _load_data(
    pre: PreTypes,
    type_: SupportedTypes,
) -> DataType:
    if isinstance(pre, str):
        match type_:
            case "xml":
                return _load_xml(pre)
            case "csv":
                return _load_csv(pre)
            case "json":
                return _load_json(pre)
            case "jsonl":
                return _load_jsonl(pre)
            case _:
                raise ValueError(f"Unsupported data type: {type_}")
    return pre


def load(input_: InputTypes, provider: Provider) -> Records:
    pre = _maybe_read(input_)
    data = _load_data(pre, provider.data_type)
    root = provider.get_root(data)
    df = pl.DataFrame(root, infer_schema_length=None)
    return Records(df, provider)

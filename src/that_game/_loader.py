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


def _load_xml(input_: Any) -> pl.DataFrame:
    text = _maybe_read(input_)
    data = xmltodict.parse(text)
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
                df = _load_xml(input_)
            case _:
                raise ValueError(
                    f"Unsupported data type: {provider.data_type}"
                )

    return Records(df, provider)

from pathlib import Path
from typing import Any, Literal

type DataType = list[Any] | dict[str, Any]
type PreTypes = DataType | str
type InputTypes = PreTypes | Path
type SupportedTypes = Literal["csv", "xml", "json", "jsonl"]

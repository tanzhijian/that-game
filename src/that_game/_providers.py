from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class Provider:
    data_type: Literal["csv", "xml", "json", "jsonl"]
    root: str
    type_route: str

    def get_root(self, data: Any) -> Any:
        return data


statsbomb = Provider(
    data_type="json",
    root=".",
    type_route="type.name",
)

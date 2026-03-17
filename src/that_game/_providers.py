from dataclasses import dataclass

from ._types import DataType, SupportedTypes


@dataclass
class Provider:
    data_type: SupportedTypes
    root: str

    def get_root(self, data: DataType) -> DataType:
        return data


statsbomb = Provider(
    data_type="json",
    root=".",
)

from .base import FieldMap, Provider

statsbomb = Provider(
    data_type="json",
    root=".",
    field_map=FieldMap(id="id", type="type.name"),
)

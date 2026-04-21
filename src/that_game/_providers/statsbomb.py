from .base import FieldMap, Provider

statsbomb = Provider(
    data_type="json",
    root=".",
    field_map=FieldMap(id_="id", type_="type.name"),
)

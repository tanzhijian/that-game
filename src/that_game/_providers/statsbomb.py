from .base import FieldAliases, Provider

statsbomb = Provider(
    data_type="json",
    root=".",
    field_aliases=FieldAliases(
        id="id",
        type="type.name",
    ),
)

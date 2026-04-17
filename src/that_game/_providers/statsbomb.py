from .base import Index, Provider

statsbomb = Provider(
    data_type="json",
    root=".",
    index=Index(id_="id", type_="type.name"),
)

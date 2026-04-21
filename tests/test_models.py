from that_game import load
from that_game._providers.base import FieldMap, Provider


provider = Provider(
    data_type="json",
    field_map=FieldMap(id_="id", type_="type.name"),
)


def test_records_to_dict_restores_nested_structure() -> None:
    payload = [
        {
            "id": "123",
            "type": {"id": 1, "name": "Shot"},
            "location": {"x": 30.0, "y": 60.0},
        }
    ]

    records = load(payload, provider)

    assert records.to_dict() == payload


def test_records_to_dict_restores_multiple_nested_levels() -> None:
    payload = [
        {
            "id": "123",
            "type": {"name": "Pass"},
            "pass": {
                "end_location": {"x": 42.0, "y": 18.0},
            },
        }
    ]

    records = load(payload, provider)

    assert records.to_dict() == payload

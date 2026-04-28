from that_game import expression, load
from that_game._providers.base import FieldMap, Provider

provider = Provider(
    data_type="json",
    field_map=FieldMap(id_="id", type_="type.name"),
)

extended_provider = Provider(
    data_type="json",
    field_map={
        "id_": "id",
        "type_": "type.name",
        "x": "x",
        "name": "name",
    },
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


def test_records_filter_supports_numeric_comparison_expression() -> None:
    payload = [
        {"id": "1", "type": {"name": "Shot"}, "x": 10},
        {"id": "2", "type": {"name": "Pass"}, "x": 20},
        {"id": "3", "type": {"name": "Carry"}, "x": 30},
    ]

    records = load(payload, extended_provider)

    filtered = records.filter(x=expression.ge(20))

    assert [record["id"] for record in filtered.to_dict()] == ["2", "3"]


def test_records_filter_supports_between_expression() -> None:
    payload = [
        {"id": "1", "type": {"name": "Shot"}, "x": 10.0},
        {"id": "2", "type": {"name": "Pass"}, "x": 20.0},
        {"id": "3", "type": {"name": "Carry"}, "x": 30.0},
    ]

    records = load(payload, extended_provider)

    filtered = records.filter(x=expression.between(15, 25))

    assert [record["id"] for record in filtered.to_dict()] == ["2"]


def test_records_filter_supports_string_prefix_expression() -> None:
    payload = [
        {"id": "1", "type": {"name": "Shot"}, "name": "name-alpha"},
        {"id": "2", "type": {"name": "Pass"}, "name": "beta-name"},
    ]

    records = load(payload, extended_provider)

    filtered = records.filter(name=expression.starts_with("name"))

    assert [record["id"] for record in filtered.to_dict()] == ["1"]


def test_records_filter_supports_string_suffix_expression() -> None:
    payload = [
        {"id": "1", "type": {"name": "Shot"}, "name": "alpha-name"},
        {"id": "2", "type": {"name": "Pass"}, "name": "name-beta"},
    ]

    records = load(payload, extended_provider)

    filtered = records.filter(name=expression.ends_with("name"))

    assert [record["id"] for record in filtered.to_dict()] == ["1"]


def test_records_filter_raises_for_expression_type_mismatch() -> None:
    payload = [
        {"id": "1", "type": {"name": "Shot"}, "name": "name-alpha"},
    ]

    records = load(payload, extended_provider)

    try:
        records.filter(name=expression.ge(10))
    except ValueError as exc:
        assert str(exc) == "Comparison expressions require a numeric column"
    else:
        raise AssertionError(
            "Expected ValueError for mismatched expression type"
        )

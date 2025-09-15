import polars as pl

from that_game import Event, dataclass_instances_to_df


def test_dataclass_instances_to_df(event_1: Event, event_2: Event) -> None:
    df = dataclass_instances_to_df([event_1, event_2])
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 2
    assert df.schema["type_"] == pl.Categorical

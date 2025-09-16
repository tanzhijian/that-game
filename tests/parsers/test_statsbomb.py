from pathlib import Path

import pytest

from that_game import StatsBombEventsParser

data_path = Path(Path.cwd(), "tests/data/statsbomb")


class TestStatsBombEventsParser:
    @pytest.fixture(scope="class")
    def parser(self) -> StatsBombEventsParser:
        return StatsBombEventsParser()

    def test_parse(self, parser: StatsBombEventsParser) -> None:
        records = parser.parse(data_path / "events_3895333.json")
        sample = records.sample()
        assert type(sample.id_) is str
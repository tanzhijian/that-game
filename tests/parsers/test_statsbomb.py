from pathlib import Path

import pytest

from that_game import StatsBombEventsParser

data_path = Path(Path.cwd(), "tests/data/statsbomb")


class TestStatsBombEventsParser:
    @pytest.fixture(scope="class")
    def parser(self) -> StatsBombEventsParser:
        return StatsBombEventsParser()

    def test_parse(self, parser: StatsBombEventsParser) -> None:
        records = parser.parse(
            data_path / "events_3895333.json", game_id="3895333"
        )
        assert records.df['game_id'].n_unique() == 1
        event = records.sample()
        assert event.game_id == "3895333"

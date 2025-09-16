import uuid
from pathlib import Path

import pytest

from that_game import (
    StatsBombCompetitionsParser,
    StatsBombEventsParser,
    StatsBombGamesInfoParser,
    StatsBombPlayersParser,
    StatsBombTeamsParser,
)

data_path = Path(Path.cwd(), "tests/data/statsbomb")


class TestStatsBombEventsParser:
    @pytest.fixture(scope="class")
    def parser(self) -> StatsBombEventsParser:
        return StatsBombEventsParser()

    def test_parse(self, parser: StatsBombEventsParser) -> None:
        records = parser.parse(
            data_path / "events_3895333.json", game_id="3895333"
        )
        assert records.df["game_id"].n_unique() == 1
        event = records.sample()
        assert event.game_id == "3895333"

    def test_parse_no_game_id(self, parser: StatsBombEventsParser) -> None:
        records = parser.parse(data_path / "events_3895333.json")
        assert records.df["game_id"].n_unique() == 1
        event = records.sample()
        assert isinstance(event.game_id, str)
        uuid.UUID(event.game_id)


def test_statsbomb_competitions_parser() -> None:
    parser = StatsBombCompetitionsParser()
    records = parser.parse(data_path / "competitions.json")
    assert records.df.shape[0] > 0
    com = records.find_one(id_="9", season_id="281")
    assert com.name == "1. Bundesliga"


def test_statsbomb_teams_parser() -> None:
    parser = StatsBombTeamsParser()
    records = parser.parse(data_path / "matches_9_281.json")
    assert records.df.shape[0] > 0
    team = records.find_one(id_="904")
    assert team.name == "Bayer Leverkusen"


def test_statsbomb_gameinfo_parser() -> None:
    parser = StatsBombGamesInfoParser()
    records = parser.parse(data_path / "matches_9_281.json")
    assert records.df.shape[0] > 0
    game_info = records.find_one(id_="3895333")
    assert game_info.away_team_id == "904"
    assert game_info.away_score == 5


def test_statsbomb_players_parser() -> None:
    parser = StatsBombPlayersParser()
    records = parser.parse(data_path / "lineups_3895333.json")
    assert records.df.shape[0] > 0
    player = records.find_one(id_="3500")
    assert player.name == "Granit Xhaka"
    assert player.team_id == "904"
import pytest

from that_game._loaders.statsbomb import StatsBombLoader


class TestStatsBombLoaderAllParams:
    @pytest.fixture(scope="class")
    def loader(self) -> StatsBombLoader:
        data_path = "tests/data/statsbomb"
        matches_path = f"{data_path}/matches_9_281.json"
        lineups_path = f"{data_path}/lineups_3895333.json"
        events_path = f"{data_path}/events_3895333.json"
        game_id = "3895333"

        with (
            open(matches_path) as matches,
            open(lineups_path) as lineups,
            open(events_path) as events,
        ):
            return StatsBombLoader(
                game_id,
                events.read(),
                matches=matches.read(),
                lineups=lineups.read(),
            )

    def test_pitch(self, loader: StatsBombLoader) -> None:
        assert int(loader.pitch.length) == 120

    def test_datetime(self, loader: StatsBombLoader) -> None:
        assert loader.datetime == "2024-05-05 18:30:00.000"

    def test_competition(self, loader: StatsBombLoader) -> None:
        competition = loader.competition
        assert competition is not None
        assert competition.id == "9"
        assert competition.name == "1. Bundesliga"

    def test_home_team(self, loader: StatsBombLoader) -> None:
        team = loader.home_team
        assert team.id == "184"
        assert team.name == "Eintracht Frankfurt"

    def test_away_team(self, loader: StatsBombLoader) -> None:
        team = loader.away_team
        assert team.id == "904"
        assert team.name == "Bayer Leverkusen"

    def test_home_players(self, loader: StatsBombLoader) -> None:
        players = loader.home_players
        assert len(players) > 0
        player = players[0]
        assert player.name == "Ellyes Joris Skhiri"
        assert player.jersey_number == 15

    def test_away_players(self, loader: StatsBombLoader) -> None:
        players = loader.away_players
        assert len(players) > 0
        player = players[0]
        assert player.name == "Granit Xhaka"
        assert player.jersey_number == 34

    def test_events(self, loader: StatsBombLoader) -> None:
        events = loader.events
        assert len(events) > 0

    def test_shots(self, loader: StatsBombLoader) -> None:
        shots = loader.get_shots()
        assert len(shots) == 26
        shot = shots[0]
        assert shot.body_part == "left_foot"
        assert shot.xg is not None
        assert int(shot.xg * 1000) == 24
        assert shot.result == "blocked"
        assert shot.location.z is None

        assert shot.related_players is not None
        assert len(shot.related_players) == 19
        related_player = shot.related_players[0]
        assert int(related_player.location.x) == 99
        assert related_player.team.name == "Bayer Leverkusen"
        assert related_player.player.name == "Patrik Schick"

    def test_passes(self, loader: StatsBombLoader) -> None:
        passes = loader.get_passes()
        assert len(passes) > 0
        pass_ = passes[0]
        assert pass_.result == "success"
        assert pass_.location.z is None


class TestStatsBombLoaderOnlyEvents:
    @pytest.fixture(scope="class")
    def loader(self) -> StatsBombLoader:
        data_path = "tests/data/statsbomb"
        events_path = f"{data_path}/events_3895333.json"
        game_id = "3895333"

        with open(events_path) as events:
            return StatsBombLoader(game_id, events.read())

    def test_datetime(self, loader: StatsBombLoader) -> None:
        assert loader.datetime is None

    def test_competition(self, loader: StatsBombLoader) -> None:
        assert loader.competition is None

    def test_home_team(self, loader: StatsBombLoader) -> None:
        team = loader.home_team
        assert team.id == "184"
        assert team.name == "Eintracht Frankfurt"

    def test_away_team(self, loader: StatsBombLoader) -> None:
        team = loader.away_team
        assert team.id == "904"
        assert team.name == "Bayer Leverkusen"

    def test_home_players(self, loader: StatsBombLoader) -> None:
        players = loader.home_players
        assert len(players) > 0
        player = players[0]
        assert player.name == "Lucas Silva Melo"
        assert player.jersey_number is None

    def test_away_players(self, loader: StatsBombLoader) -> None:
        players = loader.away_players
        assert len(players) > 0
        player = players[0]
        assert player.name == "Jonas Hofmann"
        assert player.jersey_number is None

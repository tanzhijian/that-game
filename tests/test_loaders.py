import pytest

from that_game._loaders.statsbomb import load_statsbomb
from that_game._models import Game


class TestLoadStatsbomb:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
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
            return load_statsbomb(
                game_id, matches.read(), lineups.read(), events.read()
            )

    def test_fields(self, game: Game) -> None:
        assert game.id == "3895333"
        assert game.home_team.id == "184"
        assert game.home_team.name == "Eintracht Frankfurt"
        assert game.away_team.id == "904"
        assert game.away_team.name == "Bayer Leverkusen"
        assert game.kick_off == "18:30"
        assert game.competition.id == "9"

        player = game.away_players[0]
        assert player.name == "Granit Xhaka"
        assert player.jersey_number == 34

        assert len(game.events) > 0

    def test_events_status(self, game: Game) -> None:
        shots = game.shots()
        assert len(shots) == 26
        shot = shots[0]
        assert shot.body_part == "left_foot"

        pass_ = game.passes()[0]
        assert pass_.result == "success"
        assert shot.result == "blocked"
        assert shot.location.z is None

    def test_event_related_players(self, game: Game) -> None:
        shot = game.shots()[0]
        if shot.related_players is not None:
            assert len(shot.related_players) == 19
            related_player = shot.related_players[0]
            assert int(related_player.location.x) == 99
            assert related_player.team.name == "Bayer Leverkusen"
            assert related_player.player.name == "Patrik Schick"

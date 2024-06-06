import pytest
from that_game._models import (
    Competition,
    Event,
    Game,
    Player,
    PlayGround,
    Position,
    Team,
)
from that_game._status import BodyPart, EventType


class TestGame:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
        competition = Competition(id="pl", name="Premier League")
        home_team = Team(id="ars", name="Arsenal")
        away_team = Team(id="mci", name="Man City")
        home_players = [Player(id="a7", name="Bukayo Saka", role="FW")]
        away_players = [Player(id="h9", name="Erling Haaland", role="FW")]
        playground = PlayGround(length=108, width=68)

        events = [
            Event(
                id="0001",
                type=EventType.SHOT,
                timestamp=62.0,
                team=home_team,
                player=home_players[0],
                position=Position(x=100.1, y=43.2),
                body_part=BodyPart.LEFT_FOOT,
            )
        ]
        return Game(
            id="ars_vs_mci",
            datetime="2024-03-31 11:30",  # type: ignore
            playground=playground,
            competition=competition,
            home_team=home_team,
            away_team=away_team,
            home_players=home_players,
            away_players=away_players,
            events=events,
        )

    def test_game_attrs(self, game: Game) -> None:
        assert game.id == "ars_vs_mci"
        assert game.date == "2024-03-31"
        assert game.time == "11:30"

    def test_game_event(self, game: Game) -> None:
        shots = [event for event in game.events if event.type == EventType.SHOT]
        shot = shots[0]
        assert int(shot.position.x) == 100

    def test_model_dump_pandas(self, game: Game) -> None:
        df = game.model_dump_pandas()
        assert df.shape == (1, 11)
        event = df.iloc[0]
        assert event["id"] == "0001"
        assert event["team.name"] == "Arsenal"

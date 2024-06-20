import pytest
from that_game._models import (
    Competition,
    Event,
    Game,
    Location,
    Pitch,
    Player,
    Team,
)


class TestEvent:
    @pytest.fixture(scope="class")
    def event(self) -> Event:
        return Event(
            id="0001",
            type="shot",
            timestamp=62.0,
            team={"id": "ars", "name": "Arsenal"},
            player={"id": "h9", "name": "Erling Haaland", "position": "FW"},
            location={
                "x": 100.1,
                "y": 43.2,
                "pitch": {"length": 108, "width": 68},
            },
            body_part="left_foot",
            result="saved",
        )

    def test_attrs(self, event: Event) -> None:
        assert event.type == "shot"


class TestGame:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
        competition = Competition(id="pl", name="Premier League")
        home_team = Team(id="ars", name="Arsenal")
        away_team = Team(id="mci", name="Man City")
        home_players = [Player(id="a7", name="Bukayo Saka", position="FW")]
        away_players = [Player(id="h9", name="Erling Haaland", position="FW")]
        pitch = Pitch(length=108, width=68)

        events = [
            Event(
                id="0001",
                type="shot",
                timestamp=62.0,
                team=home_team,
                player=home_players[0],
                location=Location(x=100.1, y=43.2, pitch=pitch),
                body_part="left_foot",
                result="saved",
            )
        ]
        return Game(
            id="ars_vs_mci",
            datetime="2024-03-31 11:30",
            competition=competition,
            home_team=home_team,
            away_team=away_team,
            home_players=home_players,
            away_players=away_players,
            events=events,
        )

    def test_attrs(self, game: Game) -> None:
        assert game.id == "ars_vs_mci"
        assert game.date == "2024-03-31"
        assert game.kick_off == "11:30"

    def test_event(self, game: Game) -> None:
        shots = [event for event in game.events if event.type == "shot"]
        shot = shots[0]
        assert int(shot.location.x) == 100

    def test_model_dump_pandas(self, game: Game) -> None:
        df = game.model_dump_pandas()
        assert df.shape == (1, 14)
        event = df.iloc[0]
        assert event["id"] == "0001"
        assert event["team.name"] == "Arsenal"


class TestPosition:
    @pytest.fixture(scope="class")
    def location(self) -> Location:
        return Location(x=0.5, y=0.6, pitch=Pitch(length=1, width=1))

    def test_transform(self, location: Location) -> None:
        pitch = Pitch(length=100, width=100)
        new = location.transform(pitch)
        assert int(new.x) == 50
        assert int(new.y) == 60

    def test_init(self) -> None:
        location = Location(x=0.5, y=0.6, pitch={"length": 1, "width": 1})
        assert location

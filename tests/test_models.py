import pytest

from that_game._models import (
    Competition,
    Game,
    Location,
    Pitch,
    Player,
    Shot,
    Team,
)
from that_game._utils import is_float_close


class TestEvent:
    @pytest.fixture(scope="class")
    def event(self) -> Shot:
        return Shot(
            id="0001",
            type="shot",
            period="first_half",
            seconds=62.0,
            team={"id": "ars", "name": "Arsenal"},
            player={"id": "h9", "name": "Erling Haaland", "position": "FW"},
            location={
                "x": 100.1,
                "y": 43.2,
                "pitch": {"length": 108, "width": 68},
            },
            end_location={
                "x": 108.0,
                "y": 43.2,
                "pitch": {"length": 108, "width": 68},
            },
            pattern="open_play",
            body_part="left_foot",
            result="saved",
        )

    def test_attrs(self, event: Shot) -> None:
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
            Shot(
                id="0001",
                type="shot",
                period="first_half",
                seconds=62.0,
                team=home_team,
                player=home_players[0],
                location=Location(x=100.1, y=43.2, pitch=pitch),
                end_location=Location(x=108.0, y=43.2, pitch=pitch),
                pattern="open_play",
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
        shot = game.shots()[0]
        assert int(shot.location.x) == 100
        assert shot.period == "first_half"

    def test_model_dump_pandas(self, game: Game) -> None:
        df = game.model_dump_pandas()
        assert df.shape == (1, 33)
        event = df.iloc[0]
        assert event["id"] == "0001"
        assert event["team.name"] == "Arsenal"


def test_pitch_eq() -> None:
    pitch1 = Pitch(length=1, width=0.5 + 0.5, height_scale_to_meter=0.1 + 0.2)
    pitch2 = Pitch(length=1, width=1, height_scale_to_meter=0.3)
    assert pitch1 == pitch2


class TestLocation:
    @pytest.fixture
    def location(self) -> Location:
        return Location(
            x=60,
            y=40,
            pitch=Pitch(length=100, width=60),
        )

    @pytest.fixture
    def location_include_z(self) -> Location:
        return Location(
            x=120,
            y=43.4,
            z=2.3,
            pitch=Pitch(length=120, width=80, width_direction="down"),
        )

    def test_init(self, location: Location) -> None:
        assert int(location.x) == 60
        assert int(location.pitch.length) == 100

    def test_transform(self, location: Location) -> None:
        pitch = Pitch(
            length=120,
            width=80,
        )
        location.transform(pitch)
        assert int(location.x) == 72
        assert int(location.y) == 53

    def test_transform_direction_flip(self, location: Location) -> None:
        pitch = Pitch(
            length=120,
            width=80,
            length_direction="left",
            width_direction="down",
        )
        location.transform(pitch)
        assert int(location.x) == 48
        assert int(location.y) == 26

    def test_transform_vertical(self, location: Location) -> None:
        pitch = Pitch(
            length=60,
            width=100,
            width_direction="down",
            vertical=True,
        )
        location.transform(pitch)
        assert int(location.x) == 40
        assert int(location.y) == 60

    def test_z(self, location_include_z: Location) -> None:
        if location_include_z.z is not None:
            assert is_float_close(location_include_z.z, 2.3)

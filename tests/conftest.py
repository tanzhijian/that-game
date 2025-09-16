import pytest

from that_game import (
    Competition,
    Event,
    Shot,
    Team,
)


@pytest.fixture(scope="module")
def competition_1() -> Competition:
    return Competition(
        id_="comp_1",
        name="Premier League",
        season_id="2023",
        season_name="2023/24",
        country="England",
    )


@pytest.fixture(scope="module")
def competition_2() -> Competition:
    return Competition(
        id_="comp_2",
        name="La Liga",
        season_id="2023",
        season_name="2023/24",
        country="Spain",
    )

@pytest.fixture(scope="module")
def team_1() -> Team:
    return Team(
        id_="team_1",
        name="Team A",
        color="#FF0000",
    )


@pytest.fixture(scope="session")
def event_1() -> Event:
    return Event(
        id_="event_1",
        game_id="game_1",
        type_="pass",
        time="00:15",
        player_id="player_1",
        team_id="team_1",
        x=50.0,
        y=30.0,
        part=1,
    )


@pytest.fixture(scope="session")
def event_2() -> Event:
    return Event(
        id_="event_2",
        game_id="game_1",
        type_="shot",
        time="00:20",
        player_id="player_2",
        team_id="team_1",
        x=80.0,
        y=20.0,
        part=1,
    )


@pytest.fixture(scope="module")
def shot_1() -> Shot:
    return Shot(
        id_="shot_1",
        game_id="game_1",
        type_="shot",
        time="00:20",
        player_id="player_2",
        team_id="team_1",
        x=80.0,
        y=20.0,
        part=1,
    )

@pytest.fixture(scope="module")
def shot_2() -> Shot:
    return Shot(
        id_="shot_2",
        game_id="game_1",
        type_="shot",
        time="00:45",
        player_id="player_3",
        team_id="team_2",
        x=70.0,
        y=25.0,
        part=2,
    )

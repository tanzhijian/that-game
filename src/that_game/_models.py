from datetime import datetime

from pydantic import BaseModel, computed_field


class Competition(BaseModel):
    id: str
    name: str


class Player(BaseModel):
    id: str
    name: str
    role: str


class Team(BaseModel):
    id: str
    name: str


class Position(BaseModel):
    x: float
    y: float


class PlayGround(BaseModel):
    length: int
    width: int


class Event(BaseModel):
    id: str
    type: str
    timestamp: float
    team: Team
    player: Player
    position: Position


class Game(BaseModel):
    id: str
    datetime: datetime
    playground: PlayGround
    home_team: Team
    away_team: Team
    home_players: list[Player]
    away_players: list[Player]
    competition: Competition
    events: list[Event]

    @computed_field  # type: ignore
    @property
    def date(self) -> str:
        return self.datetime.strftime("%Y-%m-%d")

    @computed_field  # type: ignore
    @property
    def time(self) -> str:
        return self.datetime.strftime("%H:%M")

from datetime import datetime

import pandas as pd
from pydantic import BaseModel, computed_field

from ._status import BodyPart, EventType


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


class PlayGround(BaseModel):
    length: int
    width: int


class Position(BaseModel):
    x: float
    y: float


class Event(BaseModel):
    id: str
    type: EventType
    timestamp: float
    team: Team
    player: Player
    position: Position
    body_part: BodyPart


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

    def model_dump_pandas(self) -> pd.DataFrame:
        events_dict = self.model_dump()["events"]
        df = pd.json_normalize(events_dict)
        return df

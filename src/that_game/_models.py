import typing
from datetime import datetime

import pandas as pd
from pydantic import BaseModel, computed_field, field_validator

from ._status import BodyPart, EventType, ShotResult


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


class Playground(BaseModel):
    length: int
    width: int


class Position(BaseModel):
    x: float
    y: float
    playground: Playground

    @field_validator("playground", mode="before")
    @classmethod
    def get_playground(
        cls, v: Playground | dict[str, typing.Any]
    ) -> Playground:
        if isinstance(v, dict):
            return Playground(**v)
        return v

    def transform(self, playground: Playground) -> "Position":
        x_ratio = playground.length / self.playground.length
        y_ratio = playground.width / self.playground.width
        return Position(
            x=self.x * x_ratio,
            y=self.y * y_ratio,
            playground=playground,
        )


class Event(BaseModel):
    id: str
    type: EventType
    timestamp: float
    team: Team
    player: Player
    position: Position
    body_part: BodyPart
    result: ShotResult


class Game(BaseModel):
    id: str
    datetime: datetime
    playground: Playground
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

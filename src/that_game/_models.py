from datetime import datetime
from typing import Literal

import pandas as pd
from pydantic import BaseModel, computed_field, model_validator
from typing_extensions import Self

from ._status import BodyPart, EventType, Result


class Competition(BaseModel):
    id: str
    name: str


class Player(BaseModel):
    id: str
    name: str
    position: str


class Team(BaseModel):
    id: str
    name: str


class Pitch(BaseModel):
    length: int
    width: int
    x_direction: Literal["left", "right"] = "right"
    y_direction: Literal["up", "down"] = "up"


class Location(BaseModel):
    x: float
    y: float
    pitch: Pitch

    _standard_pitch = Pitch(length=108, width=68)

    @model_validator(mode="after")
    def _init_transform(self) -> Self:
        self.transform(self._standard_pitch)
        return self

    def transform(self, pitch: Pitch) -> None:
        if pitch == self.pitch:
            return

        x_scale = pitch.length / self.pitch.length
        y_scale = pitch.width / self.pitch.width
        self.x = self.x * x_scale
        self.y = self.y * y_scale

        if pitch.x_direction == "left":
            self.x = pitch.length - self.x
        if pitch.y_direction == "down":
            self.y = pitch.width - self.y
        self.pitch = pitch


class Event(BaseModel):
    id: str
    type: EventType
    seconds: float
    team: Team
    player: Player
    location: Location
    body_part: BodyPart
    result: Result


class Game(BaseModel):
    id: str
    datetime: datetime
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
    def kick_off(self) -> str:
        return self.datetime.strftime("%H:%M")

    def model_dump_pandas(self) -> pd.DataFrame:
        events_dict = self.model_dump()["events"]
        df = pd.json_normalize(events_dict)
        return df

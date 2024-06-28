from datetime import datetime
from typing import Literal

import pandas as pd
from pydantic import BaseModel, computed_field

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
    origin: Literal["top-left", "top-right", "bottom-left", "bottom-right"]
    home: Literal["left", "right"]
    away: Literal["left", "right"]

    @computed_field  # type: ignore
    @property
    def x_direction(self) -> Literal["left", "right"]:
        """X轴方向根据原点位置确定，原点在左侧时，X轴方向是向右（right），在右侧时，X轴方向是向左（left）"""
        return "right" if "left" in self.origin else "left"

    @computed_field  # type: ignore
    @property
    def y_direction(self) -> Literal["up", "down"]:
        """Y轴方向根据原点位置确定，原点在上方时，Y轴方向是向下（down），在下方时，Y轴方向是向上（up）"""
        return "down" if "top" in self.origin else "up"


class Location(BaseModel):
    x: float
    y: float
    pitch: Pitch

    _standard_pitch = Pitch(
        length=108,
        width=68,
        origin="top-left",
        home="left",
        away="left",
    )

    def transform(self, pitch: Pitch) -> None:
        x_ratio = pitch.length / self.pitch.length
        y_ratio = pitch.width / self.pitch.width
        self.x = self.x * x_ratio
        self.y = self.y * y_ratio
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

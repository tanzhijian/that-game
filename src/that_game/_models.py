from datetime import datetime
from typing import Literal, Sequence

import pandas as pd
from pydantic import BaseModel, Field, computed_field

from ._status import (
    BodyPart,
    EventType,
    PassPattern,
    PassResult,
    Period,
    ShotPattern,
    ShotResult,
)
from ._utils import is_float_close


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
    length: float
    width: float
    length_direction: Literal["left", "right"] = "right"
    width_direction: Literal["up", "down"] = "up"
    height_scale_to_meter: float = Field(default=1.0, gt=0)

    def __eq__(self, other: object) -> bool:
        """重写等于方法，以支持浮点数的容差比较。"""
        if not isinstance(other, Pitch):
            return NotImplemented

        for field in self.model_fields:
            value1, value2 = getattr(self, field), getattr(other, field)
            # 对浮点数使用容差比较
            if isinstance(value1, float) and isinstance(value2, float):
                return is_float_close(value1, value2)
            # 对非浮点数直接比较
            elif value1 != value2:
                return False
        return True


class Location(BaseModel):
    x: float
    y: float
    z: float | None = None
    pitch: Pitch

    def transform(self, pitch: Pitch) -> None:
        if pitch == self.pitch:
            return

        x_scale = pitch.length / self.pitch.length
        y_scale = pitch.width / self.pitch.width
        self.x = self.x * x_scale
        self.y = self.y * y_scale
        if self.z is not None and not is_float_close(
            pitch.height_scale_to_meter, self.pitch.height_scale_to_meter
        ):
            z_scale = (
                pitch.height_scale_to_meter / self.pitch.height_scale_to_meter
            )
            self.z = self.z * z_scale
            self.pitch.height_scale_to_meter = pitch.height_scale_to_meter

        if self.pitch.length_direction != pitch.length_direction:
            self.x = pitch.length - self.x
        if self.pitch.width_direction != pitch.width_direction:
            self.y = pitch.width - self.y
        self.pitch = pitch


class Event(BaseModel):
    id: str
    type: EventType
    period: Period
    seconds: float


class Shot(Event):
    team: Team
    player: Player
    location: Location
    end_location: Location
    pattern: ShotPattern
    body_part: BodyPart
    result: ShotResult


class Pass(Event):
    team: Team
    player: Player
    location: Location
    end_location: Location
    result: PassResult
    body_part: BodyPart
    pattern: PassPattern


class Game(BaseModel):
    id: str
    datetime: datetime
    home_team: Team
    away_team: Team
    home_players: Sequence[Player]
    away_players: Sequence[Player]
    competition: Competition
    events: Sequence[Shot | Pass]

    @computed_field  # type: ignore
    @property
    def date(self) -> str:
        return self.datetime.strftime("%Y-%m-%d")

    @computed_field  # type: ignore
    @property
    def kick_off(self) -> str:
        return self.datetime.strftime("%H:%M")

    def model_dump_pandas(self) -> pd.DataFrame:
        events_dict = self.model_dump(exclude_none=True)["events"]
        df = pd.json_normalize(events_dict)
        return df

    def shots(self) -> list[Shot]:
        return [event for event in self.events if isinstance(event, Shot)]

    def passes(self) -> list[Pass]:
        return [event for event in self.events if isinstance(event, Pass)]

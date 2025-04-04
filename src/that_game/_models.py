from datetime import datetime as datetimelib
from typing import Any, Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, computed_field

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
    jersey_number: int | None = None


class Team(BaseModel):
    id: str
    name: str
    color: str | None = None


class Pitch(BaseModel):
    model_config = ConfigDict(frozen=True)

    length: float = 105
    width: float = 68
    length_direction: Literal["left", "right"] = "right"
    width_direction: Literal["up", "down"] = "up"
    vertical: bool = False
    height_scale_to_meter: float = Field(default=1.0, gt=0)
    goal_width: float = 7.32
    goal_height: float = 2.44

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

        if self.pitch.vertical != pitch.vertical:
            self.x, self.y = self.y, self.x
            length = self.pitch.width
            width = self.pitch.length
            if self.pitch.width_direction == "up":
                length_direction = "right"
            else:
                length_direction = "left"
            if self.pitch.length_direction == "right":
                width_direction = "down"
            else:
                width_direction = "up"
        else:
            length = self.pitch.length
            width = self.pitch.width
            length_direction = self.pitch.length_direction
            width_direction = self.pitch.width_direction

        self.x *= pitch.length / length
        self.y *= pitch.width / width
        if self.z is not None:
            self.z *= pitch.height_scale_to_meter / self.pitch.height_scale_to_meter

        if length_direction != pitch.length_direction:
            self.x = pitch.length - self.x
        if width_direction != pitch.width_direction:
            self.y = pitch.width - self.y

        self.pitch = pitch


class RelatedPlayer(BaseModel):
    team: Team
    player: Player
    location: Location


class Event(BaseModel):
    id: str
    type: EventType
    period: Period
    seconds: float
    team: Team
    player: Player
    related_players: Sequence[RelatedPlayer] | None = None
    location: Location


class Shot(Event):
    end_location: Location
    pattern: ShotPattern
    body_part: BodyPart
    result: ShotResult
    xg: float | None = None


class Pass(Event):
    end_location: Location
    result: PassResult
    body_part: BodyPart
    pattern: PassPattern


class Game(BaseModel):
    id: str
    datetime: datetimelib | None = None
    competition: Competition | None = None
    home_team: Team
    away_team: Team
    home_players: Sequence[Player]
    away_players: Sequence[Player]
    events: Sequence[Any]

    @computed_field  # type: ignore
    @property
    def date(self) -> str | None:
        if self.datetime is None:
            return None
        return self.datetime.strftime("%Y-%m-%d")

    def shots(self) -> list[Shot]:
        return [event for event in self.events if isinstance(event, Shot)]

    def passes(self) -> list[Pass]:
        return [event for event in self.events if isinstance(event, Pass)]

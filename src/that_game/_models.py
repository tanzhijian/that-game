from datetime import datetime
from typing import Any, Literal, Sequence

import pandas as pd
from pydantic import BaseModel, Field, computed_field, model_validator
from pydantic.main import IncEx
from typing_extensions import Self

from ._status import (
    BodyPart,
    EventType,
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
    pitch: Pitch = Field(exclude=True)

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
        if self.z is not None and not is_float_close(
            pitch.height_scale_to_meter, self.pitch.height_scale_to_meter
        ):
            self.z = self.z * pitch.height_scale_to_meter

        if pitch.length_direction == "left":
            self.x = pitch.length - self.x
        if pitch.width_direction == "down":
            self.y = pitch.width - self.y
        self.pitch = pitch

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )


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
        events_dict = self.model_dump()["events"]
        df = pd.json_normalize(events_dict)
        return df

    def shots(self) -> list[Shot]:
        return [event for event in self.events if isinstance(event, Shot)]

    def passes(self) -> list[Pass]:
        return [event for event in self.events if isinstance(event, Pass)]

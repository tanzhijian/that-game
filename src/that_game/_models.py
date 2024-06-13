import typing
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum

import arrow
import pandas as pd

from ._status import BodyPart, EventType, ShotResult


@dataclass
class Metadata:
    def to_dict(self) -> dict[str, typing.Any]:
        return asdict(self)


@dataclass
class Competition(Metadata):
    id: str
    name: str


@dataclass
class Player(Metadata):
    id: str
    name: str
    role: str


@dataclass
class Team(Metadata):
    id: str
    name: str


@dataclass
class Playground(Metadata):
    length: int
    width: int


class Position:
    def __init__(
        self,
        x: float,
        y: float,
        playground: Playground | dict[str, typing.Any],
    ) -> None:
        self.x = x
        self.y = y
        self.playground = get_instance(playground, Playground)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "x": self.x,
            "y": self.y,
            "playground": self.playground.to_dict(),
        }

    def transform(
        self,
        playground: Playground | dict[str, typing.Any],
    ) -> "Position":
        playground = get_instance(playground, Playground)
        x_ratio = playground.length / self.playground.length
        y_ratio = playground.width / self.playground.width
        return Position(
            x=self.x * x_ratio,
            y=self.y * y_ratio,
            playground=playground,
        )


class Event:
    def __init__(
        self,
        id: str,
        type: EventType | str,
        timestamp: float,
        team: Team | dict[str, typing.Any],
        player: Player | dict[str, typing.Any],
        position: Position | dict[str, typing.Any],
        body_part: BodyPart | str,
        result: ShotResult | str,
    ) -> None:
        self.id = id
        self.type = get_enum(type, EventType)
        self.timestamp = timestamp
        self.team = get_instance(team, Team)
        self.player = get_instance(player, Player)
        self.position = get_instance(position, Position)
        self.body_part = get_enum(body_part, BodyPart)
        self.result = get_enum(result, ShotResult)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "team": self.team.to_dict(),
            "player": self.player.to_dict(),
            "position": self.position.to_dict(),
            "body_part": self.body_part.value,
            "result": self.result.value,
        }


class Game:
    def __init__(
        self,
        id: str,
        datetime: datetime | str,
        playground: Playground,
        home_team: Team,
        away_team: Team,
        home_players: list[Player],
        away_players: list[Player],
        competition: Competition,
        events: list[Event],
    ) -> None:
        self.id = id
        self.datetime = arrow.get(datetime)
        self.playground = playground
        self.home_team = home_team
        self.away_team = away_team
        self.home_players = home_players
        self.away_players = away_players
        self.competition = competition
        self.events = events

    @property
    def date(self) -> str:
        return self.datetime.strftime("%Y-%m-%d")

    @property
    def time(self) -> str:
        return self.datetime.strftime("%H:%M")

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "datetime": self.datetime,
            "date": self.date,
            "time": self.time,
            "playground": self.playground.to_dict(),
            "home_team": self.home_team.to_dict(),
            "away_team": self.away_team.to_dict(),
            "home_players": [player.to_dict() for player in self.home_players],
            "away_players": [player.to_dict() for player in self.away_players],
            "competition": self.competition.to_dict(),
            "events": [event.to_dict() for event in self.events],
        }

    def to_pandas(self) -> pd.DataFrame:
        events_dict = self.to_dict()["events"]
        df = pd.json_normalize(events_dict)
        return df


T = typing.TypeVar("T")
U = typing.TypeVar("U", bound=Enum)


def get_instance(obj: T | dict[str, typing.Any], cls: type[T]) -> T:
    if isinstance(obj, dict):
        return cls(**obj)
    return obj


def get_enum(obj: U | str, cls: type[U]) -> U:
    if isinstance(obj, str):
        return cls(obj)
    return obj

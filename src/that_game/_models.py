import typing
from dataclasses import asdict, dataclass
from datetime import datetime

import arrow
import pandas as pd

from ._status import BodyPart, EventType, ShotResult


@dataclass
class _Metadata:
    def to_dict(self) -> dict[str, typing.Any]:
        return asdict(self)


@dataclass
class Competition(_Metadata):
    id: str
    name: str


@dataclass
class Player(_Metadata):
    id: str
    name: str
    role: str


@dataclass
class Team(_Metadata):
    id: str
    name: str


@dataclass
class Playground(_Metadata):
    length: int
    width: int


class Position:
    def __init__(
        self,
        x: float,
        y: float,
        playground: Playground,
    ) -> None:
        self.x = x
        self.y = y
        self.playground = playground

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "x": self.x,
            "y": self.y,
            "playground": self.playground.to_dict(),
        }

    def transform(self, playground: Playground) -> "Position":
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
        type: EventType,
        timestamp: float,
        team: Team,
        player: Player,
        position: Position,
        body_part: BodyPart,
        result: ShotResult,
    ) -> None:
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.team = team
        self.player = player
        self.position = position
        self.body_part = body_part
        self.result = result

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

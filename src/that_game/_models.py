import typing
from dataclasses import asdict, dataclass
from datetime import datetime

import arrow
import pandas as pd

from ._metadata import Competition, Player, Playground, Team
from ._status import BodyPart, EventType, ShotResult
from ._types import DateTimeTypes


@dataclass
class Position:
    x: float
    y: float
    playground: Playground

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
            "team": asdict(self.team),
            "player": asdict(self.player),
            "position": asdict(self.position),
            "body_part": self.body_part.value,
            "result": self.result.value,
        }


class Game:
    def __init__(
        self,
        id: str,
        datetime: DateTimeTypes,
        playground: Playground,
        home_team: Team,
        away_team: Team,
        home_players: list[Player],
        away_players: list[Player],
        competition: Competition,
        events: list[Event],
    ) -> None:
        self.id = id
        self.datetime = self._parse_datetime(datetime)
        self.playground = playground
        self.home_team = home_team
        self.away_team = away_team
        self.home_players = home_players
        self.away_players = away_players
        self.competition = competition
        self.events = events

    def _parse_datetime(self, dt: DateTimeTypes) -> datetime:
        if isinstance(dt, str):
            return arrow.get(dt).datetime
        return dt

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "datetime": self.datetime,
            "date": self.date,
            "time": self.time,
            "playground": asdict(self.playground),
            "home_team": asdict(self.home_team),
            "away_team": asdict(self.away_team),
            "home_players": [asdict(player) for player in self.home_players],
            "away_players": [asdict(player) for player in self.away_players],
            "competition": asdict(self.competition),
            "events": [event.to_dict() for event in self.events],
        }

    @property
    def date(self) -> str:
        return self.datetime.strftime("%Y-%m-%d")

    @property
    def time(self) -> str:
        return self.datetime.strftime("%H:%M")

    def to_pandas(self) -> pd.DataFrame:
        events_dict = self.to_dict()["events"]
        df = pd.json_normalize(events_dict)
        return df

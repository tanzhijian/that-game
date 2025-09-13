from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Generic, Self, TypeVar

import polars as pl

from ._utils import transform_schema, validate_schema


@dataclass
class Pitch:
    length: float
    width: float


@dataclass
class Record(ABC):
    id_: str

    custom_pl_schema: ClassVar[dict[str, type[pl.DataType]]]


@dataclass
class Competition(Record):
    name: str
    season_id: str
    season_name: str | None
    country: str | None


@dataclass
class Team(Record):
    name: str
    color: str | None


@dataclass
class Player(Record):
    name: str
    team_id: str
    position: str | None
    number: int | None

    custom_pl_schema = {"number": pl.Int8}


@dataclass
class GameInfo(Record):
    date: str
    time: str
    home_team_id: str
    away_team_id: str
    competition_id: str
    season_id: str | None
    home_score: int | None
    away_score: int | None

    custom_pl_schema = {"home_score": pl.Int8, "away_score": pl.Int8}


@dataclass
class Event(Record):
    game_id: str
    type_: str
    time: str
    player_id: str
    team_id: str
    x: float
    y: float
    part: int

    custom_pl_schema = {
        "game_id": pl.Categorical,
        "type_": pl.Categorical,
        "team_id": pl.Categorical,
        "player_id": pl.Categorical,
    }


@dataclass
class Shot(Event):
    pass


@dataclass
class Frame(Record):
    player_id: str
    team_id: str
    x: float
    y: float
    time: str


R = TypeVar("R", bound=Record)


class Records(Generic[R]):
    def __init__(self, df: pl.DataFrame, model: type[R]) -> None:
        self._model = model
        self._validate(df)
        self._df = self._preprocess(df)

    @property
    def model(self) -> type[R]:
        return self._model

    @property
    def required_schema(self) -> dict[str, type[pl.DataType]]:
        return transform_schema(self._model)

    def _validate(self, df: pl.DataFrame) -> None:
        validate_schema(df, self.required_schema)

    def _preprocess(self, df: pl.DataFrame) -> pl.DataFrame:
        return df

    @property
    def df(self) -> pl.DataFrame:
        return self._df

    def export(self) -> dict[str, R]:
        return {row["id_"]: self._model(**row) for row in self.df.to_dicts()}

    def find(self, id_: str) -> R | None:
        row = self.df.filter(pl.col("id_") == id_).to_dicts()
        if row:
            return self._model(**row[0])
        return None

    def sample(self) -> R:
        row = self.df.sample(n=1).to_dicts()
        return self._model(**row[0])

    def __add__(self, other: object) -> Self:
        if type(other) is not type(self):
            raise TypeError(
                "Can only add Records with another Records instance"
            )
        if self._model != other.model:
            raise ValueError("Cannot add with different models")
        return type(self)(
            pl.concat([self.df, other.df], how="vertical"), self._model
        )


E = TypeVar("E", bound=Event)


class BaseEvents(Records[E], Generic[E], ABC):
    def __init__(self, df: pl.DataFrame, model: type[E], pitch: Pitch) -> None:
        super().__init__(df, model)
        self._pitch = pitch

    def __add__(self, other: object) -> Self:
        if not isinstance(other, BaseEvents):
            raise TypeError(
                "Can only add BaseEvents with another BaseEvents instance"
            )
        if self._model != other.model:
            raise ValueError("Cannot add with different models")
        if self._pitch != other.pitch:
            raise ValueError("Cannot add with different pitches")
        return type(self)(
            pl.concat([self.df, other.df], how="vertical"),
            self._model,
            self._pitch,
        )

    @property
    def pitch(self) -> Pitch:
        return self._pitch

    @property
    def teams_id(self) -> list[str]:
        return self._df["team_id"].to_list()

    @property
    def players_id(self) -> list[str]:
        return self._df["player_id"].to_list()

    @property
    def xs(self) -> list[float]:
        return self._df["x"].to_list()

    @property
    def ys(self) -> list[float]:
        return self._df["y"].to_list()

    def filter_by_type(self, type_: str) -> pl.DataFrame:
        return self.df.filter(pl.col("type_") == type_)

    def transform_locations(self, pitch: Pitch) -> None:
        raise NotImplementedError


class Events(BaseEvents[Event]):
    def __init__(self, df: pl.DataFrame, pitch: Pitch) -> None:
        self._model = Event
        super().__init__(df, self._model, pitch)

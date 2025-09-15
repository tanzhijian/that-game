from abc import ABC, abstractmethod
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

    def _ensure_compatible(self, obj: Self) -> None:
        if type(obj) is not type(self):
            raise TypeError(
                (
                    f"Can only add {type(self).__name__} with another "
                    f"{type(self).__name__} instance"
                )
            )
        if self._model != obj.model:
            raise ValueError("Cannot add with different models")

    def _concat_with(self, other: Self) -> Self:
        return type(self)(
            pl.concat([self.df, other.df], how="vertical"), self._model
        )

    def __add__(self, other: Self) -> Self:
        self._ensure_compatible(other)
        return self._concat_with(other)


E = TypeVar("E", bound=Event)


class BaseEvents(Records[E], Generic[E], ABC):
    def __init__(self, df: pl.DataFrame, model: type[E], pitch: Pitch) -> None:
        super().__init__(df, model)
        self._pitch = pitch

    def _ensure_compatible(self, obj: Self) -> None:
        super()._ensure_compatible(obj)
        if self._pitch != obj.pitch:
            raise ValueError("Cannot add with different pitches")

    @abstractmethod
    def _concat_with(self, other: Self) -> Self:
        raise NotImplementedError

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

    def find_next(self, event_id: str) -> E | None:
        raise NotImplementedError

    def find_prev(self, event_id: str) -> E | None:
        raise NotImplementedError

    def transform_locations(self, pitch: Pitch) -> None:
        raise NotImplementedError


class Part(BaseEvents[Event]):
    def __init__(self, df: pl.DataFrame, pitch: Pitch) -> None:
        self._model = Event
        super().__init__(df, self._model, pitch)

    def _validate(self, df: pl.DataFrame) -> None:
        super()._validate(df)
        parts = df["part"].unique()
        if len(parts) != 1:
            raise ValueError(
                "DataFrame must contain events from a single part"
            )

    def _concat_with(self, other: "Part") -> "Part":
        return Part(
            pl.concat([self.df, other.df], how="vertical"), self._pitch
        )


class Shots(BaseEvents[Shot]):
    def __init__(self, df: pl.DataFrame, pitch: Pitch) -> None:
        self._model = Shot
        super().__init__(df, self._model, pitch)

    def _concat_with(self, other: "Shots") -> "Shots":
        return Shots(
            pl.concat([self.df, other.df], how="vertical"), self._pitch
        )

    def _validate(self, df: pl.DataFrame) -> None:
        super()._validate(df)
        if not all(df["type_"] == "shot"):
            raise ValueError("All events must be of type 'shot'")

    @property
    def end_xs(self) -> list[float]:
        raise NotImplementedError

    @property
    def end_ys(self) -> list[float]:
        raise NotImplementedError

    def get_xg_features(self) -> pl.DataFrame:
        raise NotImplementedError

    def get_xg_label(self) -> pl.DataFrame:
        raise NotImplementedError

    def filter_goals(self) -> "Shots":
        raise NotImplementedError


class Events(BaseEvents[Event]):
    def __init__(self, df: pl.DataFrame, pitch: Pitch) -> None:
        self._model = Event
        super().__init__(df, self._model, pitch)

    def _concat_with(self, other: "Events") -> "Events":
        return Events(
            pl.concat([self.df, other.df], how="vertical"), self._pitch
        )

    def sample_part(self) -> Part:
        part_number = (
            self.df.select(pl.col("part").unique())
            .sample(n=1)
            .to_dicts()[0]["part"]
        )
        part_df = self.df.filter(pl.col("part") == part_number)
        return Part(part_df, self._pitch)

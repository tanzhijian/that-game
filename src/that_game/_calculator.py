from typing import Sequence

import pandas as pd

from ._models import Shot


class BaseXG:
    """Only distance and angle"""

    def __init__(self, shots: Sequence[Shot]) -> None:
        self._shots = shots

    @property
    def _x(self) -> pd.Series:
        xs = []
        ids = []
        for shot in self._shots:
            xs.append(shot.location.x)
            ids.append(shot.id)
        return pd.Series(xs, index=ids, name="x")

    @property
    def _y(self) -> pd.Series:
        ys = []
        ids = []
        for shot in self._shots:
            ys.append(shot.location.y)
            ids.append(shot.id)
        return pd.Series(ys, index=ids, name="y")

    @property
    def _c(self) -> pd.Series:
        width = self._shots[0].location.pitch.width
        c = abs(width - self._y)
        c.name = "c"
        return c

    def distance(self) -> pd.Series:
        pass

    def angle(self) -> pd.Series:
        pass

    def features(self) -> pd.DataFrame:
        pass

    def label(self) -> pd.Series:
        pass


class XG(BaseXG):
    """Include:

    * shot type: One of open play, free kick (if within 10 seconds of a free kick),
        corner (if within 10 seconds of a corner) or throw-in (if within 20 seconds
        of an attacking throw-in. The closest event is taken for set-pieces
        when there is more than one event in the timeframe.
    * x
    * y
    * body part
    * distance
    * angle
    * opponents in angle
    * teammates in angle
    * foot: strong foot
    * one on one
    * under pressure

    * goalkeeper x
    * goalkeeper y
    * shot to goalkeeper distance
    * is open goal: Whether the shot was taken into an open goal (no defending players)

    * carry length?
    * pass type?: cross, through ball, cut-back, switch
    * assist type?: The assist type, which is one of pass, recovery, clearance, direct,
        or rebound
    * counterattack?
    * fast break?
    """

    def __init__(self, shots: Sequence[Shot]) -> None:
        super().__init__(shots)

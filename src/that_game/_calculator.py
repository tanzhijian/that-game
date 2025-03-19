from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import numpy.typing as npt
from sklearn.linear_model import LogisticRegression

from ._models import Shot


class BaseXGInput:
    """Only distance and angle"""

    def __init__(self, shots: Sequence[Shot]) -> None:
        self._shots = shots

        xs = []
        ys = []
        labels = []
        for shot in shots:
            xs.append(shot.location.x)
            ys.append(shot.location.y)
            labels.append(shot.result == "goal")
        self._x: npt.NDArray[np.float64] = np.array(xs)
        self._y: npt.NDArray[np.float64] = np.array(ys)
        self._label: npt.NDArray[np.bool_] = np.array(labels)

    @property
    def _cal_x(self) -> npt.NDArray[np.float64]:
        length = self._shots[0].location.pitch.length
        return length - self._x

    @property
    def _cal_c(self) -> npt.NDArray[np.float64]:
        width = self._shots[0].location.pitch.width
        c: npt.NDArray[np.float64] = np.abs(width / 2 - self._y)
        return c

    @property
    def x(self) -> npt.NDArray[np.float64]:
        return self._x

    @property
    def y(self) -> npt.NDArray[np.float64]:
        return self._y

    @property
    def distance(self) -> npt.NDArray[np.float64]:
        return np.sqrt(self._cal_x**2 + self._cal_c**2)

    @property
    def angle(self) -> npt.NDArray[np.float64]:
        angle = (
            np.where(
                np.arctan(
                    7.32
                    * self._cal_x
                    / (self._cal_x**2 + self._cal_c**2 - (7.32 / 2) ** 2)
                )
                >= 0,
                np.arctan(
                    7.32
                    * self._cal_x
                    / (self._cal_x**2 + self._cal_c**2 - (7.32 / 2) ** 2)
                ),
                np.arctan(
                    7.32
                    * self._cal_x
                    / (self._cal_x**2 + self._cal_c**2 - (7.32 / 2) ** 2)
                )
                + np.pi,
            )
            * 180
            / np.pi
        )
        return angle

    @property
    def features(self) -> npt.NDArray[np.float64]:
        return np.column_stack((self.distance, self.angle))

    @property
    def label(self) -> npt.NDArray[np.bool_]:
        return self._label


class XGInput(BaseXGInput):
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


class XGModel:
    def __init__(self) -> None:
        self._model: LogisticRegression | None = None

    def load(self, path: Path) -> None:
        self._model = joblib.load(path)

    def save(self, path: Path) -> None:
        if self._model is None:
            raise ValueError("Model is not trained or loaded yet.")
        joblib.dump(self._model, path)

    def train(self, xg_input: BaseXGInput) -> None:
        if self._model is not None:
            raise ValueError("Model is already trained.")
        self._model = LogisticRegression()
        self._model.fit(xg_input.features, xg_input.label)

    def predict(self, xg_input: BaseXGInput) -> npt.NDArray[np.float64]:
        if self._model is None:
            raise ValueError("Model is not trained or loaded yet.")
        results: npt.NDArray[np.float64] = self._model.predict_proba(xg_input.features)[
            :, 1
        ]
        return results

    def calculate_xg(self, shot: Shot) -> Shot:
        shot.xg = self.predict(BaseXGInput([shot]))[0]
        return shot

from typing import Sequence, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mplsoccer import Pitch as MPLPitchLib
from mplsoccer import VerticalPitch as MPLVerticalPitchLib

from ._models import Location, Pitch, Shot


def _mpl_pitch_factory(pitch: Pitch) -> MPLPitchLib | MPLVerticalPitchLib:
    if pitch.vertical:
        Lib = MPLVerticalPitchLib
    else:
        Lib = MPLPitchLib
    return Lib(
        pitch_type="custom",
        pitch_length=pitch.length,
        pitch_width=pitch.width,
        axis=True,
        label=True,
    )


def _create_mpl_pitch_and_ax(
    pitch: Pitch,
) -> tuple[MPLPitchLib | MPLVerticalPitchLib, Axes]:
    mpl_pitch = _mpl_pitch_factory(pitch)
    _, ax = mpl_pitch.draw()
    ax = cast(Axes, ax)

    if pitch.length_direction == "left":
        ax.invert_xaxis()
    if pitch.width_direction == "down":
        ax.invert_yaxis()
    return mpl_pitch, ax


class PitchVisualization:
    def __init__(self, pitch: Pitch) -> None:
        self.pitch = pitch

    def show(self) -> None:
        _create_mpl_pitch_and_ax(self.pitch)
        plt.show()


class LocationVisualization:
    def __init__(self, location: Location) -> None:
        self.location = location

    def show(self) -> None:
        mpl_pitch, ax = _create_mpl_pitch_and_ax(self.location.pitch)
        mpl_pitch.scatter(x=self.location.x, y=self.location.y, s=500, ax=ax)
        plt.show()


class ShotVisualization:
    def __init__(self, shot: Shot) -> None:
        self.shot = shot

    def show(self) -> None:
        mpl_pitch, ax = _create_mpl_pitch_and_ax(self.shot.location.pitch)
        mpl_pitch.scatter(
            x=self.shot.location.x,
            y=self.shot.location.y,
            s=500,
            ax=ax,
        )
        mpl_pitch.lines(
            self.shot.location.x,
            self.shot.location.y,
            self.shot.end_location.x,
            self.shot.end_location.y,
            ax=ax,
            color="blue",
        )
        plt.show()


class ShotsVisualization:
    def __init__(self, shots: Sequence[Shot]) -> None:
        self.shots = shots

    def show(self) -> None:
        mpl_pitch, ax = _create_mpl_pitch_and_ax(self.shots[0].location.pitch)
        for shot in self.shots:
            mpl_pitch.scatter(
                x=shot.location.x,
                y=shot.location.y,
                s=500,
                ax=ax,
            )
            mpl_pitch.lines(
                shot.location.x,
                shot.location.y,
                shot.end_location.x,
                shot.end_location.y,
                ax=ax,
                color="blue",
            )
        plt.show()

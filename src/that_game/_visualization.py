from typing import Sequence, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mplsoccer import Pitch as MPLPitchLib
from mplsoccer import VerticalPitch as MPLVerticalPitchLib
from mplsoccer._pitch_plot import BasePitchPlot

from ._models import Location, Pitch, Shot, Team


class _Colors:
    background = "#f8f9fa"
    divide = "#dee2e6"
    home_team = "#dc3545"
    away_team = "#0d6efd"
    line = "#198754"


def _mpl_pitch_factory(pitch: Pitch) -> BasePitchPlot:
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
        pitch_color=_Colors.background,
        line_color=_Colors.divide,
    )


def _create_mpl_pitch_and_ax(
    pitch: Pitch,
) -> tuple[BasePitchPlot, Axes]:
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
        mpl_pitch.scatter(x=self.location.x, y=self.location.y, s=100, ax=ax)
        plt.show()


class ShotVisualization:
    def __init__(self, shot: Shot) -> None:
        self.shot = shot

    @property
    def _team_color(self) -> str:
        if (color := self.shot.team.color) is not None:
            return color
        return _Colors.home_team

    def show(self) -> None:
        mpl_pitch, ax = _create_mpl_pitch_and_ax(self.shot.location.pitch)
        mpl_pitch.scatter(
            x=self.shot.location.x,
            y=self.shot.location.y,
            s=100,
            color=self._team_color,
            ax=ax,
        )

        if (jersey_number := self.shot.player.jersey_number) is not None:
            mpl_pitch.annotate(
                text=jersey_number,
                xy=(
                    self.shot.location.x + 0.2,
                    self.shot.location.y + 0.2,
                ),
                ax=ax,
                color="white",
                ha="center",
                va="center",
                fontsize=7,
            )

        mpl_pitch.lines(
            self.shot.location.x,
            self.shot.location.y,
            self.shot.end_location.x,
            self.shot.end_location.y,
            color=_Colors.line,
            lw=1,
            ax=ax,
        )

        if self.shot.related_players is not None:
            for player in self.shot.related_players:
                if player.team.name == self.shot.team.name:
                    mpl_pitch.scatter(
                        x=player.location.x,
                        y=player.location.y,
                        s=100,
                        ax=ax,
                        color=_Colors.home_team,
                        alpha=0.7,
                    )
                else:
                    mpl_pitch.scatter(
                        x=player.location.x,
                        y=player.location.y,
                        s=100,
                        ax=ax,
                        color=_Colors.away_team,
                        alpha=0.7,
                    )
        plt.show()


class ShotsVisualization:
    def __init__(self, shots: Sequence[Shot]) -> None:
        self.shots = shots
        self._home_taem: Team | None = None

    def _team_color(self, team: Team) -> str:
        if team.color is not None:
            return team.color
        if self._home_taem is None:
            self._home_taem = team
            return _Colors.home_team
        if self._home_taem == team:
            return _Colors.home_team
        return _Colors.away_team

    def show(self) -> None:
        mpl_pitch, ax = _create_mpl_pitch_and_ax(self.shots[0].location.pitch)
        for shot in self.shots:
            mpl_pitch.scatter(
                x=shot.location.x,
                y=shot.location.y,
                s=100,
                ax=ax,
                color=self._team_color(shot.team),
            )
            mpl_pitch.lines(
                shot.location.x,
                shot.location.y,
                shot.end_location.x,
                shot.end_location.y,
                color=_Colors.line,
                lw=1,
                ax=ax,
            )
        plt.show()

    def xg(self) -> None:
        return

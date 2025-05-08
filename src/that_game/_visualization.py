from typing import Sequence

from ._models import Location, Pitch, Shot, Team


class _Colors:
    background = "#f8f9fa"
    divide = "#dee2e6"
    home_team = "#dc3545"
    away_team = "#0d6efd"
    line = "#198754"


class PitchVisualization:
    def __init__(self, pitch: Pitch) -> None:
        self.pitch = pitch

    def show(self) -> None:
        pass


class LocationVisualization:
    def __init__(self, location: Location) -> None:
        self.location = location

    def show(self) -> None:
        pass


class ShotVisualization:
    def __init__(self, shot: Shot) -> None:
        self.shot = shot

    @property
    def _team_color(self) -> str:
        if (color := self.shot.team.color) is not None:
            return color
        return _Colors.home_team

    def show(self) -> None:
        pass


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
        pass

    def xg(self) -> None:
        return

import typing
from datetime import datetime

from ._metadata import Player

PlayerTypes = Player | dict[str, typing.Any]
DateTimeTypes = datetime | str

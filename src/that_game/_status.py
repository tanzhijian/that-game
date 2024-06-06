from enum import Enum


class EventType(Enum):
    SHOT = "shot"
    PASS = "pass"


class ShotResult(Enum):
    GOAL = "goal"
    SAVED = "saved"
    MISSED = "missed"
    POST = "post"
    BLOCKED = "blocked"
    OWN_GOAL = "own_goal"


class Period(Enum):
    FIRST_HALF = 1
    SECOND_HALF = 2
    FIRST_EXTRA = 3
    SECOND_EXTRA = 4
    PENALTY_SHOOTOUT = 5


class BodyPart(Enum):
    RIGHT_FOOT = 1
    LEFT_FOOT = 2
    HEAD = 3
    OTHER = 4


class ShotType(Enum):
    OPEN_PLAY = 1
    FREEKICK = 2
    PENALTY = 3

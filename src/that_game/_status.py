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
    FIRST_HALF = "1st"
    SECOND_HALF = "2nd"
    FIRST_EXTRA = "1st_et"
    SECOND_EXTRA = "2nd_et"
    PENALTY_SHOOTOUT = "pk"


class BodyPart(Enum):
    RIGHT_FOOT = "rf"
    LEFT_FOOT = "lf"
    HEAD = "head"
    OTHER = "other"


class ShotType(Enum):
    OPEN_PLAY = "open_play"
    FREEKICK = "freekick"
    PENALTY = "penalty"

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

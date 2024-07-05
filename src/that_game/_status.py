from typing import Literal

Period = Literal[
    "first_half",
    "second_half",
    "first_extra",
    "second_extra",
    "penalty_shootout",
]
BodyPart = Literal[
    "right_foot",
    "left_foot",
    "head",
    "hand",
    "other",
    "unknown",
]

ShotPattern = Literal["freekick", "penalty", "open_play"]
PassPattern = Literal["general", "high_pass"]

ShotResult = Literal[
    "goal",
    "saved",
    "missed",
    "post",
    "blocked",
    "own_goal",
]
PassResult = Literal["success", "fail"]

EventType = Literal["shot", "pass"]

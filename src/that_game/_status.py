from typing import Literal

Period = Literal[
    "first_half",
    "second_half",
    "first_extra",
    "second_extra",
    "penalty_shootout",
]
BodyPart = Literal["right_foot", "left_foot", "head", "other"]

ShotPattern = Literal["freekick", "penalty", "open_play"]

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

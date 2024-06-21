from typing import Literal

Period = Literal[
    "first_half",
    "second_half",
    "first_extra",
    "second_extra",
    "penalty_shootout",
]
BodyPart = Literal["right_foot", "left_foot", "head", "other"]

ShotResult = Literal[
    "goal",
    "saved",
    "missed",
    "post",
    "blocked",
    "own_goal",
]
PassResult = Literal["pass"]
Result = ShotResult | PassResult | Literal["other"]

EventType = Literal["shot", "pass"]

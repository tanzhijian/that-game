from dataclasses import dataclass


@dataclass
class Competition:
    id: str
    name: str


@dataclass
class Player:
    id: str
    name: str
    role: str


@dataclass
class Team:
    id: str
    name: str


@dataclass
class Playground:
    length: int
    width: int

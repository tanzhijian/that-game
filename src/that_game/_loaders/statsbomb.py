import json
import typing
from datetime import datetime

from .._models import (
    Competition,
    Event,
    Game,
    Location,
    Pass,
    Pitch,
    Player,
    Shot,
    Team,
)
from .._status import BodyPart, EventType, Period, ShotPattern, ShotResult


def load_statsbomb(
    game_id: str,
    matches: str,
    lineups: str,
    events: str,
    three_sixty: str | None = None,
) -> Game:
    loader = StatsBombLoader(game_id, matches, lineups, events, three_sixty)
    return loader.game


class StatsBombLoader:
    def __init__(
        self,
        game_id: str,
        matches: str,
        lineups: str,
        events: str,
        three_sixty: str | None = None,
    ) -> None:
        self._game_id = game_id

        self._raw_game = next(
            game
            for game in json.loads(matches)
            if str(game["match_id"]) == self._game_id
        )
        self._raw_lineups = json.loads(lineups)
        self._raw_events = json.loads(events)
        self._raw_three_sixty = (
            json.loads(three_sixty) if three_sixty is not None else None
        )

        self._teams = {
            (
                home_team_id := str(self._raw_game["home_team"]["home_team_id"])
            ): Team(
                id=home_team_id,
                name=self._raw_game["home_team"]["home_team_name"],
            ),
            (
                away_team_id := str(self._raw_game["away_team"]["away_team_id"])
            ): Team(
                id=away_team_id,
                name=self._raw_game["away_team"]["away_team_name"],
            ),
        }
        self._home_players, self._away_players = self._parse_players()
        self._competition = Competition(
            id=str(self._raw_game["competition"]["competition_id"]),
            name=self._raw_game["competition"]["competition_name"],
        )
        self._pitch = Pitch(length=120, width=80, y_direction="down")

    def _parse_players(self) -> tuple[dict[str, Player], dict[str, Player]]:
        p1, p2 = self._raw_lineups[0], self._raw_lineups[1]
        if str(p1["team_id"]) == next(iter(self._teams)):
            home, away = p1, p2
        else:
            home, away = p2, p1

        home_players = {
            str(player["player_id"]): self._parse_player(player)
            for player in home["lineup"]
        }
        away_players = {
            str(player["player_id"]): self._parse_player(player)
            for player in away["lineup"]
        }
        return home_players, away_players

    def _parse_player(self, player_dict: typing.Any) -> Player:
        try:
            position = player_dict["positions"][0]["position"]
        except IndexError:
            position = "bench"
        return Player(
            id=str(player_dict["player_id"]),
            name=player_dict["player_name"],
            position=position,
        )

    @property
    def home_team(self) -> Team:
        return list(self._teams.values())[0]

    @property
    def away_team(self) -> Team:
        return list(self._teams.values())[1]

    @property
    def home_players(self) -> list[Player]:
        return list(self._home_players.values())

    @property
    def away_players(self) -> list[Player]:
        return list(self._away_players.values())

    @property
    def competition(self) -> Competition:
        return self._competition

    @property
    def pitch(self) -> Pitch:
        return self._pitch

    def _find_player(self, player_id: str) -> Player:
        return (
            self._home_players.get(player_id) or self._away_players[player_id]
        )

    def _transform_timestamp(self, time_str: str) -> float:
        time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
        seconds = (
            time_obj.hour * 3600
            + time_obj.minute * 60
            + time_obj.second
            + time_obj.microsecond / 1e6
        )
        return seconds

    @property
    def events(self) -> list[Event]:
        events: list[Event] = []
        for event in self._raw_events:
            # 目前只处理两种事件，射门和传球
            if (type_ := EVENT_TYPES.get(event["type"]["name"])) is None:
                continue

            id_ = event["id"]
            period = PERIODS[event["period"]]
            seconds = self._transform_timestamp(event["timestamp"])
            team = self._teams[str(event["team"]["id"])]
            player = self._find_player(str(event["player"]["id"]))
            location = Location(
                x=event["location"][0],
                y=event["location"][1],
                pitch=self.pitch,
            )

            match type_:
                case "shot":
                    event = Shot(
                        id=id_,
                        type=type_,
                        period=period,
                        seconds=seconds,
                        team=team,
                        player=player,
                        location=location,
                        end_location=Location(
                            x=event["shot"]["end_location"][0],
                            y=event["shot"]["end_location"][1],
                            pitch=self.pitch,
                        ),
                        pattern=SHOT_PATTERNS[event["shot"]["type"]["name"]],
                        body_part=BODY_PARTS[
                            event["shot"]["body_part"]["name"]
                        ],
                        result=SHOT_RESULTS[event["shot"]["outcome"]["name"]],
                    )
                case "pass":
                    event = Pass(
                        id=id_,
                        type=type_,
                        period=period,
                        seconds=seconds,
                        team=team,
                        player=player,
                        location=location,
                        end_location=Location(
                            x=event["pass"]["end_location"][0],
                            y=event["pass"]["end_location"][1],
                            pitch=self.pitch,
                        ),
                        result="fail"
                        if event["pass"].get("outcome")
                        else "success",
                    )
                case _:
                    raise ValueError(f"Check event, index: {event['index']}")

            events.append(event)

        return events

    @property
    def game(self) -> Game:
        return Game(
            id=self._game_id,
            datetime=f"{self._raw_game['match_date']} {self._raw_game['kick_off']}",
            home_team=self.home_team,
            away_team=self.away_team,
            home_players=self.home_players,
            away_players=self.away_players,
            competition=self.competition,
            events=self.events,
        )


# 目前只处理两种事件，射门和传球
EVENT_TYPES: dict[str, EventType] = {
    "Pass": "pass",
    "Shot": "shot",
}
BODY_PARTS: dict[str, BodyPart] = {
    "Right Foot": "right_foot",
    "Left Foot": "left_foot",
    "Head": "head",
    "Other": "other",
}

SHOT_PATTERNS: dict[str, ShotPattern] = {
    "Corner": "freekick",
    "Free Kick": "freekick",
    "Open Play": "open_play",
    "Penalty": "penalty",
    "Kick Off": "open_play",
}
# 这里考虑需要使用 statsbomb 的 results 扩展词汇
SHOT_RESULTS: dict[str, ShotResult] = {
    "Goal": "goal",
    "Saved": "saved",
    "Off T": "missed",
    "Wayward": "missed",
    "Post": "post",
    "Blocked": "blocked",
    "Saved Off T": "saved",
    "Saved To Post": "saved",
}
PERIODS: dict[int, Period] = {
    1: "first_half",
    2: "second_half",
    3: "first_extra",
    4: "second_extra",
    5: "penalty_shootout",
}

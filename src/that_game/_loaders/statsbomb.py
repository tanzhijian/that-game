import json
import typing
from datetime import datetime

from .._models import (
    Competition,
    Event,
    Game,
    Location,
    Pitch,
    Player,
    Team,
)
from .._status import BodyPart, EventType, Result


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
        self._pitch = Pitch(length=120, width=80)

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
            if (type_ := event["type"]["name"]) not in EVENT_TYPES:
                continue

            # 先快速处理 KeyError，稍后再来分析具体数据
            try:
                player = self._find_player(str(event["player"]["id"]))
                location = Location(
                    x=event["location"][0],
                    y=event["location"][1],
                    pitch=self.pitch,
                )
            except KeyError:
                continue

            type_ = EVENT_TYPES[type_]
            # 目前只有 shot 和 pass
            try:
                if type_ == "shot":
                    body_part = (
                        BODY_PARTS.get(event["shot"]["body_part"]["name"])
                        or "other"
                    )
                else:
                    body_part = (
                        BODY_PARTS.get(event["pass"]["body_part"]["name"])
                        or "other"
                    )
            except KeyError:
                body_part = "other"

            try:
                if type_ == "shot":
                    result = (
                        RESULTS.get(event["shot"]["outcome"]["name"]) or "other"
                    )
                else:
                    result = (
                        RESULTS.get(event["pass"]["outcome"]["name"]) or "other"
                    )

            except KeyError:
                result = "other"

            events.append(
                Event(
                    id=event["id"],
                    type=type_,
                    seconds=self._transform_timestamp(event["timestamp"]),
                    team=self._teams[str(event["team"]["id"])],
                    player=player,
                    location=location,
                    body_part=body_part,
                    result=result,
                )
            )
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
# 这里考虑需要使用 statsbomb 的 results 扩展词汇
SHOT_RESULTS: dict[str, Result] = {
    "Goal": "goal",
    "Saved": "saved",
    "Off T": "missed",
    "Wayward": "missed",
    "Post": "post",
    "Blocked": "blocked",
    "Saved Off T": "saved",
    "Saved To Post": "saved",
}
PASS_RESULTS: dict[str, Result] = {
    "Incomplete": "pass",
    "Out": "pass",
    "Unknown": "pass",
    "Pass Offside": "pass",
}
RESULTS = SHOT_RESULTS | PASS_RESULTS

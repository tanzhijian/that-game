import json
from datetime import datetime
from typing import Any

from .._models import (
    Competition,
    Game,
    Location,
    Pass,
    Pitch,
    Player,
    RelatedPlayer,
    Shot,
    Team,
)
from .._status import (
    BodyPart,
    EventType,
    PassPattern,
    Period,
    ShotPattern,
    ShotResult,
)


def load_statsbomb(
    game_id: str,
    events: str,
    *,
    matches: str | None = None,
    lineups: str | None = None,
    three_sixty: str | None = None,
) -> Game:
    loader = StatsBombLoader(
        game_id,
        events,
        matches=matches,
        lineups=lineups,
        three_sixty=three_sixty,
    )
    return loader.game()


class StatsBombLoader:
    def __init__(
        self,
        game_id: str,
        events: str,
        *,
        matches: str | None = None,
        lineups: str | None = None,
        three_sixty: str | None = None,
    ) -> None:
        self._game_id = game_id
        self._three_sixty = three_sixty
        self._pitch = Pitch(length=120, width=80, width_direction="down")

        self._game_info = self._find_game_info(matches)
        self._teams = self._init_teams()
        self._players = self._init_players(lineups)
        self._events = self._init_events(events)

    def _find_game_info(self, raw_matches: str | None) -> Any | None:
        if raw_matches is None:
            return None
        for game in json.loads(raw_matches):
            if str(game["match_id"]) == self._game_id:
                return game
        raise ValueError(f"Game {self._game_id} not found")

    def _init_teams(self) -> dict[str, Team]:
        if self._game_info is None:
            return {}

        home_team_id = str(self._game_info["home_team"]["home_team_id"])
        home_team = Team(
            id=home_team_id,
            name=self._game_info["home_team"]["home_team_name"],
        )
        away_team_id = str(self._game_info["away_team"]["away_team_id"])
        away_team = Team(
            id=away_team_id,
            name=self._game_info["away_team"]["away_team_name"],
        )
        return {
            home_team_id: home_team,
            away_team_id: away_team,
        }

    def _init_players(self, raw_lineups: str | None) -> dict[str, tuple[str, Player]]:
        if raw_lineups is None:
            return {}

        players: dict[str, tuple[str, Player]] = {}
        for team in json.loads(raw_lineups):
            team_id = str(team["team_id"])
            for player in team["lineup"]:
                player_id = str(player["player_id"])

                try:
                    position = player["positions"][0]["position"]
                except IndexError:
                    position = "bench"

                players[player_id] = (
                    team_id,
                    Player(
                        id=player_id,
                        name=player["player_name"],
                        position=position,
                        jersey_number=player["jersey_number"],
                    ),
                )
        return players

    def _select_players(self, team_id: str) -> list[Player]:
        return [player[1] for player in self._players.values() if player[0] == team_id]

    def _find_player(self, player_id: str) -> Player:
        return self._players[player_id][1]

    def _transform_timestamp(self, time_str: str) -> float:
        time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
        seconds = (
            time_obj.hour * 3600
            + time_obj.minute * 60
            + time_obj.second
            + time_obj.microsecond / 1e6
        )
        return seconds

    def _parse_common_fields(
        self, raw_event: dict[str, Any]
    ) -> tuple[str, Period, float, Team, Player, Location]:
        id_ = raw_event["id"]
        period = PERIODS[raw_event["period"]]
        seconds = self._transform_timestamp(raw_event["timestamp"])
        team = self._teams[str(raw_event["team"]["id"])]
        player = self._find_player(str(raw_event["player"]["id"]))
        location = Location(
            x=raw_event["location"][0],
            y=raw_event["location"][1],
            pitch=self.pitch,
        )
        return id_, period, seconds, team, player, location

    def _parse_shot(self, raw_event: dict[str, Any]) -> Shot:
        id_, period, seconds, team, player, location = self._parse_common_fields(
            raw_event
        )
        raw_shot = raw_event["shot"]

        try:
            z = raw_shot["end_location"][2]
        except IndexError:
            z = None

        try:
            related_players = []
            for item in raw_shot["freeze_frame"]:
                related_team = team
                if not item["teammate"]:
                    another_team_id = next(
                        id_ for id_ in self._teams if id_ != related_team.id
                    )
                    related_team = self._teams[another_team_id]

                related_players.append(
                    RelatedPlayer(
                        team=related_team,
                        player=self._find_player(str(item["player"]["id"])),
                        location=Location(
                            x=item["location"][0],
                            y=item["location"][1],
                            pitch=self.pitch,
                        ),
                    )
                )
        except KeyError:
            related_players = None

        return Shot(
            id=id_,
            type="shot",
            period=period,
            seconds=seconds,
            team=team,
            player=player,
            related_players=related_players,
            location=location,
            end_location=Location(
                x=raw_shot["end_location"][0],
                y=raw_shot["end_location"][1],
                z=z,
                pitch=self.pitch,
            ),
            pattern=SHOT_PATTERNS[raw_shot["type"]["name"]],
            body_part=BODY_PARTS[raw_shot["body_part"]["name"]],
            result=SHOT_RESULTS[raw_shot["outcome"]["name"]],
            xg=raw_shot["statsbomb_xg"],
        )

    def _parse_pass(self, raw_event: dict[str, Any]) -> Pass:
        id_, period, seconds, team, player, location = self._parse_common_fields(
            raw_event
        )
        raw_pass = raw_event["pass"]
        result = "fail" if raw_pass.get("outcome") else "success"

        try:
            body_part_obj = raw_pass["body_part"]
        except KeyError:
            body_part = "unknown"
        else:
            body_part = BODY_PARTS[body_part_obj["name"]]

        return Pass(
            id=id_,
            type="pass",
            period=period,
            seconds=seconds,
            team=team,
            player=player,
            location=location,
            end_location=Location(
                x=raw_pass["end_location"][0],
                y=raw_pass["end_location"][1],
                pitch=self.pitch,
            ),
            result=result,
            body_part=body_part,
            pattern=PASS_PATTERNS[raw_pass["height"]["name"]],
        )

    def _init_events(self, raw_events: str) -> list[Any]:
        events = []
        for raw_event in json.loads(raw_events):
            team = raw_event["team"]
            if (team_id := str(team["id"])) not in self._teams:
                self._teams[team_id] = Team(id=team_id, name=team["name"])

            try:
                player = raw_event["player"]
                if (player_id := str(player["id"])) not in self._players:
                    position = raw_event["position"]["name"]
                    self._players[player_id] = (
                        team_id,
                        Player(
                            id=player_id,
                            name=player["name"],
                            position=position,
                        ),
                    )
            except KeyError:
                pass

            # 目前只处理两种事件，射门和传球
            try:
                type_ = EVENT_TYPES[raw_event["type"]["name"]]
            except KeyError:
                continue

            event: Any
            match type_:
                case "shot":
                    event = self._parse_shot(raw_event)
                case "pass":
                    event = self._parse_pass(raw_event)
                case _:
                    raise ValueError(f"Check event, index: {raw_event['index']}")

            events.append(event)
        return events

    @property
    def pitch(self) -> Pitch:
        return self._pitch

    def datetime(self) -> str | None:
        if self._game_info is None:
            return None
        return f"{self._game_info['match_date']} {self._game_info['kick_off']}"

    def competition(self) -> Competition | None:
        if self._game_info is None:
            return None
        return Competition(
            id=str(self._game_info["competition"]["competition_id"]),
            name=self._game_info["competition"]["competition_name"],
        )

    def home_team(self) -> Team:
        return list(self._teams.values())[0]

    def away_team(self) -> Team:
        return list(self._teams.values())[1]

    def home_players(self) -> list[Player]:
        return self._select_players(self.home_team().id)

    def away_players(self) -> list[Player]:
        return self._select_players(self.away_team().id)

    def events(self) -> list[Any]:
        return self._events

    def game(self) -> Game:
        return Game(
            id=self._game_id,
            datetime=self.datetime(),
            competition=self.competition(),
            home_team=self.home_team(),
            away_team=self.away_team(),
            home_players=self.home_players(),
            away_players=self.away_players(),
            events=self.events(),
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
    "Drop Kick": "other",
    "Keeper Arm": "hand",
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
PASS_PATTERNS: dict[str, PassPattern] = {
    "Ground Pass": "general",
    "Low Pass": "general",
    "High Pass": "high_pass",
}
PERIODS: dict[int, Period] = {
    1: "first_half",
    2: "second_half",
    3: "first_extra",
    4: "second_extra",
    5: "penalty_shootout",
}

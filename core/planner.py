class Planner:
    def __init__(self, config, parser):
        self.config = config
        self.parser = parser

    def _move_action_by_diff(self, diff):
        if diff is None:
            return {
                "name": "idle",
                "hold": 0.0,
                "reason": "diff_none",
                "target": None,
                "diff": None
            }

        if diff > 0:
            return {
                "name": "move_right",
                "hold": self.config.move_hold_time,
                "reason": "target_on_right",
                "target": None,
                "diff": diff
            }
        else:
            return {
                "name": "move_left",
                "hold": self.config.move_hold_time,
                "reason": "target_on_left",
                "target": None,
                "diff": diff
            }

    def plan(self, parsed):
        player = parsed["player"]

        if player is None:
            return {
                "name": "idle",
                "hold": 0.0,
                "reason": "no_player",
                "target": None,
                "diff": None
            }

        # 1. replay
        replay = self.parser.nearest_to_player(player, parsed["replays"])
        if replay is not None:
            diff = self.parser.x_diff(player, replay)
            if abs(diff) <= self.config.interact_x_threshold:
                return {
                    "name": "confirm",
                    "hold": self.config.confirm_hold_time,
                    "reason": "handle_replay",
                    "target": replay,
                    "diff": diff
                }
            action = self._move_action_by_diff(diff)
            action["reason"] = "move_to_replay"
            action["target"] = replay
            return action

        # 2. questionmark
        qmark = self.parser.nearest_to_player(player, parsed["questionmarks"])
        if qmark is not None:
            diff = self.parser.x_diff(player, qmark)
            if abs(diff) <= self.config.interact_x_threshold:
                return {
                    "name": "confirm",
                    "hold": self.config.confirm_hold_time,
                    "reason": "handle_questionmark",
                    "target": qmark,
                    "diff": diff
                }
            action = self._move_action_by_diff(diff)
            action["reason"] = "move_to_questionmark"
            action["target"] = qmark
            return action

        # 3. monster
        monster = self.parser.nearest_to_player(player, parsed["monsters"])
        if monster is not None:
            diff = self.parser.x_diff(player, monster)
            if abs(diff) <= self.config.attack_x_threshold:
                return {
                    "name": "attack",
                    "hold": self.config.attack_hold_time,
                    "reason": "attack_monster",
                    "target": monster,
                    "diff": diff
                }
            action = self._move_action_by_diff(diff)
            action["reason"] = "move_to_monster"
            action["target"] = monster
            return action

        # 4. item
        item = self.parser.nearest_to_player(player, parsed["items"])
        if item is not None:
            diff = self.parser.x_diff(player, item)
            if abs(diff) <= self.config.pickup_x_threshold:
                return {
                    "name": "pickup",
                    "hold": self.config.pickup_hold_time,
                    "reason": "pickup_item",
                    "target": item,
                    "diff": diff
                }
            action = self._move_action_by_diff(diff)
            action["reason"] = "move_to_item"
            action["target"] = item
            return action

        # 5. door
        door = self.parser.nearest_to_player(player, parsed["doors"])
        if door is not None:
            diff = self.parser.x_diff(player, door)
            if abs(diff) <= self.config.interact_x_threshold:
                return {
                    "name": "confirm",
                    "hold": self.config.confirm_hold_time,
                    "reason": "enter_door",
                    "target": door,
                    "diff": diff
                }
            action = self._move_action_by_diff(diff)
            action["reason"] = "move_to_door"
            action["target"] = door
            return action

        # 6. idle patrol
        if self.config.idle_patrol_direction == "left":
            return {
                "name": "move_left",
                "hold": self.config.move_hold_time,
                "reason": "idle_patrol_left",
                "target": None,
                "diff": None
            }

        return {
            "name": "move_right",
            "hold": self.config.move_hold_time,
            "reason": "idle_patrol_right",
            "target": None,
            "diff": None
        }
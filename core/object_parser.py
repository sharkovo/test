from math import hypot


class ObjectParser:
    def parse(self, objects):
        data = {
            "player": None,
            "doors": [],
            "items": [],
            "monsters": [],
            "obstacles": [],
            "questionmarks": [],
            "replays": [],
        }

        for obj in objects:
            n = obj["cls_name"]

            if n == "player":
                data["player"] = obj
            elif n == "door":
                data["doors"].append(obj)
            elif n == "item":
                data["items"].append(obj)
            elif n == "monster":
                data["monsters"].append(obj)
            elif n == "obstacle":
                data["obstacles"].append(obj)
            elif n == "questionmark":
                data["questionmarks"].append(obj)
            elif n == "replay":
                data["replays"].append(obj)

        return data

    def nearest_to_player(self, player, obj_list):
        if player is None or not obj_list:
            return None

        px, py = player["center"]

        def dist(obj):
            ox, oy = obj["center"]
            return hypot(ox - px, oy - py)

        return min(obj_list, key=dist)

    def x_diff(self, player, obj):
        if player is None or obj is None:
            return None
        px, _ = player["center"]
        ox, _ = obj["center"]
        return ox - px
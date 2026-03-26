import os
import json
import time
from math import hypot
from datetime import datetime

import cv2


class HardCaseMiner:
    def __init__(self, config):
        self.config = config
        self.last_save_time = 0.0
        self.player_missing_count = 0

        self.class_name_to_id = {
            name: cid for cid, name in self.config.class_id_to_name.items()
        }

        self.base_dir = self.config.auto_mine_dir
        self.image_dir = os.path.join(self.base_dir, "images")
        self.label_dir = os.path.join(self.base_dir, "labels")
        self.meta_dir = os.path.join(self.base_dir, "meta")

        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.label_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)

    def _now_ok_to_save(self):
        return time.time() - self.last_save_time >= self.config.auto_mine_cooldown_sec

    def _mark_saved(self):
        self.last_save_time = time.time()

    def _distance(self, obj1, obj2):
        x1, y1 = obj1["center"]
        x2, y2 = obj2["center"]
        return hypot(x1 - x2, y1 - y2)

    def _find_low_conf_targets(self, objects):
        reasons = []

        for obj in objects:
            name = obj["cls_name"]
            conf = obj["conf"]

            if name == "player" and conf < self.config.hard_low_conf_player:
                reasons.append(f"low_conf_player:{conf:.2f}")
            elif name == "monster" and conf < self.config.hard_low_conf_monster:
                reasons.append(f"low_conf_monster:{conf:.2f}")
            elif name == "obstacle" and conf < self.config.hard_low_conf_obstacle:
                reasons.append(f"low_conf_obstacle:{conf:.2f}")

        return reasons

    def _find_close_pair_reasons(self, parsed):
        reasons = []

        player = parsed["player"]
        monsters = parsed["monsters"]
        obstacles = parsed["obstacles"]

        if player is not None:
            for monster in monsters:
                d = self._distance(player, monster)
                if d <= self.config.close_center_dist_player_monster:
                    reasons.append(f"close_player_monster:{d:.1f}")
                    break

            for obstacle in obstacles:
                d = self._distance(player, obstacle)
                if d <= self.config.close_center_dist_player_obstacle:
                    reasons.append(f"close_player_obstacle:{d:.1f}")
                    break

        for monster in monsters:
            for obstacle in obstacles:
                d = self._distance(monster, obstacle)
                if d <= self.config.close_center_dist_monster_obstacle:
                    reasons.append(f"close_monster_obstacle:{d:.1f}")
                    return reasons

        return reasons

    def _update_player_missing(self, parsed):
        if parsed["player"] is None:
            self.player_missing_count += 1
        else:
            self.player_missing_count = 0

    def _find_player_missing_reason(self):
        if self.player_missing_count >= self.config.player_missing_frames_threshold:
            return [f"player_missing_frames:{self.player_missing_count}"]
        return []

    def _frame_size(self, frame):
        h, w = frame.shape[:2]
        return w, h

    def _clamp(self, x, low, high):
        return max(low, min(x, high))

    def _to_yolo_line(self, obj, img_w, img_h):
        class_name = obj["cls_name"]
        if class_name not in self.class_name_to_id:
            return None

        if obj["conf"] < self.config.pseudo_label_min_conf:
            return None

        x1, y1, x2, y2 = obj["bbox"]

        x1 = self._clamp(x1, 0, img_w - 1)
        y1 = self._clamp(y1, 0, img_h - 1)
        x2 = self._clamp(x2, 0, img_w - 1)
        y2 = self._clamp(y2, 0, img_h - 1)

        bw = max(1, x2 - x1)
        bh = max(1, y2 - y1)
        cx = x1 + bw / 2.0
        cy = y1 + bh / 2.0

        cx_n = cx / img_w
        cy_n = cy / img_h
        bw_n = bw / img_w
        bh_n = bh / img_h

        class_id = self.class_name_to_id[class_name]
        return f"{class_id} {cx_n:.6f} {cy_n:.6f} {bw_n:.6f} {bh_n:.6f}"

    def _save_case(self, frame, objects, reasons, action):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        image_path = os.path.join(self.image_dir, f"{timestamp}.png")
        label_path = os.path.join(self.label_dir, f"{timestamp}.txt")
        meta_path = os.path.join(self.meta_dir, f"{timestamp}.json")

        cv2.imwrite(image_path, frame)

        img_w, img_h = self._frame_size(frame)
        lines = []
        for obj in objects:
            line = self._to_yolo_line(obj, img_w, img_h)
            if line is not None:
                lines.append(line)

        with open(label_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        meta = {
            "image": image_path,
            "label": label_path,
            "reasons": reasons,
            "action": action,
            "objects": objects,
            "image_size": {
                "width": img_w,
                "height": img_h
            }
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        self._mark_saved()
        print(f"[AUTO_MINE] saved hard case: {timestamp} | reasons={reasons}")

    def maybe_save(self, frame, objects, parsed, action):
        if not self.config.auto_mine_enabled:
            return

        self._update_player_missing(parsed)

        reasons = []
        reasons.extend(self._find_low_conf_targets(objects))
        reasons.extend(self._find_close_pair_reasons(parsed))
        reasons.extend(self._find_player_missing_reason())

        if not reasons:
            return

        if not self._now_ok_to_save():
            return

        self._save_case(frame, objects, reasons, action)
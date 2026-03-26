import time
import cv2


class Runner:
    def __init__(self, capture, detector, parser, planner, controller, miner, config):
        self.capture = capture
        self.detector = detector
        self.parser = parser
        self.planner = planner
        self.controller = controller
        self.miner = miner
        self.config = config

        self.last_action_time = {
            "move_left": 0.0,
            "move_right": 0.0,
            "attack": 0.0,
            "pickup": 0.0,
            "confirm": 0.0,
            "idle": 0.0,
        }

    def _get_cooldown(self, action_name):
        if action_name in ("move_left", "move_right"):
            return self.config.cooldown_move
        if action_name == "attack":
            return self.config.cooldown_attack
        if action_name == "pickup":
            return self.config.cooldown_pickup
        if action_name == "confirm":
            return self.config.cooldown_confirm
        return 0.0

    def _can_execute(self, action_name):
        now = time.time()
        cd = self._get_cooldown(action_name)
        return now - self.last_action_time.get(action_name, 0.0) >= cd

    def _mark_executed(self, action_name):
        self.last_action_time[action_name] = time.time()

    def execute_action(self, action):
        name = action["name"]
        hold = action.get("hold", 0.03)

        if name == "idle":
            return

        if not self._can_execute(name):
            return

        if name == "move_left":
            self.controller.tap("left", hold)
        elif name == "move_right":
            self.controller.tap("right", hold)
        elif name == "attack":
            self.controller.tap("attack", hold)
        elif name == "pickup":
            self.controller.tap("pickup", hold)
        elif name == "confirm":
            self.controller.tap("confirm", hold)

        self._mark_executed(name)

    def draw_debug(self, frame, objects, parsed, action):
        for obj in objects:
            x1, y1, x2, y2 = obj["bbox"]
            cx, cy = obj["center"]
            text = f'{obj["cls_name"]} {obj["conf"]:.2f}'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(
                frame,
                text,
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

        target_name = "none"
        if action.get("target") is not None:
            target_name = action["target"]["cls_name"]

        lines = [
            f'player: {"yes" if parsed["player"] else "no"}',
            f'monsters: {len(parsed["monsters"])}',
            f'items: {len(parsed["items"])}',
            f'doors: {len(parsed["doors"])}',
            f'obstacles: {len(parsed["obstacles"])}',
            f'questionmarks: {len(parsed["questionmarks"])}',
            f'replays: {len(parsed["replays"])}',
            f'action: {action["name"]}',
            f'reason: {action.get("reason", "none")}',
            f'target: {target_name}',
            f'diff: {action.get("diff", None)}',
            'Q: quit'
        ]

        y = 25
        for line in lines:
            cv2.putText(
                frame,
                line,
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 0, 0),
                2
            )
            y += 28

        cv2.imshow("debug", frame)

    def run(self):
        cv2.namedWindow("debug", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("debug", 960, 540)
        cv2.moveWindow("debug", 1300, 50)

        while True:
            frame = self.capture.grab()
            objects = self.detector.predict(frame)
            parsed = self.parser.parse(objects)
            action = self.planner.plan(parsed)

            self.execute_action(action)
            self.miner.maybe_save(frame, objects, parsed, action)

            if self.config.debug:
                self.draw_debug(frame, objects, parsed, action)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            time.sleep(self.config.loop_sleep)

        cv2.destroyAllWindows()
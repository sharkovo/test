import time
import kmNet


HID = {
    "a": 0x04,
    "d": 0x07,
    "w": 0x1A,
    "s": 0x16,
    "j": 0x0D,
    "k": 0x0E,
    "x": 0x1B,
    "1": 0x1E,
    "2": 0x1F,
    "3": 0x20,
    "space": 0x2C,
    ";": 0x33,
}


class KMBoxController:
    def __init__(self, ip, port, uuid, keymap=None, hold_time=0.03):
        self.ip = ip
        self.port = port
        self.uuid = uuid
        self.hold_time = hold_time

        self.keymap = keymap or {
            "left": "k",
            "right": ";",
            "up": "o",
            "down": "l",
            "attack": "x",
            "jump": "c",
            "pickup": "x",
            "skill1": "1",
            "skill2": "2",
            "skill3": "3",
            "confirm": "space",
        }

        self._connect()

    def _connect(self):
        print(f"connecting kmbox: ip={self.ip}, port={self.port}, uuid={self.uuid}")
        kmNet.init(self.ip, self.port, self.uuid)
        print("kmbox connected")

    def _to_code(self, key_name):
        real_key = self.keymap.get(key_name, key_name).lower()
        if real_key not in HID:
            raise ValueError(f"未配置键码: {real_key}")
        return HID[real_key]

    def tap(self, key_name, hold_time=None):
        hold_time = self.hold_time if hold_time is None else hold_time
        code = self._to_code(key_name)
        kmNet.keydown(code)
        time.sleep(hold_time)
        kmNet.keyup(code)
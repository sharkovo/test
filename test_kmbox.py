import time
from config import AppConfig
from control.kmbox_controller import KMBoxController


def main():
    config = AppConfig()

    controller = KMBoxController(
        ip=config.kmbox_ip,
        port=config.kmbox_port,
        uuid=config.kmbox_uuid,
        keymap={
            "left": "a",
            "right": "d",
            "up": "w",
            "down": "s",
            "attack": "j",
            "jump": "k",
            "pickup": "x",
            "skill1": "1",
            "skill2": "2",
            "skill3": "3",
            "confirm": "space",
        }
    )

    print("3秒后开始测试，请切到目标窗口")
    time.sleep(3)

    print("test left")
    controller.tap("left")
    time.sleep(0.5)

    print("test right")
    controller.tap("right")
    time.sleep(0.5)

    print("test attack")
    controller.tap("attack")
    time.sleep(0.5)

    print("test confirm")
    controller.tap("confirm")
    time.sleep(0.5)

    print("done")


if __name__ == "__main__":
    main()
from config import AppConfig
from capture.screen_capture import ScreenCapture
from detect.yolo_detector import YoloDetector
from core.object_parser import ObjectParser
from core.planner import Planner
from core.runner import Runner
from core.hard_case_miner import HardCaseMiner
from control.kmbox_controller import KMBoxController


def main():
    config = AppConfig()

    capture = ScreenCapture(config.capture_region)

    detector = YoloDetector(
        model_path=config.model_path,
        conf=config.conf,
        iou=config.iou,
        class_id_to_name=config.class_id_to_name
    )

    parser = ObjectParser()
    planner = Planner(config, parser)
    miner = HardCaseMiner(config)

    controller = KMBoxController(
        ip=config.kmbox_ip,
        port=config.kmbox_port,
        uuid=config.kmbox_uuid,
        keymap={
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
    )

    runner = Runner(
        capture=capture,
        detector=detector,
        parser=parser,
        planner=planner,
        controller=controller,
        miner=miner,
        config=config
    )
    runner.run()


if __name__ == "__main__":
    main()
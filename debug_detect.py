import cv2
import numpy as np
import mss
from detect.yolo_detector import YoloDetector
from core.object_parser import ObjectParser


MODEL_PATH = "D:/test/runs/detect/train/weights/best.pt"


def main():
    detector = YoloDetector(MODEL_PATH, conf=0.5, iou=0.5)
    parser = ObjectParser()

    with mss.mss() as sct:
        monitor = {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720
        }

        while True:
            shot = sct.grab(monitor)
            frame = np.array(shot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            objects = detector.predict(frame)
            parsed = parser.parse(objects)

            for obj in objects:
                x1, y1, x2, y2 = obj["bbox"]
                cx, cy = obj["center"]
                label = f'{obj["cls_name"]} {obj["conf"]:.2f}'

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame, label, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            lines = [
                f'player: {"yes" if parsed["player"] else "no"}',
                f'monsters: {len(parsed["monsters"])}',
                f'items: {len(parsed["items"])}',
                f'doors: {len(parsed["doors"])}',
                f'obstacles: {len(parsed["obstacles"])}',
                f'questionmarks: {len(parsed["questionmarks"])}',
                f'replays: {len(parsed["replays"])}',
            ]

            y = 25
            for line in lines:
                cv2.putText(frame, line, (20, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)
                y += 28

            cv2.imshow("detect_debug", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
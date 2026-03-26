from ultralytics import YOLO


class YoloDetector:
    def __init__(self, model_path, conf=0.5, iou=0.5, class_id_to_name=None):
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.class_id_to_name = class_id_to_name or {}

        print("loaded model:", model_path)
        print("raw model.names:", self.model.names)
        print("override class_id_to_name:", self.class_id_to_name)

    def _get_class_name(self, cls_id):
        if cls_id in self.class_id_to_name:
            return self.class_id_to_name[cls_id]
        return self.model.names[cls_id]

    def predict(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            verbose=False
        )

        objects = []
        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                score = float(box.conf[0].item())
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                cls_name = self._get_class_name(cls_id)

                objects.append({
                    "cls_id": cls_id,
                    "cls_name": cls_name,
                    "conf": score,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                })

        return objects
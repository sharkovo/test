import mss
import numpy as np
import cv2


class ScreenCapture:
    def __init__(self, capture_region):
        self.sct = mss.mss()
        self.region = capture_region

    def grab(self):
        img = self.sct.grab(self.region)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame
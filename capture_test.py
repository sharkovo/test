import cv2
import numpy as np
import mss

with mss.mss() as sct:
    monitor = sct.monitors[1]  # 主屏幕
    screenshot = sct.grab(monitor)

    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    cv2.imwrite("D:/test/screen_test.png", img)
    print("截图已保存为 screen_test.png")
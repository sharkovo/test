import time
import cv2
import numpy as np
import mss
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = True  # 鼠标移到左上角可强制中止

WINDOW_TITLE = "Vision Test Window"

def get_window_region(title):
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        return None, None

    win = windows[0]

    # 有些情况下窗口最小化了
    if win.isMinimized:
        win.restore()
        time.sleep(0.5)

    try:
        win.activate()
    except:
        pass

    time.sleep(0.3)

    left = win.left
    top = win.top
    width = win.width
    height = win.height

    region = {
        "left": left,
        "top": top,
        "width": width,
        "height": height
    }
    return win, region

def find_color_box(frame, color_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color_name == "red":
        lower1 = np.array([0, 120, 70])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 70])
        upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = mask1 | mask2

    elif color_name == "blue":
        lower = np.array([100, 120, 70])
        upper = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

    else:
        return None

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < 300:
        return None

    x, y, w, h = cv2.boundingRect(largest)
    cx = x + w // 2
    cy = y + h // 2
    return (x, y, w, h, cx, cy)

def draw_box(frame, result, color, label):
    if result is None:
        return
    x, y, w, h, cx, cy = result
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    cv2.circle(frame, (cx, cy), 4, color, -1)
    cv2.putText(frame, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def main():
    print("正在查找测试窗口...")
    win, region = get_window_region(WINDOW_TITLE)

    if region is None:
        print(f"没找到窗口：{WINDOW_TITLE}")
        print("请先运行 test_window.py")
        return

    print("找到窗口，3 秒后开始控制。")
    print("停止方法：")
    print("1) 把鼠标移到屏幕左上角")
    print("2) 或者按调试窗口里的 q")
    time.sleep(3)

    last_key_time = 0
    last_activate_time = 0

    with mss.mss() as sct:
        while True:
            now = time.time()

            # 每隔一段时间重新激活测试窗口
            if now - last_activate_time > 2:
                try:
                    win.activate()
                except:
                    pass
                last_activate_time = now

            screenshot = sct.grab(region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            red_box = find_color_box(frame, "red")
            blue_box = find_color_box(frame, "blue")

            draw_box(frame, red_box, (0, 0, 255), "target")
            draw_box(frame, blue_box, (255, 0, 0), "player")

            action_text = "searching..."

            if red_box is not None and blue_box is not None:
                _, _, _, _, red_cx, _ = red_box
                _, _, _, _, blue_cx, _ = blue_box

                diff = red_cx - blue_cx

                cv2.line(frame, (red_cx, 0), (red_cx, frame.shape[0]), (0, 0, 255), 1)
                cv2.line(frame, (blue_cx, 0), (blue_cx, frame.shape[0]), (255, 0, 0), 1)

                # 控制节奏，避免按太快
                if diff > 20:
                    pyautogui.keyDown("d")
                    time.sleep(0.03)
                    pyautogui.keyUp("d")
                    action_text = "press D"
                    last_key_time = now

                elif diff < -20:
                    pyautogui.keyDown("a")
                    time.sleep(0.03)
                    pyautogui.keyUp("a")
                    action_text = "press A"
                    last_key_time = now

                else:
                    pyautogui.keyDown("space")
                    time.sleep(0.03)
                    pyautogui.keyUp("space")
                    action_text = "press SPACE"
                    last_key_time = now

                cv2.putText(frame, f"diff={diff}", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)

            cv2.putText(frame, action_text, (20, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 120, 0), 2)

            cv2.imshow("Bot Debug", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
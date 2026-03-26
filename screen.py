import os
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import mss
from PIL import Image
import keyboard


class AutoScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Screenshot")
        self.root.geometry("560x470")
        self.root.resizable(False, False)

        self.running = False
        self.worker_thread = None
        self.hotkey_started = False

        self.save_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "screenshots"))
        self.left_var = tk.StringVar(value="0")
        self.top_var = tk.StringVar(value="0")
        self.width_var = tk.StringVar(value="1280")
        self.height_var = tk.StringVar(value="720")
        self.interval_var = tk.StringVar(value="1.0")
        self.prefix_var = tk.StringVar(value="shot")

        self.toggle_hotkey_var = tk.StringVar(value="f8")
        self.quit_hotkey_var = tk.StringVar(value="f9")

        self.status_var = tk.StringVar(value="状态：未开始")
        self.count_var = tk.StringVar(value="已截图：0")
        self.last_file_var = tk.StringVar(value="最近文件：无")

        self.capture_count = 0
        self.hotkey_toggle_id = None
        self.hotkey_quit_id = None

        self.build_ui()
        self.register_hotkeys()

    def build_ui(self):
        pad_x = 12
        pad_y = 8

        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="保存目录").grid(row=0, column=0, sticky="w", pady=pad_y)
        ttk.Entry(frame, textvariable=self.save_dir_var, width=42).grid(row=0, column=1, sticky="we", pady=pad_y)
        ttk.Button(frame, text="选择", command=self.choose_folder).grid(row=0, column=2, padx=6, pady=pad_y)

        ttk.Label(frame, text="文件前缀").grid(row=1, column=0, sticky="w", pady=pad_y)
        ttk.Entry(frame, textvariable=self.prefix_var, width=20).grid(row=1, column=1, sticky="w", pady=pad_y)

        region_box = ttk.LabelFrame(frame, text="截图区域", padding=10)
        region_box.grid(row=2, column=0, columnspan=3, sticky="we", pady=pad_y)

        ttk.Label(region_box, text="Left").grid(row=0, column=0, padx=pad_x, pady=pad_y, sticky="w")
        ttk.Entry(region_box, textvariable=self.left_var, width=10).grid(row=0, column=1, pady=pad_y)

        ttk.Label(region_box, text="Top").grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky="w")
        ttk.Entry(region_box, textvariable=self.top_var, width=10).grid(row=0, column=3, pady=pad_y)

        ttk.Label(region_box, text="Width").grid(row=1, column=0, padx=pad_x, pady=pad_y, sticky="w")
        ttk.Entry(region_box, textvariable=self.width_var, width=10).grid(row=1, column=1, pady=pad_y)

        ttk.Label(region_box, text="Height").grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky="w")
        ttk.Entry(region_box, textvariable=self.height_var, width=10).grid(row=1, column=3, pady=pad_y)

        ttk.Label(frame, text="截图间隔（秒）").grid(row=3, column=0, sticky="w", pady=pad_y)
        ttk.Entry(frame, textvariable=self.interval_var, width=12).grid(row=3, column=1, sticky="w", pady=pad_y)

        hotkey_box = ttk.LabelFrame(frame, text="热键设置", padding=10)
        hotkey_box.grid(row=4, column=0, columnspan=3, sticky="we", pady=pad_y)

        ttk.Label(hotkey_box, text="开始/停止热键").grid(row=0, column=0, sticky="w", padx=pad_x, pady=pad_y)
        ttk.Entry(hotkey_box, textvariable=self.toggle_hotkey_var, width=12).grid(row=0, column=1, sticky="w", pady=pad_y)

        ttk.Label(hotkey_box, text="退出程序热键").grid(row=0, column=2, sticky="w", padx=pad_x, pady=pad_y)
        ttk.Entry(hotkey_box, textvariable=self.quit_hotkey_var, width=12).grid(row=0, column=3, sticky="w", pady=pad_y)

        ttk.Button(hotkey_box, text="重新注册热键", command=self.reregister_hotkeys).grid(row=1, column=0, columnspan=2, sticky="w", padx=pad_x, pady=pad_y)

        btn_box = ttk.Frame(frame)
        btn_box.grid(row=5, column=0, columnspan=3, pady=16)

        self.start_btn = ttk.Button(btn_box, text="开始截图", command=self.start_capture)
        self.start_btn.pack(side="left", padx=8)

        self.stop_btn = ttk.Button(btn_box, text="停止截图", command=self.stop_capture, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        ttk.Button(btn_box, text="打开保存目录", command=self.open_save_dir).pack(side="left", padx=8)

        status_box = ttk.LabelFrame(frame, text="运行信息", padding=10)
        status_box.grid(row=6, column=0, columnspan=3, sticky="we", pady=pad_y)

        ttk.Label(status_box, textvariable=self.status_var).pack(anchor="w", pady=4)
        ttk.Label(status_box, textvariable=self.count_var).pack(anchor="w", pady=4)
        ttk.Label(status_box, textvariable=self.last_file_var, wraplength=500).pack(anchor="w", pady=4)

        tip_text = (
            "说明：\n"
            "1. 默认区域是屏幕左上角 1280x720\n"
            "2. 按热键可开始/停止截图\n"
            "3. 默认 F8 开始/停止，F9 退出程序\n"
            "4. 如果热键无效，尝试用管理员权限运行"
        )
        ttk.Label(frame, text=tip_text, foreground="#444").grid(row=7, column=0, columnspan=3, sticky="w", pady=10)

        frame.columnconfigure(1, weight=1)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_dir_var.set(folder)

    def open_save_dir(self):
        path = self.save_dir_var.get().strip()
        if not path:
            messagebox.showerror("错误", "保存目录不能为空")
            return

        os.makedirs(path, exist_ok=True)
        os.startfile(path)

    def validate_inputs(self):
        try:
            left = int(self.left_var.get().strip())
            top = int(self.top_var.get().strip())
            width = int(self.width_var.get().strip())
            height = int(self.height_var.get().strip())
            interval = float(self.interval_var.get().strip())
        except ValueError:
            messagebox.showerror("输入错误", "left/top/width/height 必须是整数，间隔必须是数字")
            return None

        if width <= 0 or height <= 0:
            messagebox.showerror("输入错误", "width 和 height 必须大于 0")
            return None

        if interval <= 0:
            messagebox.showerror("输入错误", "截图间隔必须大于 0")
            return None

        save_dir = self.save_dir_var.get().strip()
        if not save_dir:
            messagebox.showerror("输入错误", "保存目录不能为空")
            return None

        prefix = self.prefix_var.get().strip() or "shot"

        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "interval": interval,
            "save_dir": save_dir,
            "prefix": prefix,
        }

    def start_capture(self):
        if self.running:
            return

        config = self.validate_inputs()
        if config is None:
            return

        os.makedirs(config["save_dir"], exist_ok=True)

        self.running = True
        self.status_var.set("状态：运行中")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.worker_thread = threading.Thread(target=self.capture_loop, args=(config,), daemon=True)
        self.worker_thread.start()

    def stop_capture(self):
        if not self.running:
            return

        self.running = False
        self.status_var.set("状态：正在停止...")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def toggle_capture(self):
        self.root.after(0, self._toggle_capture_on_ui_thread)

    def _toggle_capture_on_ui_thread(self):
        if self.running:
            self.stop_capture()
        else:
            self.start_capture()

    def capture_loop(self, config):
        region = {
            "left": config["left"],
            "top": config["top"],
            "width": config["width"],
            "height": config["height"],
        }

        try:
            with mss.mss() as sct:
                while self.running:
                    shot = sct.grab(region)
                    img = Image.frombytes("RGB", shot.size, shot.rgb)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = f'{config["prefix"]}_{timestamp}.png'
                    filepath = os.path.join(config["save_dir"], filename)

                    img.save(filepath)

                    self.capture_count += 1
                    self.root.after(0, self.update_runtime_info, filepath)

                    sleep_seconds = config["interval"]
                    step = 0.05
                    elapsed = 0.0
                    while self.running and elapsed < sleep_seconds:
                        time.sleep(min(step, sleep_seconds - elapsed))
                        elapsed += step

        except Exception as e:
            self.root.after(0, self.handle_error, str(e))
            return

        self.root.after(0, self.finish_stop)

    def update_runtime_info(self, filepath):
        self.status_var.set("状态：运行中")
        self.count_var.set(f"已截图：{self.capture_count}")
        self.last_file_var.set(f"最近文件：{filepath}")

    def handle_error(self, error_text):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("状态：出错")
        messagebox.showerror("运行错误", error_text)

    def finish_stop(self):
        self.status_var.set("状态：已停止")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def register_hotkeys(self):
        try:
            toggle_hotkey = self.toggle_hotkey_var.get().strip().lower()
            quit_hotkey = self.quit_hotkey_var.get().strip().lower()

            if not toggle_hotkey or not quit_hotkey:
                raise ValueError("热键不能为空")

            self.hotkey_toggle_id = keyboard.add_hotkey(toggle_hotkey, self.toggle_capture)
            self.hotkey_quit_id = keyboard.add_hotkey(quit_hotkey, self.safe_quit)

            self.status_var.set(f"状态：热键已注册（{toggle_hotkey} 开始/停止，{quit_hotkey} 退出）")
            self.hotkey_started = True

        except Exception as e:
            self.hotkey_started = False
            messagebox.showerror("热键注册失败", f"{e}\n\n可尝试管理员权限运行。")

    def unregister_hotkeys(self):
        try:
            if self.hotkey_toggle_id is not None:
                keyboard.remove_hotkey(self.hotkey_toggle_id)
                self.hotkey_toggle_id = None

            if self.hotkey_quit_id is not None:
                keyboard.remove_hotkey(self.hotkey_quit_id)
                self.hotkey_quit_id = None
        except Exception:
            pass

    def reregister_hotkeys(self):
        self.unregister_hotkeys()
        self.register_hotkeys()

    def safe_quit(self):
        self.root.after(0, self.on_close)

    def on_close(self):
        self.running = False
        self.unregister_hotkeys()
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AutoScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
# from dataclasses import dataclass, field


# @dataclass
# class AppConfig:

#     model_path: str = "D:/test/runs/detect/train/weights/best.pt"
#     conf: float = 0.3
#     iou: float = 0.5
#     loop_sleep: float = 0.03
#     debug: bool = True

#     capture_region: dict = field(default_factory=lambda: {
#         "left": 0,
#         "top": 0,
#         "width": 1280,
#         "height": 720
#     })
#     kmbox_ip: str="192.168.2.188"
#     kmbox_port: str = "9312"
#     kmbox_uuid: str = "EE770C3D"
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    model_path: str = "D:/test/runs/detect/train/weights/best.pt"
    conf: float = 0.3
    iou: float = 0.5
    loop_sleep: float = 0.03
    debug: bool = True

    capture_region: dict = field(default_factory=lambda: {
        "left": 0,
        "top": 0,
        "width": 1280,
        "height": 720
    })

    kmbox_ip: str = "192.168.2.188"
    kmbox_port: str = "9312"
    kmbox_uuid: str = "EE770C3D"

    # 你当前程序使用的“规范类别名”
    # 后面自动导出 YOLO 伪标签时，就按这个顺序写 class id
    class_id_to_name: dict = field(default_factory=lambda: {
        0: "door",
        1: "item",
        2: "monster",
        3: "obstacle",
        4: "player",
        5: "questionmark",
        6: "replay",
    })

    # 决策阈值
    attack_x_threshold: int = 90
    pickup_x_threshold: int = 70
    interact_x_threshold: int = 80

    # 按键时长
    move_hold_time: float = 0.05
    attack_hold_time: float = 0.04
    pickup_hold_time: float = 0.04
    confirm_hold_time: float = 0.04

    # 动作冷却
    cooldown_move: float = 0.06
    cooldown_attack: float = 0.20
    cooldown_pickup: float = 0.25
    cooldown_confirm: float = 0.25

    idle_patrol_direction: str = "right"

    # ========== 难例采集 ==========
    auto_mine_enabled: bool = True
    auto_mine_dir: str = "datasets/auto_mined"

    # 两次保存的最小间隔，避免同一场景连拍几百张
    auto_mine_cooldown_sec: float = 1.2

    # 连续丢失 player 达到多少帧，算难例
    player_missing_frames_threshold: int = 8

    # 关键类别低置信阈值
    hard_low_conf_player: float = 0.60
    hard_low_conf_monster: float = 0.55
    hard_low_conf_obstacle: float = 0.55

    # 目标中心过近，视为“重合/贴边困难样本”
    close_center_dist_player_monster: int = 110
    close_center_dist_player_obstacle: int = 100
    close_center_dist_monster_obstacle: int = 100

    # 导出伪标签时，最低保留置信度
    pseudo_label_min_conf: float = 0.45
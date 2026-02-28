import os

# 基础路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# 音频处理策略
MAX_SPEED_UP_RATIO = 1.5  # 最大允许的加速倍率 (超过则裁剪结尾)
BACKGROUND_VOLUME_RATIO = 0.2  # 原视频作为背景音的音量比例 (20%)

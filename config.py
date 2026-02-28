import os

# 基础路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# 音频处理策略
MAX_SPEED_UP_RATIO = 1.5  # 最大允许的加速倍率 (超过则裁剪结尾)
BACKGROUND_VOLUME_RATIO = 0.2  # 原视频作为背景音的音量比例 (20%)

# 跨平台原生离线音色映射表
# 键名: 抽象音色特征 (可在外部 CLI 直接指定)
# 对应值: Mac下的 say 命令发音人 (mac), Windows下的 sapi5 引擎发音人 (win), Http 离线大模型发音人特征 (http)
VOICE_PROFILES = {
    "female": {"mac": "Ting-Ting", "win": "Huihui", "http": "nova"},
    "male": {"mac": "Kankan", "win": "Kangkang", "http": "echo"},
    "broadcaster": {"mac": "Ting-Ting", "win": "Huihui", "http": "alloy"}, # 系统自带局限，默认回落机制
}


import os

# 基础路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# 音频处理策略
MAX_SPEED_UP_RATIO = 1.5  # 最大允许的加速倍率 (超过则裁剪结尾)
BACKGROUND_VOLUME_RATIO = 0.2  # 原视频作为背景音的音量比例 (20%)

# TTS 引擎模式选择: "native" (系统自带) 或 "cosyvoice" (本地部署的 AI 服务)
TTS_MODE = "native" 
COSYVOICE_URL = "http://localhost:9233/v1/audio/speech" # 默认 CosyVoice OpenAI 兼容接口地址

# 可选维度定义
GENDERS = ["male", "female"]
STYLES = ["standard", "broadcaster"]

# 跨平台/AI 二维映射表 [性别][维度风格]
# 映射逻辑：[gender][style] -> {mac, win, http_voice_id}
VOICE_MAP = {
    "female": {
        "standard": {"mac": "Tingting", "win": "Huihui", "http": "中文女"},
        "broadcaster": {"mac": "Tingting", "win": "Huihui", "http": "晓晓"},
    },
    "male": {
        "standard": {"mac": "Eddy", "win": "Kangkang", "http": "中文男"},
        "broadcaster": {"mac": "Eddy", "win": "Kangkang", "http": "云扬"},
    }

}






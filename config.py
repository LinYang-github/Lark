import os

# 基础路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# 音频处理策略
MAX_SPEED_UP_RATIO = 1.5  # 最大允许的加速倍率 (超过则裁剪结尾)
BACKGROUND_VOLUME_RATIO = 0.2  # 原视频作为背景音的音量比例 (20%)

# TTS 引擎模式选择: "native" 或 "cosyvoice"
TTS_MODE = "native" 
COSYVOICE_URL = "http://localhost:9233/v1/audio/speech"

# 引擎能力矩阵与参数映射
TTS_ENGINE_CAPABILITIES = {
    "native": {
        "name": "Native (系统轻量级)",
        "params": ["gender", "rate"],
        "genders": ["male", "female"],
        "voices": {
            "female": {"mac": "Tingting", "win": "Huihui"},
            "male": {"mac": "Eddy", "win": "Kangkang"}
        },
        "default_rate": 180  # 系统默认语速 (单词/分钟)
    },
    "cosyvoice": {
        "name": "CosyVoice (AI 专业级)",
        "params": ["language", "gender", "style"],
        "languages": ["中文", "English", "日本語", "粤语", "한국어"],
        "genders": ["male", "female"],
        "styles": ["standard", "broadcaster"],
        "voices": {
            "中文": {
                "female": {"standard": "中文女", "broadcaster": "晓晓"},
                "male": {"standard": "中文男", "broadcaster": "云扬"}
            },
            "English": {
                "female": {"standard": "英文女", "broadcaster": "AzureEN"},
                "male": {"standard": "英文男", "broadcaster": "AzureEN"}
            },
            "日本語": {
                "female": {"standard": "日文女", "broadcaster": "AzureJA"},
                "male": {"standard": "日文男", "broadcaster": "AzureJA"}
            },
            "粤语": {
                "female": {"standard": "粤语女", "broadcaster": "晓晓"}, # 晓晓在离线包中通常支持多语言
                "male": {"standard": "粤语女", "broadcaster": "晓晓"}
            },
            "한국어": {
                "female": {"standard": "韩文女", "broadcaster": "晓晓"},
                "male": {"standard": "韩文女", "broadcaster": "晓晓"}
            }
        }
    }
}







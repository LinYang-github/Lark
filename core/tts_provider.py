import os
import sys
import json
import urllib.request
from abc import ABC, abstractmethod
import config

# 尝试导入 pyttsx3，如果失败不报错，而是留给具体实现的构造函数去处理
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

class TTSProvider(ABC):
    """TTS 语音生成接口基类，提供可插拔设计"""
    
    @abstractmethod
    def generate_audio(self, text: str, output_path: str) -> bool:
        """
        根据文本生成语音并保存为指定的输出路径 (通常为 .wav)
        :param text: 要转换的文本
        :param output_path: 最终生成的音频输出路径
        :return: 成功返回 True, 失败返回 False
        """
        pass

class Pyttsx3TTS(TTSProvider):
    """基于系统自带接口的本地 TTS 引擎实现 (Mac: say, Windows: sapi5)"""
    def __init__(self, gender="female", rate=180):
        self.is_mac = sys.platform == "darwin"
        self.gender = gender
        self.rate = rate
        self.engine = None
        
        cap = config.TTS_ENGINE_CAPABILITIES["native"]
        self.voice_name = cap["voices"][gender]["win" if not self.is_mac else "mac"]

        if not self.is_mac:
            if pyttsx3 is None:
                raise ImportError("Windows 下运行 Native 模式需安装 pyttsx3")
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', rate)
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if self.voice_name.lower() in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        break
            except Exception as e:
                print(f"初始化 pyttsx3 失败: {e}")

    def generate_audio(self, text: str, output_path: str) -> bool:
        if self.is_mac:
            # Mac 专用 fallback: 使用自带的 say 命令生成 aiff，再用 ffmpeg 转 wav
            try:
                import subprocess
                aiff_path = output_path.replace(".wav", ".aiff")
                # say 命令参数: -v 音色, -r 语速 (wpm), -o 输出文件
                subprocess.run(["say", "-v", self.voice_name, "-r", str(self.rate), "-o", aiff_path, text], check=True)
                # 转换为 wav 格式
                subprocess.run(["ffmpeg", "-y", "-i", aiff_path, output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(aiff_path):
                    os.remove(aiff_path)
                return True
            except Exception as e:
                print(f"Mac say 命令生成失败: {e}")
                return False
        else:
            if not self.engine:
                return False
            try:
                self.engine.save_to_file(text, output_path)
                self.engine.runAndWait()
                return True
            except Exception as e:
                print(f"Pyttsx3 生成失败: {e}")
                return False

class HttpTTS(TTSProvider):
    """用于对接本地 CosyVoice 或其他 AI 模型 API 服务"""
    def __init__(self, params):
        self.api_url = config.COSYVOICE_URL
        mode = params["mode"]
        lang = params["language"]
        gender = params["gender"]
        style = params["style"]
        
        cap = config.TTS_ENGINE_CAPABILITIES[mode]
        try:
            self.http_voice = cap["voices"][lang][gender][style]
        except KeyError:
            print(f"Warning: Voice not found for {lang}/{gender}/{style}. Fallback.")
            self.http_voice = "中文女"

    def generate_audio(self, text: str, output_path: str) -> bool:
        try:
            payload = {
                "model": "cosyvoice",
                "input": text,
                "voice": self.http_voice, 
                "response_format": "wav"
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.api_url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=300) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.read())
                    return True
                else:
                    return False
        except Exception as e:
            print(f"连接 CosyVoice 服务失败: {e}")
            return False

def get_tts_provider(params: dict) -> TTSProvider:
    mode = params["mode"]
    if mode == "native":
        # 获取可选的 rate，如果不存在则使用默认值
        rate = params.get("rate", config.TTS_ENGINE_CAPABILITIES["native"]["default_rate"])
        return Pyttsx3TTS(params["gender"], rate)
    elif mode == "cosyvoice":
        return HttpTTS(params)
    else:
        raise ValueError(f"不支持的 TTS 模式: {mode}")

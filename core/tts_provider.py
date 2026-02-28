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
    """基于系统自带接口的本地 TTS 引擎实现 (Mac fallback: say, Windows: sapi5)"""
    def __init__(self, rate: int = 150, voice_type: str = "female"):
        self.rate = rate
        self.is_mac = sys.platform == "darwin"
        self.engine = None
        self.mac_voice = config.VOICE_PROFILES.get(voice_type, config.VOICE_PROFILES["female"])["mac"]
        target_win_voice = config.VOICE_PROFILES.get(voice_type, config.VOICE_PROFILES["female"])["win"]
        
        if not self.is_mac and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', rate)
                
                # 尝试选择一个合适的系统声音
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    voice_id = getattr(voice, 'id', '')
                    voice_name = getattr(voice, 'name', '')
                    lang_str = str(getattr(voice, 'languages', []))
                    
                    # 优先匹配指定音色名，如果没有则 fallback 到普通中文
                    if target_win_voice.lower() in voice_name.lower() or target_win_voice.lower() in voice_id.lower():
                        self.engine.setProperty('voice', voice_id)
                        break
                    elif 'zh' in lang_str or 'Chinese' in voice_name or 'CN' in voice_id:
                        self.engine.setProperty('voice', voice_id)
                        # 不 break，继续找更精准的 target_win_voice
            except Exception as e:
                print(f"初始化 pyttsx3 失败: {e}")
                
    def generate_audio(self, text: str, output_path: str) -> bool:
        if self.is_mac:
            # Mac 专用 fallback: 使用自带的 say 命令生成 aiff，再用 ffmpeg 转 wav
            try:
                import subprocess
                aiff_path = output_path.replace(".wav", ".aiff")
                # 使用映射的发音人
                subprocess.run(["say", "-v", self.mac_voice, "-o", aiff_path, text], check=True)
                # 转换为 wav 格式
                subprocess.run(["ffmpeg", "-y", "-i", aiff_path, output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(aiff_path):
                    os.remove(aiff_path)
                return True
            except Exception as e:
                print(f"Mac fallback (say) 生成语音失败: {e}")
                return False
        else:
            if not self.engine:
                print("Windows 环境下 pyttsx3 引擎未正确初始化")
                return False
            try:
                self.engine.save_to_file(text, output_path)
                self.engine.runAndWait()
                return os.path.exists(output_path)
            except Exception as e:
                print(f"Pyttsx3TTS 生成语音失败: {e}")
                return False

class HttpTTS(TTSProvider):
    """预留的 HTTP TTS 类，用于后续对接本地大模型 API 服务"""
    def __init__(self, api_url: str = 'http://localhost:8080/v1/audio/speech', voice_type: str = "female"):
        self.api_url = api_url
        self.http_voice = config.VOICE_PROFILES.get(voice_type, config.VOICE_PROFILES["female"])["http"]
        
    def generate_audio(self, text: str, output_path: str) -> bool:
        try:
            # [占位符]: 这里根据具体模型(如 ChatTTS/CosyVoice)定义 request body
            payload = {
                "input": text,
                "voice": self.http_voice, # 传递请求大模型的具体角色特征
                "response_format": "wav"
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.api_url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.read())
                    return True
                else:
                    print(f"HttpTTS 响应异常: {response.status}")
                    return False
        except Exception as e:
            print(f"HttpTTS 调用失败或接口未启动: {e}")
            return False

if __name__ == "__main__":
    # ===== 阶段 2 独立测试入口 =====
    test_text = "测试跨平台的离线语音合成功能！"
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(parent_dir, "temp")
    test_output = os.path.join(temp_dir, "test_tts.wav")
    
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"正在初始化 Pyttsx3TTS 引擎 (Platform: {sys.platform})...")
    tts = Pyttsx3TTS(voice_type="male")
    print("开始生成音频...")
    success = tts.generate_audio(test_text, test_output)
    if success:
        print(f"✅ TTS 测试成功，音频已保存在: {test_output}")
    else:
        print("❌ TTS 测试失败。")

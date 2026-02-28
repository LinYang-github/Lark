import os
import subprocess
import config

class VideoMixer:
    def mix(self, video_path: str, vocal_audio_path: str, output_path: str):
        """
        核心混流：
        1. 读取原视频，压低原音频音量
        2. 读取合成的新 vocal 音频
        3. 两者混音，并保留原视频流，输出新视频
        """
        bg_vol = config.BACKGROUND_VOLUME_RATIO
        
        # 判断视频流输入是否有音频，用 ffmpeg amix 合并
        cmd = [
            "ffmpeg", "-y", 
            "-i", video_path,
            "-i", vocal_audio_path,
            "-filter_complex", 
            f"[0:a]volume={bg_vol}[bg];[bg][1:a]amix=inputs=2:duration=first:dropout_transition=0[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            output_path
        ]
        
        try:
            # 屏蔽详细输出，若出错则抛出异常
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            # 兼容原视频完全没有音轨的情况，会导致 [0:a] 查找失败
            # 此时直接替换原视频默认音轨为新配音音轨
            cmd_fallback = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", vocal_audio_path,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

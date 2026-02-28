import os
import subprocess
from pydub import AudioSegment
from typing import List

from .subtitle_parser import SubtitleItem
from .tts_provider import TTSProvider

class AudioProcessor:
    def __init__(self, tts_provider: TTSProvider):
        self.tts = tts_provider
        
    def _apply_atempo(self, input_path: str, output_path: str, ratio: float):
        """调用 FFmpeg 的 atempo 滤镜进行音频变速"""
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-filter:a", f"atempo={ratio}",
            output_path
        ]
        # 屏蔽 FFmpeg 输出
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
    def process_subtitles(self, subtitles: List[SubtitleItem], temp_dir: str, max_speed: float) -> str:
        """
        核心处理：遍历字幕并生成整条拼装对齐好的新音轨
        :param subtitles: 解析后的字幕列表
        :param temp_dir: 临时文件存放目录
        :param max_speed: 最大允许的加速倍率
        :return: 最终合成好的 wav 音频绝对路径
        """
        # 初始一个空声轨作为叠加根部
        final_audio = AudioSegment.silent(duration=0)
        current_time_ms = 0
        
        for item in subtitles:
            # 1. 填补间隔静音 (前一句结束到当前句开始)
            if item.start_time_ms > current_time_ms:
                gap = item.start_time_ms - current_time_ms
                final_audio += AudioSegment.silent(duration=gap)
                current_time_ms = item.start_time_ms
                
            # 2. 调用 TTS 接口生成此句字幕片段 (.wav)
            temp_wav = os.path.join(temp_dir, f"tts_{item.index}.wav")
            processed_wav = os.path.join(temp_dir, f"tts_processed_{item.index}.wav")
            
            success = self.tts.generate_audio(item.text, temp_wav)
            if not success or not os.path.exists(temp_wav):
                # 理论上这里的 failed 应该做日志记录，并用静音跳过保证时间轴不错乱
                final_audio += AudioSegment.silent(duration=item.duration_ms)
                current_time_ms += item.duration_ms
                continue
                
            # 3. 读取片段长度，并进行长短校验与处理
            segment = AudioSegment.from_wav(temp_wav)
            segment_dur_ms = len(segment)
            target_dur_ms = item.duration_ms
            
            if segment_dur_ms <= target_dur_ms:
                # 策略: 若 TTS 生成足够快，长度没满，尾部补充静音进行对齐 (Pad)
                diff = target_dur_ms - segment_dur_ms
                segment += AudioSegment.silent(duration=diff)
                final_audio += segment
                current_time_ms += target_dur_ms
            else:
                # 策略: 若 TTS 生成时间过长，计算挤进字幕窗口所需的压缩比率 (atempo加速)
                ratio = segment_dur_ms / target_dur_ms
                if ratio > max_speed:
                    # 超过阈值：先硬性加速到 max_speed
                    self._apply_atempo(temp_wav, processed_wav, max_speed)
                    accelerated_segment = AudioSegment.from_wav(processed_wav)
                    # 再强行进行绝对时间裁剪 (丢弃多余尾部)
                    accelerated_segment = accelerated_segment[:target_dur_ms]
                    final_audio += accelerated_segment
                else:
                    # 在安全接受区间内：完全依据时间比例进行挤压
                    self._apply_atempo(temp_wav, processed_wav, ratio)
                    accelerated_segment = AudioSegment.from_wav(processed_wav)
                    
                    # 以防 FFmpeg 精度毫秒不完全对齐，强制截取
                    accelerated_segment = accelerated_segment[:target_dur_ms]
                    # 余下用静音填平（如果因为四舍五入少了）
                    diff = target_dur_ms - len(accelerated_segment)
                    if diff > 0:
                        accelerated_segment += AudioSegment.silent(duration=diff)
                        
                    final_audio += accelerated_segment
                    
                current_time_ms += target_dur_ms
                
        # 4. 全部循环拼装完毕，导出单条合轨音频
        output_path = os.path.join(temp_dir, "merged_vocal.wav")
        final_audio.export(output_path, format="wav")
        return output_path

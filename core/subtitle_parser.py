import os
import pysrt
from dataclasses import dataclass
from typing import List

@dataclass
class SubtitleItem:
    """定义单条字幕的数据结构，时间统一采用毫秒 (ms) 作为绝对运算单位"""
    index: int           # 字幕序号
    start_time_ms: int   # 开始时间 (毫秒)
    end_time_ms: int     # 结束时间 (毫秒)
    duration_ms: int     # 持续时间 (毫秒)
    text: str            # 字幕文本信息

class SubtitleParser:
    def __init__(self, srt_path: str):
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"找不到字幕文件: {srt_path}")
        self.srt_path = srt_path
        
    def parse(self) -> List[SubtitleItem]:
        """
        解析 SRT 文件，返回结构化的字幕列表。
        强制使用 UTF-8 编码读取，并将多行文本合并单行，利于 TTS 处理。
        """
        # pysrt 会自动推测编码，但明确使用 utf-8 读取较安全
        try:
            subs = pysrt.open(self.srt_path, encoding='utf-8')
        except UnicodeDecodeError:
            # 兼容其他如 gbk 编码
            subs = pysrt.open(self.srt_path, encoding='gbk')
            
        parsed_items = []
        for i, sub in enumerate(subs):
            start_ms = sub.start.ordinal
            end_ms = sub.end.ordinal
            duration_ms = end_ms - start_ms
            
            if duration_ms <= 0:
                continue # 忽略无效时间轴的字幕
            
            # 文本清理：去掉换行和前后空格
            clean_text = sub.text.replace('\n', ' ').strip()
            
            if not clean_text:
                continue # 忽略空字幕
                
            item = SubtitleItem(
                index=i + 1,
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                duration_ms=duration_ms,
                text=clean_text
            )
            parsed_items.append(item)
            
        return parsed_items

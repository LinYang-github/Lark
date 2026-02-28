import os
import shutil
import argparse
import config
from core.subtitle_parser import SubtitleParser
from core.tts_provider import Pyttsx3TTS, HttpTTS
from core.audio_processor import AudioProcessor
from core.video_mixer import VideoMixer

def main():
    parser = argparse.ArgumentParser(description="Lark 视频配音工具")
    parser.add_argument("--video", "-v", required=True, help="输入的原视频路径 (.mp4)")
    parser.add_argument("--srt", "-s", required=True, help="输入的字幕路径 (.srt)")
    parser.add_argument("--output", "-o", default="output.mp4", help="输出的新视频路径")
    parser.add_argument("--tts", "-t", choices=["local", "http"], default="local", help="TTS引擎选择 (local: pyttsx3, http: 离线大模型接口)")
    parser.add_argument("--gender", "-g", choices=config.GENDERS, default="male", help="选择性别")
    parser.add_argument("--style", "-style", choices=config.STYLES, default="broadcaster", help="选择朗读风格")
    args = parser.parse_args()

    print(f"1. 正在解析字幕: {args.srt}")
    parser_module = SubtitleParser(args.srt)
    subtitles = parser_module.parse()
    if not subtitles:
        print("未提取到任何有效字幕。")
        return

    print(f"2. 初始化 TTS 引擎 (性别: {args.gender}, 风格: {args.style})...")
    if args.tts == "local":
        tts = Pyttsx3TTS(rate=150, gender=args.gender, style=args.style)
    else:
        tts = HttpTTS(gender=args.gender, style=args.style)

    if os.path.exists(config.TEMP_DIR):
        shutil.rmtree(config.TEMP_DIR)
    os.makedirs(config.TEMP_DIR, exist_ok=True)

    print("3. 音频合成与时间轴对齐处理 (耗时操作)...")
    audio_processor = AudioProcessor(tts)
    try:
        merged_wav = audio_processor.process_subtitles(
            subtitles, 
            temp_dir=config.TEMP_DIR, 
            max_speed=config.MAX_SPEED_UP_RATIO
        )
    except Exception as e:
        print(f"音频处理失败: {e}")
        return

    print("4. 视频音频混流封装...")
    video_mixer = VideoMixer()
    try:
        video_mixer.mix(args.video, merged_wav, args.output)
        print(f"\n🎉 任务全部完成！最终配音视频已保存至: {args.output}")
    except Exception as e:
        print(f"\n❌ 混流拼接失败: {e}")
    finally:
        print("5. 清理临时缓存文件...")
        if os.path.exists(config.TEMP_DIR):
            shutil.rmtree(config.TEMP_DIR)

if __name__ == "__main__":
    main()

import os
import shutil
import pytest
from core.subtitle_parser import SubtitleParser
from core.tts_provider import get_tts_provider
from core.audio_processor import AudioProcessor
import config

# 测试数据路径
DEMO_SRT = os.path.join("demo", "demo.srt")
DEMO_MP4 = os.path.join("demo", "demo.mp4")
TEST_OUTPUT_DIR = "tests/test_output"

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """测试前准备，测试后清理"""
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)
    yield
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)

def test_subtitle_parsing():
    """验证 SRT 解析是否正确"""
    parser = SubtitleParser(DEMO_SRT)
    subs = parser.parse()
    assert len(subs) == 2
    assert subs[0].text == "这是第一句话，演示自动配音效果。"
    assert subs[1].start_time_ms == 4500 # 4.5秒 = 4500ms

def test_native_tts_generation():
    """验证系统原生 TTS 驱动是否能生成文件"""
    params = {
        "mode": "native",
        "gender": "female",
        "rate": 200
    }
    tts = get_tts_provider(params)
    out_ptr = os.path.join(TEST_OUTPUT_DIR, "test_native.wav")
    success = tts.generate_audio("单元测试文本", out_ptr)
    assert success is True
    assert os.path.exists(out_ptr)
    assert os.path.getsize(out_ptr) > 0

def test_audio_processing_logic():
    """验证音频处理器是否能正确计算并合并语音 (使用 Native 引擎)"""
    parser = SubtitleParser(DEMO_SRT)
    subs = parser.parse()
    
    params = {"mode": "native", "gender": "male", "rate": 180}
    tts = get_tts_provider(params)
    
    processor = AudioProcessor(tts)
    merged_wav = processor.process_subtitles(
        subs, 
        temp_dir=TEST_OUTPUT_DIR,
        max_speed=1.5
    )
    
    assert os.path.exists(merged_wav)
    assert merged_wav.endswith(".wav")
    # 验证生成的总长度（demo 最后一句结束于 8s，所以长度应接近 8s）
    # 注意：pydub 计算长度可能会有微秒偏差
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(merged_wav)
    assert 7500 < len(audio) < 8500 

def test_cosyvoice_tts_generation():
    """验证 CosyVoice AI 引擎是否能生成文件 (中文播音腔男声 - 云扬)"""
    params = {
        "mode": "cosyvoice",
        "language": "中文",
        "gender": "male",
        "style": "broadcaster"
    }
    tts = get_tts_provider(params)
    out_ptr = os.path.join(TEST_OUTPUT_DIR, "test_cosyvoice.wav")
    
    # 注意：CosyVoice 生成较慢，可能会耗时 30s+
    success = tts.generate_audio("你好，这是一条 AI 播音腔测试。", out_ptr)
    
    assert success is True
    assert os.path.exists(out_ptr)
    assert os.path.getsize(out_ptr) > 5000 # 确保文件不是空的且有一定大小

def test_cosyvoice_full_workflow():
    """验证全链路 CosyVoice AI 配音流程是否通畅"""
    parser = SubtitleParser(DEMO_SRT)
    subs = parser.parse()
    
    params = {
        "mode": "cosyvoice",
        "language": "中文",
        "gender": "male",
        "style": "broadcaster"
    }
    tts = get_tts_provider(params)
    
    processor = AudioProcessor(tts)
    # 处理 demo (2 句)，预计耗时 1-2 分钟
    merged_wav = processor.process_subtitles(
        subs, 
        temp_dir=TEST_OUTPUT_DIR,
        max_speed=1.5
    )
    
    assert os.path.exists(merged_wav)
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(merged_wav)
    assert len(audio) > 5000 # 保证生成了足够长度的内容

if __name__ == "__main__":
    # 如果直接运行脚本，则执行测试
    pytest.main([__file__])

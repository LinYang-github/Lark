# Lark 视频字幕自动配音工具 (Lark AI Voice Studio)

Lark 是一个专为**完全离线（内网）环境**设计的轻量级自动化视频配音与混轨工具。它通过读取本地的 `.mp4` 视频和配套的 `.srt` 字幕文件，利用 AI 大模型或系统原生引擎自动生成语音，并精准进行时间轴动态对齐，最终合成高质量的配音视频。

---

## 🌟 核心特性

- **🎬 电影级 AI 配音 (New)**：集成阿里 **CosyVoice** 大模型，提供媲美真人的自然语感。支持“播音腔”、“标准”等多种风格。
- **🧩 双引擎模式**：
  - **CosyVoice (AI)**：极高质量，适合正式视频、宣传片。支持 Docker 离线部署。
  - **Native (轻量)**：瞬时生成，直接调用系统底层接口（Mac: `say`, Win: `SAPI5`）。
- **🎛️ 二维语音控制**：独立调控“性别 (男/女)”与“腔调 (标准/播音)”，跨引擎自动映射最佳音色。
- **⏱️ 智能弹性对齐**：音频比字幕长时，自动执行 `atempo` 变速挤压；短时自动填充静默，确保音画绝对同步。
- **🎵 自动化合流**：自动压降原视频环境声（默认 20%），确保配音清晰可闻。
- **🚀 绝对离线**：全链路无需互联网，所有模型 and 计算均在本地完成。

---

## 📦 项目架构

```text
Lark/
├── gui.py                      # 图形化界面入口 (可视化操作)
├── main.py                     # 命令行胶囊调度入口 (自动化脚本)
├── config.py                   # 全局配置中心 (音色映射、混流比例)
├── cosyvoice_api.py            # CosyVoice API 桥接适配器
└── core/
    ├── tts_provider.py         # 多引擎 TTS 驱动实现 (Native/CosyVoice)
    ├── audio_processor.py      # 音频对齐与变速处理
    └── video_mixer.py          # FFmpeg 最终合成引擎
```

---

## 🛠️ 环境准备 (离线部署)

### 1. 基础依赖
- **FFmpeg**: 必须安装并配置系统环境变量。
- **Python-TK**: 如果 Mac 运行 GUI 报错，请执行 `brew install python-tk@3.14` (对应您的 Python 版本)。

### 2. CosyVoice AI 部署 (可选，推荐)
为了获得最高质量的配音，建议启动 CosyVoice 容器：

#### A. 本地预下载模型 (在有网环境)
```bash
source venv/bin/activate
pip install modelscope
python3 -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice-300M', local_dir='./models/CosyVoice-300M')"
```

#### B. 启动容器 (完全离线)
```bash
docker run -d --name lark-cosyvoice \
  -p 50000:50000 -p 9233:9233 \
  -v "$(pwd)/cosyvoice_api.py:/app/cosyvoice_api.py" \
  -v "$(pwd)/models/CosyVoice-300M:/app/models/CosyVoice-300M" \
  --platform linux/amd64 harryliu888/cosyvoice:latest \
  bash -c "python3 webui.py --port 50000 & python3 cosyvoice_api.py"
```

---

## 🚀 使用指南

### 1. 图形化界面 (推荐)
直接运行：
```bash
python gui.py
```
- 在界面选定 `.mp4` 和 `.srt`。
- **TTS 引擎**：选择 `native` 或 `cosyvoice`。
- **语音类型**：选择性别和风格。
- 点击 **“启动自动混流渲染”**。

### 2. 命令行模式
```bash
# 使用 CosyVoice 男声播音腔
python main.py -v input.mp4 -s input.srt -o output.mp4 --tts cosyvoice --gender male --style broadcaster

# 使用系统原生女声
python main.py -v input.mp4 -s input.srt -o output.mp4 --tts native --gender female
```

---

## 💡 注意事项
- **推理性能**：在 Mac ARM 机器上通过 Docker 模拟 x86 运行 CosyVoice，每句语音生成约需 30-50 秒，请耐心等待。
- **断网提示**：启动成功后，您可以完全拔掉网线使用。
- **清理**：程序运行结束后会自动清理 `temp_audio/` 目录下的中间文件。

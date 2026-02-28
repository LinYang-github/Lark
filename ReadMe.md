# 🕊️ Lark AI Voice Studio (Lark 视频字幕自动配音工具)

> **极简、强大、完全离线的视频配音工业级解决方案。**
> 专为政企内网、物理隔离环境设计，支持阿里 CosyVoice 大模型与系统原生引擎双切换。

---

## 📸 界面预览
*(运行 `python gui.py` 即可开启直观的图形化操作界面)*

- **左侧控制面板**：一键导入 MP4 视频与 SRT 字幕。
- **引擎控制中心**：支持 `AI 模式 (CosyVoice)` 与 `轻量模式 (Native)` 自由切换。
- **二维参数调节**：性别 (Male/Female) × 风格 (Standard/Broadcaster) 独立选择。
- **实时进度反馈**：可视化渲染进度条。

---

## 🚀 核心优势 (Why Lark?)

1.  **💎 电影级 AI 音色**：深度集成阿里 **CosyVoice-300M**，告别机械音，享受丝滑自然的播音员语感。
2.  **🔒 绝对物理离线**：不传云端，不连外网。保护您的视频素材隐私与数据安全，完美适配 Windows/Mac 离线环境。
3.  **⏱️ 毫秒级音画同步**：内置智能变速 (`atempo`) 引擎，音频过长自动无损压缩，音频不足自动静默填充，确保每一帧画面都有完美的配音对应。
4.  **🎵 原声压降混音**：自动对原视频背景声进行 20% 避让处理（Audio Ducking），让配音更有质感。

---

## 💻 快速部署与环境配置

针对不同的操作系统，请遵循以下步骤进行环境准备。

### 1. 基础依赖 (共同要求)
- **Python**: 推荐 3.10 - 3.14 版本。
- **FFmpeg**: **必须安装**。
  - 请确保在终端执行 `ffmpeg -version` 有输出。
  - **Windows**: 下载 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 构建版本，并将 `bin` 目录添加至系统变量 `PATH`。
  - **macOS**: 建议通过 `brew install ffmpeg` 安装。

### 2. 下载依赖包
#### Windows (PowerShell/CMD):
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### macOS (Terminal):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. CosyVoice AI 引擎配置 (高保真配音)
项目支持接入基于 Docker 容器运行的 CosyVoice 服务以实现最高音质输出。

#### A. 模型权重预下载 (联网环境执行)
```bash
pip install modelscope
python -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice-300M', local_dir='./models/CosyVoice-300M')"
```

#### B. 启动容器服务 (离线可用)
确保已安装并运行 **Docker Desktop**。

**Windows (PowerShell):**
```powershell
docker run -d --name lark-cosyvoice `
  -p 50000:50000 -p 9233:9233 `
  -v "${PWD}/cosyvoice_api.py:/app/cosyvoice_api.py" `
  -v "${PWD}/models/CosyVoice-300M:/app/models/CosyVoice-300M" `
  --platform linux/amd64 harryliu888/cosyvoice:latest `
  bash -c "python3 webui.py --port 50000 & python3 cosyvoice_api.py"
```

**macOS (Terminal):**
```bash
docker run -d --name lark-cosyvoice \
  -p 50000:50000 -p 9233:9233 \
  -v "$(pwd)/cosyvoice_api.py:/app/cosyvoice_api.py" \
  -v "$(pwd)/models/CosyVoice-300M:/app/models/CosyVoice-300M" \
  --platform linux/amd64 harryliu888/cosyvoice:latest \
  bash -c "python3 webui.py --port 50000 & python3 cosyvoice_api.py"
```

---

## �️ 项目结构

- `gui.py`: **主入口**。运行后弹出可视化窗口。
- `main.py`: 命令行入口。适合批量处理脚本。
- `config.py`: 配置中心。可在此修改默认音量比例 (20%) 或 Windows 系统音色 ID。
- `core/`: 核心引擎文件夹，包含字幕解析、TTS 驱动及视频混流。

---

## 📝 快速上手

1.  运行 `python gui.py`。
2.  选择您的视频和字幕文件。
3.  **模式建议**：
    - **快速预览**：选择 `native` 引擎。它会调用 Windows 内置的 `Huihui` 或 `Kangkang` (SAPI5)，速度极快。
    - **最终成片**：启动 Docker 后选择 `cosyvoice` 引擎，使用 `Male` + `Broadcaster` (云扬音色)，体验极致 AI 效果。
4.  点击 **“启动自动混流渲染”**。
5.  成品视频将自动保存在原视频同目录下。

---

## 💡 注意事项
- **Windows 用户**：若运行 `gui.py` 提示找不到 `tkinter`，通常是因为 Python 安装时未勾选 `tcl/tk` 组件。请重新运行 Python 安装程序并勾选 `Modify` -> `tcl/tk and IDLE`。
- **资源清理**：程序运行完成后会自动清理 `temp_audio/` 中的零碎文件，请勿在运行期间手动删除该目录。

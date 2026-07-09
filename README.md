# AutoCast

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **中文**：面向开源维护者的 **AI Agent 内容流水线**。AutoCast 自动读取 GitHub 原生数据（README、CHANGELOG、Issues、PRs），由大模型生成脚本，再由 FFmpeg 渲染为短视频和信息图，让开源项目的每次发版都能自动产出传播素材。
>
> **English**: An **AI Agent content pipeline for open-source maintainers**. AutoCast reads native GitHub data (README, CHANGELOG, Issues, PRs), generates scripts via LLMs, and renders them into short videos and infographics with FFmpeg—so every release automatically produces marketing content.

---

## 🎯 AI Agent Positioning / AI Agent 定位

AutoCast 是一个**数据驱动的 Agent**：

- **输入**：GitHub 仓库数据（文档、Issue、PR、Release、Contributors）
- **大脑**：DeepSeek / OpenAI / MiMo / Local LLM 生成内容脚本
- **手脚**：Python 流水线 + HTML/CSS 模板 + FFmpeg 本地渲染
- **输出**：可直接发布到社交媒体的短视频与信息图

它把维护者从“发版后还要写推文、做视频”的重复劳动中解放出来。

---

## ✨ Features / 核心特性

| Feature / 功能 | Description / 说明 |
|---|---|
| 🎬 **Doc → Video** / 文档转视频 | README / CHANGELOG → 60 秒发布解说视频。 |
| 🐛 **Issue → Visual** / Issue 转信息图 | Bug 修复说明自动生成可视化卡片。 |
| 🤖 **LLM-Powered Scripting** / LLM 驱动 | 支持 DeepSeek、OpenAI、MiMo、本地模型作为内容生成大脑。 |
| 🎨 **Template Market** / 模板市场 | Release Note、Bug Fix、Feature Demo、Contributor Thanks 等模板。 |
| 🔧 **GitHub Action Ready** / 一键 CI | 添加一个 workflow 即可在发版时自动触发。 |
| 🖥️ **Local Rendering** / 本地渲染 | 纯 FFmpeg 本地渲染，不依赖云端视频服务。 |

---

## 🏗️ Architecture / 架构

```
GitHub Data (README / CHANGELOG / Issue / PR)
        │
        ▼
┌─────────────────────────────────────┐
│  AutoCast AI Agent Pipeline         │
│  ├── parsers: extract repo facts    │
│  ├── generators: LLM script writer  │
│  ├── templates: HTML/CSS scenes     │
│  └── renderers: FFmpeg renderer     │
└─────────────────────────────────────┘
        │
        ▼
   output/release_video.mp4
   output/issue_visual.png
```

```
AutoCast/
├── autocast/                    # AI Agent 核心引擎
│   ├── pipelines/               # 流水线实现
│   │   ├── doc_to_video.py      # README → 视频
│   │   └── issue_to_visual.py   # Issue → 信息图
│   ├── generators/              # LLM 内容生成适配器
│   ├── templates/               # 视频模板（HTML/CSS）
│   └── renderers/               # FFmpeg 渲染层
├── .github/workflows/           # GitHub Action 模板
├── config.yaml                  # 项目配置
├── examples/                    # 示例项目
└── README.md                    # 本文件
```

---

## 🚀 Quick Start / 快速开始

### 1. Install / 安装

```bash
git clone https://github.com/Julie-Wang/AutoCast.git
cd AutoCast
pip install -r requirements.txt
```

### 2. Configure / 配置

Edit `config.yaml`:

```yaml
project:
  name: "your-awesome-project"
  repo_url: "https://github.com/you/your-awesome-project"

pipeline:
  doc_to_video:
    source: "README.md"
    template: "release_note"
    output_dir: "output/videos"

models:
  content_generator:
    provider: "deepseek"        # deepseek / openai / xiaomi / local
    model: "deepseek-chat"
    api_key: "${DEEPSEEK_API_KEY}"
    base_url: "https://api.deepseek.com/v1"
```

### 3. Run / 运行

```bash
# Generate release note video / 生成发布说明视频
python -m autocast pipeline doc_to_video README.md --template release_note

# Generate issue summary infographic / 生成 Issue 总结信息图
python -m autocast pipeline issue_to_visual --issue 123
```

### 4. GitHub Action Integration / GitHub Action 集成

Add `.github/workflows/autocast.yml` to your project:

```yaml
name: AutoCast Release Video
on:
  release:
    types: [published]
jobs:
  autocast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Julie-Wang/AutoCast@v1
        with:
          template: "release_note"
          output: "release_video.mp4"
```

---

## 🎨 Template Market / 模板市场

| Template / 模板 | Scenario / 场景 | Input / 输入 | Output / 输出 |
|---|---|---|---|
| `release_note` | Version release / 版本发布 | CHANGELOG | 60s explainer video |
| `bug_fix` | Bug fix demo / Bug 修复说明 | Issue + PR | 30s fix demo |
| `feature_demo` | New feature showcase / 新功能演示 | README section | 45s feature video |
| `contributor_thanks` | Contributor thanks / 贡献者致谢 | Contributors list | 15s thank-you video |

---

## 🛠️ Tech Stack / 技术栈

- **Python 3.10+** — pipeline orchestration
- **FFmpeg** — video rendering
- **Node.js 18+** — optional visual pipeline
- **HTML/CSS** — animated templates
- **LLM APIs** — DeepSeek / OpenAI / MiMo / local models

---

## 🤝 Contributing / 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

Issues and PRs are welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📄 License / 许可证

This project is licensed under the [MIT License](./LICENSE).

本项目采用 [MIT 许可证](./LICENSE)。

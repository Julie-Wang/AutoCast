# AutoCast

> 让开源项目自动生成内容：README → 视频，Issue → 信息图，Release → 社交媒体素材。

AutoCast 是一个面向**开源维护者**的 AI 内容流水线工具。它将 GitHub 原生数据（README、CHANGELOG、Issues、PRs）自动转化为短视频和信息图，把维护者从内容生产的重复劳动中解放出来。

## 为什么需要 AutoCast？

开源维护者面临双重负担：
- 写代码、审 PR、发版本
- 做内容传播：写 Release Note、做演示视频、发社交媒体

AutoCast 通过自动化流水线，**让任何开源项目在每次发版时自动生成宣传视频**。

## 核心特性

- 🎬 **双管线架构**：Python 线（文档→视频）+ Node 线（数据→视觉）
- 🔧 **GitHub Action 一键集成**：添加一个 workflow 文件即可接入
- 🎨 **内置模板市场**：Release Note、Bug 修复说明、新功能演示等模板
- 🧠 **多模型适配**：支持 OpenAI / DeepSeek / 本地模型作为内容生成大脑
- 🖥️ **纯本地渲染**：FFmpeg 本地执行，不依赖云服务

## 快速开始

### 1. 安装

```bash
git clone https://github.com/Julie-Wang/AutoCast.git
cd AutoCast
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml`：

```yaml
project:
  name: "your-awesome-project"
  repo_url: "https://github.com/you/your-awesome-project"

pipeline:
  doc_to_video:
    source: "README.md"
    template: "release_note"
    output: "output/release_video.mp4"

models:
  content_generator: "deepseek"  # 或 openai / xiaomi
  api_key: "${DEEPSEEK_API_KEY}"
```

### 3. 运行

```bash
# 生成 Release Note 视频
python -m autocast pipeline doc_to_video --template release_note

# 生成 Issue 总结信息图
python -m autocast pipeline issue_to_visual --issue 123
```

### 4. GitHub Action 集成

在你的项目中添加 `.github/workflows/autocast.yml`：

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

## 架构

```
AutoCast/
├── autocast/               # 核心引擎
│   ├── pipelines/          # 流水线实现
│   │   ├── doc_to_video.py # README → 视频
│   │   └── issue_to_visual.py # Issue → 信息图
│   ├── templates/          # 视频模板（HTML/CSS）
│   ├── generators/         # AI 内容生成适配器
│   └── renderers/          # FFmpeg 渲染层
├── .github/
│   └── workflows/          # GitHub Action 模板
├── config.yaml             # 项目配置
└── examples/               # 示例项目
```

## 模板市场

| 模板 | 场景 | 输入 | 输出 |
|------|------|------|------|
| `release_note` | 版本发布 | CHANGELOG | 60秒解说视频 |
| `bug_fix` | Bug 修复说明 | Issue + PR | 30秒修复演示 |
| `feature_demo` | 新功能演示 | README 章节 | 45秒功能展示 |
| `contributor_thanks` | 贡献者致谢 | Contributors 列表 | 15秒感谢视频 |

## 技术栈

- Python 3.10+
- FFmpeg
- Node.js 18+（Node 线）
- HTML/CSS 动画模板

## 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License

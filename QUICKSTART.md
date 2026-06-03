# 快速启动指南

## 5 分钟上手

### 1. 克隆仓库
```bash
git clone https://github.com/Julie-Wang/AutoCast.git
cd AutoCast
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
编辑 `config.yaml`，设置你的 AI 模型 API Key：
```yaml
models:
  content_generator:
    provider: "deepseek"
    api_key: "${DEEPSEEK_API_KEY}"  # 或直接在环境变量设置
```

### 4. 运行示例
```bash
# 生成 Release Note 视频
python -m autocast pipeline doc_to_video examples/demo-project/README.md --template release_note --output demo
```

### 5. 查看结果
输出视频在 `output/videos/demo.mp4`

---

## GitHub Action 集成

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
```

每次发布 Release 时，会自动生成并上传视频！

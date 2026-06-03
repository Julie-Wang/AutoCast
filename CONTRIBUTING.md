# 贡献指南

感谢你对 AutoCast 的兴趣！

## 如何贡献

### 报告 Bug
- 使用 GitHub Issues 描述问题
- 提供复现步骤、环境信息、错误日志

### 提交功能请求
- 在 Issues 中描述你的使用场景
- 说明为什么这个功能对开源维护者有帮助

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境

```bash
git clone https://github.com/YOUR_USERNAME/AutoCast.git
cd AutoCast
pip install -r requirements.txt
pip install -e .
```

### 代码风格
- 遵循 PEP 8
- 使用类型注解
- 添加 docstring

## 模板贡献

欢迎提交新的视频模板！模板放在 `autocast/templates/` 目录下。

模板结构：
```
templates/
├── release_note/
│   ├── template.html    # HTML 动画模板
│   ├── style.css        # 样式
│   └── config.yaml      # 模板配置
```

## 许可证

通过提交代码，你同意你的贡献将在 MIT 许可证下发布。

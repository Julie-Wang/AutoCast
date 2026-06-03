#!/bin/bash
# AutoCast 打包脚本

echo "📦 打包 AutoCast..."

# 创建发布目录
mkdir -p dist
cd dist

# 复制核心文件
cp -r ../autocast .
cp ../README.md .
cp ../requirements.txt .
cp ../setup.py .
cp ../LICENSE .
cp ../CONTRIBUTING.md .
cp ../config.yaml .
cp -r ../examples .
cp -r ../.github .

# 创建 zip
cd ..
zip -r AutoCast-v0.1.0.zip dist/

echo "✅ 打包完成: AutoCast-v0.1.0.zip"

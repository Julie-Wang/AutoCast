"""AI 内容生成适配器 - 支持多模型"""
import os
import requests
from typing import Optional, Dict, Any

class ContentGenerator:
    """统一的内容生成接口"""

    def __init__(self, config: Dict[str, Any]):
        self.provider = config.get("provider", "deepseek")
        self.model = config.get("model", "deepseek-chat")
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")

        # 未配置 API Key 时自动降级为 mock 模式
        # 支持空字符串或 ${VAR} 占位符两种未配置情况
        if not self.api_key or self.api_key.startswith("${"):
            print("[mock] 未配置 API Key，已切换到 mock 模式（返回模拟脚本）")
            self.provider = "mock"

    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 2000) -> str:
        """生成内容"""
        if self.provider == "deepseek":
            return self._call_deepseek(prompt, system_prompt, max_tokens)
        elif self.provider == "openai":
            return self._call_openai(prompt, system_prompt, max_tokens)
        elif self.provider == "xiaomi":
            return self._call_xiaomi(prompt, system_prompt, max_tokens)
        elif self.provider == "mock":
            return self._call_mock(prompt, system_prompt, max_tokens)
        else:
            raise ValueError(f"不支持的模型提供商: {self.provider}")

    def _call_deepseek(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """调用 DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _call_openai(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """调用 OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _call_xiaomi(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """调用小米大模型 API（占位，需根据实际 API 调整）"""
        # 小米 API 适配，根据实际接口调整
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "max_tokens": max_tokens
        }

        # 这里需要根据小米实际 API 地址调整
        response = requests.post(
            "https://api.xiaomi.ai/v1/chat",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json().get("text", "")

    def _call_mock(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """Mock 模式：解析文档内容，返回结构化模拟脚本 JSON"""
        import json
        import re

        # 从 prompt 中提取文档内容
        doc_content = ""
        if "\n\n" in prompt:
            doc_content = prompt.split("\n\n", 1)[1]
        else:
            doc_content = prompt

        # 提取项目标题（第一行 # 标题）
        title_match = re.search(r'^#\s+(.+)$', doc_content, re.MULTILINE)
        project_name = title_match.group(1).strip() if title_match else "Example Project"

        # 提取功能列表
        features = []
        # 匹配 Features 章节下的列表项
        feature_section = re.search(
            r'##\s*Features\s*\n((?:\s*[-*]\s*.+\n?)+)',
            doc_content, re.IGNORECASE | re.MULTILINE
        )
        if feature_section:
            features = re.findall(r'[-*]\s*(.+)', feature_section.group(1))
        else:
            # 全局搜索列表项作为备选
            features = re.findall(r'^[-*]\s*(.+)$', doc_content, re.MULTILINE)

        # 提取版本号
        version_match = re.search(r'v(\d+\.\d+\.\d+)', doc_content)
        version = f"v{version_match.group(1)}" if version_match else "v1.0.0"

        # 构建口语化解说词
        feature_text = "、".join(features[:3]) if features else "强大的核心功能"

        segments = [
            {
                "text": f"大家好，今天给大家介绍 {project_name}。{version} 版本正式发布，带来了多项重要更新。",
                "duration": 8,
                "visual_hint": "🎬 项目Logo"
            },
            {
                "text": f"核心功能包括：{feature_text}。每一个功能都经过精心设计，让你开发更高效。",
                "duration": 12,
                "visual_hint": "✨ 功能列表"
            },
            {
                "text": "使用非常简单，几行代码即可上手。无论是新手还是专家，都能快速融入。",
                "duration": 10,
                "visual_hint": "💻 代码演示"
            },
            {
                "text": f"{version} 版本还修复了已知问题，性能大幅提升。赶紧到 GitHub 体验，给项目点个 Star 吧！",
                "duration": 8,
                "visual_hint": "🚀 行动号召"
            }
        ]

        return json.dumps({
            "title": f"{project_name} {version} 发布",
            "project_name": project_name,
            "version": version,
            "segments": segments
        }, ensure_ascii=False)

# 工厂函数
def create_generator(config: Dict[str, Any]) -> ContentGenerator:
    """根据配置创建对应的内容生成器"""
    return ContentGenerator(config)

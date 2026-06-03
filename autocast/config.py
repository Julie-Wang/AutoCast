"""配置加载模块"""
import os
import yaml
from pathlib import Path

# 优先加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)
except ImportError:
    pass


class Config:
    """AutoCast 配置管理"""

    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.data = self._load()

    def _load(self):
        """加载 YAML 配置，支持环境变量替换"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换环境变量 ${VAR} → os.environ.get("VAR")
        import re
        def replace_env(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        content = re.sub(r'\$\{([^}]+)\}', replace_env, content)

        return yaml.safe_load(content)

    def get(self, key_path, default=None):
        """通过点号路径获取配置，如 'models.content_generator.provider'"""
        keys = key_path.split(".")
        value = self.data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def project_name(self):
        return self.get("project.name", "Unknown")

    @property
    def repo_url(self):
        return self.get("project.repo_url", "")

    @property
    def output_dir(self):
        return Path(self.get("pipeline.doc_to_video.output_dir", "output/videos"))

# 全局配置实例
_config = None

def get_config(config_path="config.yaml"):
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config

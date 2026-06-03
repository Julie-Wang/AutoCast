"""文档转视频流水线"""
import io
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import markdown
from jinja2 import Template

# 修复 Windows 终端编码问题
_old_stdout = sys.stdout
_old_stderr = sys.stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from autocast.config import get_config
from autocast.generators.ai_generator import create_generator
from autocast.renderers.template_renderer import render_slides


class DocToVideoPipeline:
    """将 Markdown 文档转换为短视频"""

    def __init__(self, config_path="config.yaml"):
        self.config = get_config(config_path)
        self.generator = create_generator(self.config.get("models.content_generator", {}))
        self.output_dir = Path(self.config.get("pipeline.doc_to_video.output_dir", "output/videos"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.resolution = self.config.get("render.resolution", "1080p")
        self.res_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "9:16": (1080, 1920)
        }

    def run(self, source_path: str, template_name: str = "release_note", output_name: str = None):
        """执行完整流水线"""
        print(f"🎬 开始处理: {source_path}")

        # 1. 读取源文档
        doc_content = self._read_document(source_path)
        print("  [1/5] 📄 文档读取完成")

        # 2. AI 生成视频脚本
        script = self._generate_script(doc_content, template_name)
        print("  [2/5] 📝 脚本生成完成")

        # 3. 生成 TTS 音频
        audio_path = self._generate_audio(script, output_name)
        print("  [3/5] 🔊 音频生成完成")

        # 4. 生成幻灯片/画面
        slides = self._generate_slides(script, template_name)
        print("  [4/5] 🖼️  幻灯片渲染完成")

        # 5. 合成视频
        video_path = self._render_video(slides, audio_path, output_name, script)
        print("  [5/5] 🎞️  视频合成完成")

        print(f"✅ 视频生成完成: {video_path}")
        return video_path

    def _read_document(self, path: str) -> str:
        """读取 Markdown 文档"""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _generate_script(self, doc_content: str, template_name: str) -> Dict[str, Any]:
        """使用 AI 生成视频脚本"""

        system_prompt = """你是一个开源项目的技术传播专家。请将给定的项目文档转换为适合短视频解说的脚本。
要求：
1. 总时长控制在 60 秒内，约 150-200 个中文字
2. 语言口语化，避免过于技术化的术语
3. 结构：开场吸引注意 → 核心功能介绍 → 使用场景 → 结尾号召
4. 输出 JSON 格式：{"title": "标题", "segments": [{"text": "段落文字", "duration": 秒数, "visual_hint": "画面提示"}]}"""

        prompt = f"请将以下项目文档转换为短视频脚本：\n\n{doc_content[:3000]}"

        response = self.generator.generate(prompt, system_prompt)

        import json
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {
            "title": "项目介绍",
            "segments": [
                {"text": response[:200], "duration": 10, "visual_hint": "项目 Logo"},
                {"text": response[200:400], "duration": 10, "visual_hint": "代码截图"},
                {"text": response[400:600], "duration": 10, "visual_hint": "使用演示"}
            ]
        }

    def _generate_audio(self, script: Dict[str, Any], output_name: str = None) -> str:
        """使用 Edge TTS 生成音频"""
        import edge_tts
        import asyncio

        text = "\n".join([seg["text"] for seg in script.get("segments", [])])

        if not output_name:
            output_name = "output"

        audio_path = self.output_dir / f"{output_name}.mp3"

        async def _tts():
            communicate = edge_tts.Communicate(
                text,
                voice="zh-CN-XiaoxiaoNeural",
                rate="+0%",
                pitch="+0Hz"
            )
            await communicate.save(str(audio_path))

        asyncio.run(_tts())

        return str(audio_path)

    def _get_resolution(self) -> tuple:
        """解析分辨率配置（支持字符串或 [w, h] 列表）"""
        if isinstance(self.resolution, (list, tuple)) and len(self.resolution) == 2:
            return tuple(self.resolution)
        return self.res_map.get(self.resolution, (1920, 1080))

    def _generate_slides(self, script: Dict[str, Any], template_name: str) -> List[str]:
        """生成幻灯片画面（PIL 高质量渲染）"""
        slides_dir = self.output_dir / "slides"
        w, h = self._get_resolution()
        return render_slides(script, slides_dir, width=w, height=h, template_name=template_name)

    def _render_video(self, slides: List[str], audio_path: str, output_name: str = None,
                      script: Dict[str, Any] = None) -> str:
        """使用 FFmpeg 合成视频（支持转场、Ken Burns、多分辨率）"""
        if not output_name:
            output_name = "output"

        video_path = self.output_dir / f"{output_name}.mp4"
        w, h = self._get_resolution()

        segments = script.get("segments", []) if script else []
        durations = [seg.get("duration", 5) for seg in segments] if segments else [5] * len(slides)

        # 如果没有脚本时长，平均分配
        if len(durations) < len(slides):
            durations.extend([5] * (len(slides) - len(durations)))

        fade_dur = 1.0  # 转场时长（秒）
        fps = 30

        # 构建 filter_complex
        inputs = []
        filters = []

        for i, (slide, dur) in enumerate(zip(slides, durations)):
            inputs.extend(["-loop", "1", "-t", str(dur), "-i", slide])
            # Ken Burns: zoompan + trim
            frames = int(dur * fps)
            filters.append(
                f"[{i}:v]zoompan=z='min(zoom+0.0015,1.5)':d={frames}:s={w}x{h}:fps={fps},"  # Ken Burns
                f"trim=duration={dur},fps={fps},format=yuv420p[v{i}]"
            )

        # xfade 转场连接
        if len(slides) == 1:
            filters.append("[v0]format=yuv420p[video]")
        else:
            cumulative = 0.0
            offsets = []
            for dur in durations[:-1]:
                cumulative += dur
                offsets.append(cumulative - fade_dur * (len(offsets) + 1))

            for i in range(len(slides) - 1):
                in1 = f"v{i}" if i == 0 else f"tmp{i-1}"
                out = f"tmp{i}" if i < len(slides) - 2 else "video"
                filters.append(
                    f"[{in1}][v{i+1}]xfade=transition=fade:duration={fade_dur}:offset={offsets[i]:.2f}[{out}]"
                )

        filter_complex = ";".join(filters)

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[video]",
            "-map", f"{len(slides)}:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(video_path)
        ]

        total_steps = len(slides) + 1
        print(f"     📐 分辨率: {w}x{h} | 幻灯片: {len(slides)} 张 | 转场: fade")

        try:
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ""
            print(f"     ⚠️  FFmpeg filter_complex 失败，尝试降级方案...")
            print(f"     错误: {stderr[:300]}")
            # 降级方案：简单 concat（无转场）
            return self._render_video_fallback(slides, audio_path, video_path, w, h, durations)

        return str(video_path)

    def _render_video_fallback(self, slides, audio_path, video_path, w, h, durations):
        """降级方案：concat 连接（无转场）"""
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for slide, dur in zip(slides, durations):
                f.write(f"file '{Path(slide).resolve().as_posix()}'\n")
                f.write(f"duration {dur}\n")
            # concat demuxer 需要最后一行重复文件
            if slides:
                f.write(f"file '{Path(slides[-1]).resolve().as_posix()}'\n")

        fallback_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", audio_path,
            "-vsync", "vfr",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(video_path)
        ]

        subprocess.run(fallback_cmd, check=True, capture_output=True)
        return str(video_path)


# CLI 入口
def main():
    import argparse
    parser = argparse.ArgumentParser(description="AutoCast: Doc to Video Pipeline")
    parser.add_argument("source", help="源文档路径")
    parser.add_argument("--template", default="release_note", help="模板名称")
    parser.add_argument("--output", default=None, help="输出文件名")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")

    args = parser.parse_args()

    pipeline = DocToVideoPipeline(args.config)
    pipeline.run(args.source, args.template, args.output)


if __name__ == "__main__":
    main()

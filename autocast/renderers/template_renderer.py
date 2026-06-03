"""PIL 模板渲染器 - 生成高质量幻灯片画面"""
import io
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 修复 Windows 终端编码问题
_old_stdout = sys.stdout
_old_stderr = sys.stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class TemplateRenderer:
    """使用 PIL 渲染幻灯片，支持渐变背景、卡片布局、进度条等"""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self._fonts = {}
        self._load_fonts()

    def _load_fonts(self):
        """加载系统字体（优先中文字体）"""
        font_paths = [
            ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"),  # 微软雅黑
            ("C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"),  # 黑体/宋体
            ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"),  # macOS
            ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),  # Linux
        ]

        self.font_bold = None
        self.font_regular = None
        self.font_emoji = None

        for bold_path, regular_path in font_paths:
            if os.path.exists(bold_path) and self.font_bold is None:
                self.font_bold = bold_path
            if os.path.exists(regular_path) and self.font_regular is None:
                self.font_regular = regular_path

        # 回退到 PIL 默认字体
        if self.font_bold is None:
            self.font_bold = self.font_regular
        if self.font_regular is None:
            self.font_regular = self.font_bold

        # emoji 字体（Windows Segoe UI Emoji）
        emoji_path = "C:/Windows/Fonts/seguiemj.ttf"
        if os.path.exists(emoji_path):
            self.font_emoji = emoji_path
        else:
            self.font_emoji = self.font_regular

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取指定大小的字体"""
        key = f"{'bold' if bold else 'regular'}_{size}"
        if key not in self._fonts:
            path = self.font_bold if bold else self.font_regular
            if path and os.path.exists(path):
                try:
                    self._fonts[key] = ImageFont.truetype(path, size)
                except:
                    self._fonts[key] = ImageFont.load_default()
            else:
                self._fonts[key] = ImageFont.load_default()
        return self._fonts[key]

    def _get_emoji_font(self, size: int) -> ImageFont.FreeTypeFont:
        """获取 emoji 字体"""
        key = f"emoji_{size}"
        if key not in self._fonts:
            if self.font_emoji and os.path.exists(self.font_emoji):
                try:
                    self._fonts[key] = ImageFont.truetype(self.font_emoji, size)
                except:
                    self._fonts[key] = self._get_font(size)
            else:
                self._fonts[key] = self._get_font(size)
        return self._fonts[key]

    def _create_gradient_background(self, color_start: Tuple[int, int, int] = (15, 23, 66),
                                    color_end: Tuple[int, int, int] = (60, 20, 80)) -> Image.Image:
        """创建渐变背景（深蓝到紫色）"""
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            ratio = y / self.height
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def _draw_rounded_rect(self, draw: ImageDraw.Draw, xy: Tuple[int, int, int, int],
                           radius: int = 20, fill: Tuple[int, int, int] = (255, 255, 255, 180),
                           outline: Tuple[int, int, int] = None, width: int = 2):
        """绘制圆角矩形"""
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    def _draw_glow_text(self, draw: ImageDraw.Draw, text: str, pos: Tuple[int, int],
                        font: ImageFont.FreeTypeFont, fill: Tuple[int, int, int] = (255, 255, 255),
                        glow_color: Tuple[int, int, int] = (100, 180, 255), glow_radius: int = 8):
        """绘制带发光效果的文字"""
        x, y = pos
        # 绘制发光层（多层模糊偏移）
        for offset in range(glow_radius, 0, -2):
            alpha = int(80 * (1 - offset / glow_radius))
            glow = (glow_color[0], glow_color[1], glow_color[2])
            draw.text((x - offset, y), text, font=font, fill=glow)
            draw.text((x + offset, y), text, font=font, fill=glow)
            draw.text((x, y - offset), text, font=font, fill=glow)
            draw.text((x, y + offset), text, font=font, fill=glow)
        # 绘制主文字
        draw.text((x, y), text, font=font, fill=fill)

    def _draw_progress_bar(self, draw: ImageDraw.Draw, current: int, total: int,
                           y_pos: int = None):
        """绘制底部进度条"""
        if y_pos is None:
            y_pos = self.height - 60

        bar_width = 400
        bar_height = 8
        x_start = (self.width - bar_width) // 2

        # 背景条
        self._draw_rounded_rect(draw, (x_start, y_pos, x_start + bar_width, y_pos + bar_height),
                                radius=4, fill=(255, 255, 255, 60), outline=None)

        # 进度条
        progress = (current + 1) / total if total > 0 else 0
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            self._draw_rounded_rect(draw,
                                    (x_start, y_pos, x_start + fill_width, y_pos + bar_height),
                                    radius=4, fill=(0, 210, 180), outline=None)

        # 页码文字
        font = self._get_font(20)
        page_text = f"{current + 1} / {total}"
        bbox = draw.textbbox((0, 0), page_text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((self.width - text_w) // 2, y_pos + 18), page_text,
                  font=font, fill=(200, 200, 200))

    def _draw_logo_placeholder(self, draw: ImageDraw.Draw):
        """绘制顶部中央 Logo 占位区域"""
        cx = self.width // 2
        cy = 100
        size = 60

        # 圆形背景
        draw.ellipse([cx - size, cy - size, cx + size, cy + size],
                     fill=(255, 255, 255, 30), outline=(255, 255, 255, 100), width=3)

        # 文字
        font = self._get_font(24)
        text = "LOGO"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((cx - text_w // 2, cy - text_h // 2), text,
                  font=font, fill=(255, 255, 255, 200))

    def render_slide(self, script: Dict[str, Any], segment_index: int, total_segments: int,
                     template_name: str = "release_note") -> Image.Image:
        """渲染单张幻灯片"""
        img = self._create_gradient_background()
        draw = ImageDraw.Draw(img)

        segments = script.get("segments", [])
        seg = segments[segment_index] if segment_index < len(segments) else {}

        # 1. 顶部 Logo 占位
        self._draw_logo_placeholder(draw)

        # 2. 标题（大号+发光）
        title = script.get("title", "项目介绍")
        title_font = self._get_font(72, bold=True)
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = bbox[2] - bbox[0]
        title_x = (self.width - title_w) // 2
        title_y = 200
        self._draw_glow_text(draw, title, (title_x, title_y), title_font,
                             fill=(255, 255, 255), glow_color=(80, 160, 255))

        # 3. 分隔线
        line_y = title_y + 100
        draw.line([(self.width // 4, line_y), (self.width * 3 // 4, line_y)],
                  fill=(255, 255, 255, 100), width=2)

        # 4. 内容卡片区域
        card_x = self.width // 2 - 500
        card_y = line_y + 60
        card_w = 1000
        card_h = 300

        # 卡片背景（半透明圆角矩形）
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            (card_x, card_y, card_x + card_w, card_y + card_h),
            radius=24, fill=(255, 255, 255, 25), outline=(255, 255, 255, 60), width=2
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # 5. Emoji 图标
        visual_hint = seg.get("visual_hint", "")
        emoji_match = re.match(r'^(\S+)\s*(.*)', visual_hint)
        emoji = emoji_match.group(1) if emoji_match else "💡"
        hint_text = emoji_match.group(2) if emoji_match else visual_hint

        emoji_font = self._get_emoji_font(80)
        draw.text((card_x + 40, card_y + 30), emoji, font=emoji_font, fill=(255, 255, 255))

        # 6. 解说文字
        text = seg.get("text", "")
        text_font = self._get_font(36)
        text_x = card_x + 140
        text_y = card_y + 40
        text_w = card_w - 180

        # 自动换行
        lines = self._wrap_text(text, text_font, text_w)
        line_height = 50
        for i, line in enumerate(lines[:4]):  # 最多 4 行
            draw.text((text_x, text_y + i * line_height), line,
                      font=text_font, fill=(240, 240, 240))

        # 7. 画面提示标签
        if hint_text:
            tag_font = self._get_font(22)
            tag_text = f"画面: {hint_text}"
            draw.text((card_x + 40, card_y + card_h - 40), tag_text,
                      font=tag_font, fill=(150, 220, 255))

        # 8. 底部进度条
        self._draw_progress_bar(draw, segment_index, total_segments)

        return img

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """自动换行"""
        if not text:
            return [""]

        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            if bbox and (bbox[2] - bbox[0]) > max_width and current_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]


def render_slides(script: Dict[str, Any], output_dir: Path, width: int = 1920,
                  height: int = 1080, template_name: str = "release_note") -> List[str]:
    """批量渲染所有幻灯片并保存"""
    renderer = TemplateRenderer(width=width, height=height)
    segments = script.get("segments", [])
    paths = []

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, seg in enumerate(segments):
        img = renderer.render_slide(script, i, len(segments), template_name)
        path = output_dir / f"slide_{i:02d}.png"
        img.save(str(path), "PNG")
        paths.append(str(path))

    return paths

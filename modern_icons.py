#!/usr/bin/env python3
"""
现代化图标和资源管理模块
为文件复制工具提供图标和动画效果支持
"""
import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import io

class ModernIcons:
    """现代化图标类，提供程序内使用的各种图标"""

    @staticmethod
    def create_folder_icon(size=(24, 24), color="#2196f3"):
        """创建文件夹图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制文件夹图标
        folder_color = color
        tab_color = ModernIcons.lighten_color(color, 0.8)

        # 文件夹主体
        draw.rounded_rectangle(
            [2, 8, size[0]-2, size[1]-4],
            radius=2,
            fill=folder_color
        )

        # 文件夹标签
        draw.rounded_rectangle(
            [2, 4, size[0]*0.4, 8],
            radius=2,
            fill=tab_color
        )

        return img

    @staticmethod
    def create_file_icon(size=(24, 24), color="#4caf50"):
        """创建文件图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制文档图标
        draw.rounded_rectangle(
            [4, 2, size[0]-4, size[1]-2],
            radius=2,
            fill=color,
            outline=ModernIcons.lighten_color(color, 0.7)
        )

        # 添加折角效果
        points = [(size[0]-8, 2), (size[0]-2, 2), (size[0]-2, 8)]
        draw.polygon(points, fill=ModernIcons.lighten_color(color, 0.6))

        return img

    @staticmethod
    def create_search_icon(size=(20, 20), color="#666666"):
        """创建搜索图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center_x, center_y = size[0]//2 - 2, size[1]//2 - 2
        radius = min(center_x, center_y) - 4

        # 绘制放大镜圆圈
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=color,
            width=2
        )

        # 绘制放大镜手柄
        handle_start = (center_x + radius - 2, center_y + radius - 2)
        handle_end = (size[0] - 2, size[1] - 2)
        draw.line([handle_start, handle_end], fill=color, width=3)

        return img

    @staticmethod
    def create_settings_icon(size=(20, 20), color="#666666"):
        """创建设置图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center_x, center_y = size[0]//2, size[1]//2
        outer_radius = min(center_x, center_y) - 2
        inner_radius = outer_radius - 3

        # 绘制外圆
        draw.ellipse(
            [center_x - outer_radius, center_y - outer_radius,
             center_x + outer_radius, center_y + outer_radius],
            outline=color,
            width=2
        )

        # 绘制内圆（齿轮效果）
        for i in range(6):
            angle = i * 60
            x = center_x + inner_radius * 0.7 * (1 if i % 2 == 0 else 0.5)
            y = center_y + inner_radius * 0.7 * (0.5 if i % 2 == 0 else 1)
            draw.ellipse([x-1, y-1, x+1, y+1], fill=color)

        return img

    @staticmethod
    def create_play_icon(size=(24, 24), color="#4caf50"):
        """创建播放/执行图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制三角形播放按钮
        center_x, center_y = size[0]//2, size[1]//2
        triangle_size = min(size) // 4

        points = [
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x + triangle_size//2, center_y),
            (center_x - triangle_size//2, center_y + triangle_size//2)
        ]

        draw.polygon(points, fill=color)

        return img

    @staticmethod
    def create_clear_icon(size=(20, 20), color="#f44336"):
        """创建清空图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制X图标
        margin = 4
        draw.line([margin, margin, size[0]-margin, size[1]-margin], fill=color, width=2)
        draw.line([size[0]-margin, margin, margin, size[1]-margin], fill=color, width=2)

        return img

    @staticmethod
    def lighten_color(hex_color, factor=0.8):
        """使颜色变亮"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        # 转换为RGB
        r = int(hex_color[:2], 16) if len(hex_color) >= 2 else 0
        g = int(hex_color[2:4], 16) if len(hex_color) >= 4 else 0
        b = int(hex_color[4:6], 16) if len(hex_color) >= 6 else 0

        # 应用因子
        r = int(min(255, r + (255 - r) * (1 - factor)))
        g = int(min(255, g + (255 - g) * (1 - factor)))
        b = int(min(255, b + (255 - b) * (1 - factor)))

        return f"#{r:02x}{g:02x}{b:02x}"

class IconManager:
    """图标管理器，负责加载和缓存图标"""

    def __init__(self):
        self.icon_cache = {}
        self.base_size = (24, 24)

    def get_icon(self, icon_type, size=None, color=None):
        """获取指定类型的图标"""
        cache_key = f"{icon_type}_{size}_{color}"

        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        # 使用默认值
        actual_size = size or self.base_size
        actual_color = color or "#666666"

        # 创建图标
        if icon_type == "folder":
            icon = ModernIcons.create_folder_icon(actual_size, actual_color)
        elif icon_type == "file":
            icon = ModernIcons.create_file_icon(actual_size, actual_color)
        elif icon_type == "search":
            icon = ModernIcons.create_search_icon(actual_size, actual_color)
        elif icon_type == "settings":
            icon = ModernIcons.create_settings_icon(actual_size, actual_color)
        elif icon_type == "play":
            icon = ModernIcons.create_play_icon(actual_size, actual_color)
        elif icon_type == "clear":
            icon = ModernIcons.create_clear_icon(actual_size, actual_color)
        else:
            # 默认创建一个简单的圆形图标
            icon = self._create_default_icon(actual_size, actual_color)

        # 转换为CTkImage并缓存
        ctk_image = ctk.CTkImage(icon, size=actual_size)
        self.icon_cache[cache_key] = ctk_image

        return ctk_image

    def _create_default_icon(self, size, color):
        """创建默认图标"""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center_x, center_y = size[0]//2, size[1]//2
        radius = min(center_x, center_y) - 2

        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            fill=color
        )

        return img

class AnimatedProgress:
    """动画进度条类，提供更丰富的视觉效果"""

    def __init__(self, parent):
        self.parent = parent
        self.progress_bar = None
        self.current_value = 0
        self.target_value = 0
        self.animation_speed = 0.02

    def create_widget(self):
        """创建带动画效果的进度条"""
        self.progress_bar = ctk.CTkProgressBar(self.parent)
        return self.progress_bar

    def set_progress(self, value, animated=True):
        """设置进度值"""
        self.target_value = max(0, min(1.0, value))

        if animated:
            self._animate_progress()
        else:
            self.current_value = self.target_value
            self.progress_bar.set(self.current_value)

    def _animate_progress(self):
        """动画过渡到目标值"""
        if abs(self.current_value - self.target_value) > 0.01:
            # 计算动画步长
            diff = self.target_value - self.current_value
            step = diff * self.animation_speed

            self.current_value += step

            # 更新进度条
            if self.progress_bar:
                self.progress_bar.set(self.current_value)

            # 继续动画
            self.parent.after(20, self._animate_progress)
        else:
            self.current_value = self.target_value
            self.progress_bar.set(self.current_value)

# 全局图标管理器实例
icon_manager = IconManager()

def get_icon(icon_type, size=None, color=None):
    """获取图标的便捷函数"""
    return icon_manager.get_icon(icon_type, size, color)
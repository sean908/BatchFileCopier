#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from file_copier import process_files, check_dependencies, analyze_file_types
from modern_icons import get_icon

# Theme colors (loaded from themes/*.json)
FRAME_COLOR = ("#ffffff", "#212121")
BORDER_COLOR = ("#cccccc", "#333333")
WINDOW_COLOR = ("#f0f0f0", "#1a1a1a")
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    themes_dir = os.path.join(base_dir, "themes")
    for _name in ("modern_blue.json", "modern_light.json", "modern_dark.json"):
        _p = os.path.join(themes_dir, _name)
        if os.path.exists(_p):
            with open(_p, "r", encoding="utf-8") as _f:
                _data = json.load(_f)
            _colors = _data.get("colors", {})
            def _as_pair(val, fallback):
                if isinstance(val, (list, tuple)) and len(val) >= 2:
                    return (val[0], val[1])
                return fallback
            FRAME_COLOR = _as_pair(_colors.get("frame"), FRAME_COLOR)
            BORDER_COLOR = _as_pair(_colors.get("border"), BORDER_COLOR)
            WINDOW_COLOR = _as_pair(_colors.get("window"), WINDOW_COLOR)
            break
except Exception:
    pass

class ModernFileCopierUI:
    def __init__(self):
        # 设置 CustomTkinter 外观
        ctk.set_appearance_mode("system")  # 跟随系统主题
        ctk.set_default_color_theme("blue")  # 默认蓝色主题

        # 颜色主题选择功能已移除，保留默认主题设置

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("Se@n's FilesCopier")
        self.root.geometry("900x996")  # 增大窗口尺寸
        self.root.minsize(800, 600)

        # 配置网格布局
        self.root.grid_rowconfigure(9, weight=1)  # 输出区域行可扩展
        self.root.grid_columnconfigure((0, 1), weight=1)  # 两列都可扩展

        # 启用DPI缩放
        try:
            ctk.set_widget_scaling(1.0)  # 默认缩放
        except:
            pass  # 如果失败则使用默认设置

        # 检查依赖
        check_dependencies()

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # # 标题
        # title_label = ctk.CTkLabel(
        #     self.root,
        #     text="文件复制工具",
        #     font=ctk.CTkFont(size=24, weight="bold")
        # )
        # title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # 源目录框架
        # Top toolbar: theme switcher (right side)
        try:
            top_bar = ctk.CTkFrame(self.root, fg_color=FRAME_COLOR, border_color=BORDER_COLOR, border_width=1)
            top_bar.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
            top_bar.grid_columnconfigure(0, weight=1)
            self.theme_var = ctk.StringVar(value="\u7cfb\u7edf")
            self.theme_label = ctk.CTkLabel(top_bar, text="Theme:", fg_color="transparent")
            self.theme_label.grid(row=0, column=0, padx=(10, 6), pady=8, sticky="e")
            self.theme_combo = ctk.CTkComboBox(top_bar, values=["\u7cfb\u7edf", "\u6d45\u8272", "\u6df1\u8272"], variable=self.theme_var, state="readonly", width=120, command=self.on_theme_change)
            self.theme_combo.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="e")
        except Exception:
            pass

        source_frame = ctk.CTkFrame(self.root, fg_color=FRAME_COLOR, border_color=BORDER_COLOR, border_width=1)
        source_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        source_frame.grid_columnconfigure(1, weight=1)
        # 统一标签列宽，确保第二列（输入）与下方行左缘对齐
        try:
            label_col_width = 140  # px
            source_frame.grid_columnconfigure(0, minsize=label_col_width)
        except Exception:
            pass

        source_label = ctk.CTkLabel(source_frame, text="源目录:", font=ctk.CTkFont(size=14, weight="bold"), image=get_icon("folder", size=(20, 20)), compound="left")
        source_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.source_entry = ctk.CTkEntry(source_frame, placeholder_text="选择要处理的源目录...")
        self.source_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        browse_btn = ctk.CTkButton(source_frame, text="浏览", command=self.browse_source, width=80, image=get_icon("folder", size=(16, 16)), compound="left")
        browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15)

        scan_btn = ctk.CTkButton(source_frame, text="扫描", command=self.scan_source, width=80, image=get_icon("search", size=(16, 16)), compound="left")
        scan_btn.grid(row=0, column=3, padx=(0, 15), pady=15)

        # 文件移动参数设置标题 - 独立一行
        params_title = ctk.CTkLabel(self.root, text="文件移动参数设置", font=ctk.CTkFont(size=16, weight="bold"))
        params_title.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        # 文件移动参数设置框架
        file_params_frame = ctk.CTkFrame(self.root, fg_color=FRAME_COLOR, border_color=BORDER_COLOR, border_width=1)
        file_params_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        file_params_frame.grid_columnconfigure(1, weight=1)
        try:
            file_params_frame.grid_columnconfigure(0, minsize=label_col_width)
        except Exception:
            pass

        # 子容器：承载“目标目录”“操作模式”，避免下方控件影响标签列宽
        top_params_frame = ctk.CTkFrame(file_params_frame, fg_color=FRAME_COLOR)
        top_params_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        top_params_frame.grid_columnconfigure(1, weight=1)

        # 目标目录
        ctk.CTkLabel(file_params_frame, text="目标目录:", font=ctk.CTkFont(size=14, weight="bold"), image=get_icon("folder", size=(20, 20)), compound="left").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.dest_entry = ctk.CTkEntry(file_params_frame, placeholder_text="选择文件复制/移动的目标目录...")
        self.dest_entry.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")

        # 添加浏览目标目录按钮
        dest_browse_btn = ctk.CTkButton(file_params_frame, text="浏览", command=self.browse_dest, width=80, image=get_icon("folder", size=(16, 16)), compound="left")
        dest_browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15, sticky="e")

        # 操作模式和其他选项
        ctk.CTkLabel(file_params_frame, text="操作模式:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=15, pady=15, sticky="w")
        self.operation_var = ctk.StringVar(value="复制")
        operation_combo = ctk.CTkComboBox(file_params_frame, values=["复制", "剪切"], variable=self.operation_var, state="readonly", width=120)
        operation_combo.grid(row=1, column=1, padx=(0, 15), pady=15, sticky="w")

        # 选项复选框
        self.keep_structure_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(file_params_frame, text="保留原有文件夹结构", variable=self.keep_structure_var).grid(row=2, column=0, padx=15, pady=15, sticky="w")

        # 文件后缀
        ctk.CTkLabel(file_params_frame, text="文件后缀(空格分隔):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        self.extensions_entry = ctk.CTkEntry(file_params_frame, placeholder_text="例如: pdf txt xlsx")
        self.extensions_entry.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        # 关键词筛选 - 包含
        # 将顶部两行迁入子容器，确保与“源目录”对齐
        try:
            # 移除原位置控件
            for rc in [(0,0),(0,1),(0,2),(1,0),(1,1)]:
                w = file_params_frame.grid_slaves(row=rc[0], column=rc[1])
                if w:
                    w[0].grid_forget()

            # 重新创建到子容器内（中文）
            ctk.CTkLabel(top_params_frame, text="目标目录:", font=ctk.CTkFont(size=14, weight="bold"), image=get_icon("folder", size=(20, 20)), compound="left").grid(row=0, column=0, padx=15, pady=15, sticky="w")
            self.dest_entry = ctk.CTkEntry(top_params_frame, placeholder_text="选择文件复制/移动的目标目录...")
            self.dest_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
            dest_browse_btn = ctk.CTkButton(top_params_frame, text="浏览", command=self.browse_dest, width=80, image=get_icon("folder", size=(16, 16)), compound="left")
            dest_browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15, sticky="e")
            
            ctk.CTkLabel(top_params_frame, text="操作模式:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=15, pady=15, sticky="w")
            operation_combo2 = ctk.CTkComboBox(top_params_frame, values=["复制", "剪切"], variable=self.operation_var, state="readonly", width=120)
            operation_combo2.grid(row=1, column=1, padx=15, pady=15, sticky="w")

        except Exception:
            pass

        # Align spacing with the source row: 15px paddings
        try:
            w = top_params_frame.grid_slaves(row=0, column=0)
            if w: w[0].grid_configure(padx=15, pady=15)
            w = top_params_frame.grid_slaves(row=0, column=1)
            if w: w[0].grid_configure(padx=15, pady=15)
            w = top_params_frame.grid_slaves(row=0, column=2)
            if w: w[0].grid_configure(padx=(0, 15), pady=15)
            w = top_params_frame.grid_slaves(row=1, column=0)
            if w: w[0].grid_configure(padx=15, pady=15)
            w = top_params_frame.grid_slaves(row=1, column=1)
            if w: w[0].grid_configure(padx=15, pady=15)
            # 将“保持原有文件夹结构”移动到第1列，避免撑大标签列
            w = file_params_frame.grid_slaves(row=2, column=0)
            if w:
                w[0].grid_configure(column=0, sticky="w")
        except Exception:
            pass

        # Ensure column-1 (inputs) start at same x by
        # matching label column minsize to the maximum label width among the three rows.
        try:
            self.root.update_idletasks()
            src_label_w = source_label.winfo_reqwidth()
            tgt_label_w = 0
            mode_label_w = 0
            w = top_params_frame.grid_slaves(row=0, column=0)
            if w:
                try:
                    tgt_label_w = w[0].winfo_reqwidth()
                except Exception:
                    tgt_label_w = 0
            w = top_params_frame.grid_slaves(row=1, column=0)
            if w:
                try:
                    mode_label_w = w[0].winfo_reqwidth()
                except Exception:
                    mode_label_w = 0
            label_col_width = max(src_label_w, tgt_label_w, mode_label_w)
            source_frame.grid_columnconfigure(0, minsize=label_col_width)
            top_params_frame.grid_columnconfigure(0, minsize=label_col_width)
        except Exception:
            pass

        include_frame = ctk.CTkFrame(file_params_frame, fg_color=FRAME_COLOR)
        include_frame.grid(row=5, column=0, padx=15, pady=(15, 5), sticky="w")
        include_label = ctk.CTkLabel(include_frame, text="包含", font=ctk.CTkFont(size=14, weight="bold"), text_color="green", fg_color="transparent")
        include_label.pack(side="left")
        suffix_label = ctk.CTkLabel(include_frame, text="关键词(空格分隔):", font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent")
        suffix_label.pack(side="left")

        self.include_entry = ctk.CTkEntry(file_params_frame, placeholder_text="文件名包含的关键词")
        self.include_entry.grid(row=6, column=0, padx=15, pady=(0, 15), sticky="ew")

        # 关键词筛选 - 排除
        exclude_frame = ctk.CTkFrame(file_params_frame, fg_color=FRAME_COLOR)
        exclude_frame.grid(row=5, column=1, padx=15, pady=(15, 5), sticky="w")
        exclude_label = ctk.CTkLabel(exclude_frame, text="排除", font=ctk.CTkFont(size=14, weight="bold"), text_color="red", fg_color="transparent")
        exclude_label.pack(side="left")
        exclude_suffix_label = ctk.CTkLabel(exclude_frame, text="关键词(空格分隔):", font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent")
        exclude_suffix_label.pack(side="left")

        self.exclude_entry = ctk.CTkEntry(file_params_frame, placeholder_text="要排除的文件关键词")
        self.exclude_entry.grid(row=6, column=1, padx=15, pady=(0, 15), sticky="ew")

        # 记录日志复选框 - 放置在右下角
        self.log_enabled_var = ctk.BooleanVar(value=True)
        log_checkbox = ctk.CTkCheckBox(file_params_frame, text="记录日志", variable=self.log_enabled_var)
        log_checkbox.grid(row=7, column=1, padx=15, pady=(0, 15), sticky="e")

        # 进度条标签
        progress_label = ctk.CTkLabel(self.root, text="进度条", font=ctk.CTkFont(size=14, weight="bold"))
        progress_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)  # 初始进度为0

        # 输出信息标签
        output_label = ctk.CTkLabel(self.root, text="输出信息：", font=ctk.CTkFont(size=14, weight="bold"))
        output_label.grid(row=8, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")

        # 输出显示区域
        output_frame = ctk.CTkFrame(self.root, fg_color=FRAME_COLOR, border_color=BORDER_COLOR, border_width=1)
        output_frame.grid(row=9, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_text = ctk.CTkTextbox(output_frame, font=ctk.CTkFont(family="Consolas", size=11))
        self.output_text.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # 按钮框架
        button_frame = ctk.CTkFrame(self.root, fg_color=FRAME_COLOR, border_color=BORDER_COLOR, border_width=1)
        button_frame.grid(row=10, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        execute_btn = ctk.CTkButton(
            button_frame,
            text="执行操作",
            command=self.execute,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            image=get_icon("play", size=(20, 20)),
            compound="left"
        )
        execute_btn.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        clear_btn = ctk.CTkButton(
            button_frame,
            text="清空输出",
            command=self.clear_output,
            height=40,
            image=get_icon("clear", size=(20, 20)),
            compound="left"
        )
        clear_btn.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        quit_btn = ctk.CTkButton(
            button_frame,
            text="退出程序",
            command=self.quit_app,
            height=40,
            fg_color="darkred",
            hover_color="red"
        )
        quit_btn.grid(row=0, column=2, padx=15, pady=15, sticky="ew")

        # 状态栏
        self.status_var = ctk.StringVar(value="就绪")
        status_bar = ctk.CTkLabel(self.root, textvariable=self.status_var, font=ctk.CTkFont(size=12))
        status_bar.grid(row=11, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        # i18n fixes via Unicode escapes to avoid encoding issues
        try:
            # Source row
            source_label.configure(text="源目录:")
            self.source_entry.configure(placeholder_text="选择要处理的源目录...")
            browse_btn.configure(text="浏览")
            scan_btn.configure(text="扫描")
            params_title.configure(text="文件复制/移动参数")

            # Top params (target dir + mode)
            w = top_params_frame.grid_slaves(row=0, column=0)
            if w: w[0].configure(text="目标目录:")
            self.dest_entry.configure(placeholder_text="选择文件复制/移动的目标目录...")
            w = top_params_frame.grid_slaves(row=0, column=2)
            if w: w[0].configure(text="浏览")
            w = top_params_frame.grid_slaves(row=1, column=0)
            if w: w[0].configure(text="操作模式:")
            w = top_params_frame.grid_slaves(row=1, column=1)
            if w:
                try:
                    w[0].configure(values=["复制", "剪切"])
                except Exception:
                    pass

            # Extensions label and placeholder
            w = file_params_frame.grid_slaves(row=3, column=0)
            if w:
                w[0].configure(text="文件扩展名（空格分隔）：")
            self.extensions_entry.configure(placeholder_text="示例: pdf txt xlsx")

            # Include/Exclude labels and placeholders
            include_label.configure(text="包含")
            suffix_label.configure(text="关键词（空格分隔）：")
            exclude_label.configure(text="排除")
            exclude_suffix_label.configure(text="关键词（空格分隔）：")
            self.include_entry.configure(placeholder_text="文件名包含的关键词")
            self.exclude_entry.configure(placeholder_text="要排除的文件关键词")

            # Keep-structure and log checkbox
            w = file_params_frame.grid_slaves(row=2, column=0)
            if w:
                w[0].configure(text="保留原有文件夹结构")
            log_checkbox.configure(text="记录日志")

            # Progress label and buttons
            progress_label.configure(text="执行进度")
            execute_btn.configure(text="执行操作")
            clear_btn.configure(text="清空输出")
            quit_btn.configure(text="退出程序")
            self.status_var.set("就绪")

            # Even split for include/exclude inputs
            file_params_frame.grid_columnconfigure(0, weight=1)
            file_params_frame.grid_columnconfigure(1, weight=1)
        except Exception:
            pass

        # 文案修正与布局微调（中文）
        try:
            # 顶部：源目录
            source_label.configure(text="源目录:")
            self.source_entry.configure(placeholder_text="选择要处理的源目录...")
            browse_btn.configure(text="浏览")
            scan_btn.configure(text="扫描")
            params_title.configure(text="文件复制/移动参数")

            # 文件扩展名标签与占位
            w = file_params_frame.grid_slaves(row=3, column=0)
            if w:
                w[0].configure(text="文件扩展名（空格分隔）：")
            self.extensions_entry.configure(placeholder_text="示例: pdf txt xlsx")

            # 包含/排除 文字与占位
            include_label.configure(text="包含")
            suffix_label.configure(text="关键词（空格分隔）：")
            exclude_label.configure(text="排除")
            exclude_suffix_label.configure(text="关键词（空格分隔）：")
            self.include_entry.configure(placeholder_text="文件名包含的关键词")
            self.exclude_entry.configure(placeholder_text="要排除的文件关键词")

            # 保留原有文件夹结构复选框与日志复选框
            w = file_params_frame.grid_slaves(row=2, column=0)
            if w:
                w[0].configure(text="保留原有文件夹结构")
            log_checkbox.configure(text="记录日志")

            # 让包含/排除输入框均分空间
            file_params_frame.grid_columnconfigure(0, weight=1)
            file_params_frame.grid_columnconfigure(1, weight=1)

            # 操作按钮与状态栏文字
            execute_btn.configure(text="执行操作")
            clear_btn.configure(text="清空输出")
            quit_btn.configure(text="退出程序")
            self.status_var.set("就绪")
        except Exception:
            pass

    def on_theme_change(self, selected):
        mapping = {"系统": "system", "浅色": "light", "深色": "dark", "System": "system", "Light": "light", "Dark": "dark"}
        mode = mapping.get(selected, "system")
        try:
            ctk.set_appearance_mode(mode)
        except Exception:
            pass
        try:
            if 'WINDOW_COLOR' in globals():
                self.root.configure(fg_color=WINDOW_COLOR)
        except Exception:
            pass

    def browse_source(self):
        """浏览选择源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, directory)

    def browse_dest(self):
        """浏览选择目标目录"""
        directory = filedialog.askdirectory(title="选择目标目录")
        if directory:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, directory)

    def scan_source(self):
        """扫描源目录中的文件类型"""
        source_dir = self.source_entry.get().strip()

        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("错误", "请选择有效的源目录")
            return

        # 清空输出区域
        self.output_text.delete("0.0", "end")
        self.status_var.set("正在扫描目录...")
        self.root.update()

        # 重定向标准输出到文本区域
        class TextRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, string):
                self.text_widget.insert("end", string)
                self.text_widget.see("end")

            def flush(self):
                pass

        # 保存原始标准输出
        original_stdout = sys.stdout
        try:
            # 重定向输出
            sys.stdout = TextRedirector(self.output_text)

            # 执行扫描
            analyze_file_types(source_dir)

        except Exception as e:
            self.output_text.insert("end", f"\n扫描过程中发生错误: {str(e)}\n")
        finally:
            # 恢复原始标准输出
            sys.stdout = original_stdout
            self.status_var.set("扫描完成")

    def change_theme(self, selected_theme):
        """切换应用主题"""
        if selected_theme == "系统":
            ctk.set_appearance_mode("system")
        elif selected_theme == "浅色":
            ctk.set_appearance_mode("light")
        elif selected_theme == "深色":
            ctk.set_appearance_mode("dark")

    def change_appearance(self, selected_appearance):
        """切换外观模式"""
        if selected_appearance == "系统":
            ctk.set_appearance_mode("system")
        elif selected_appearance == "浅色":
            ctk.set_appearance_mode("light")
        elif selected_appearance == "深色":
            ctk.set_appearance_mode("dark")

    # 颜色主题选择功能已移除

    def clear_output(self):
        """清空输出区域"""
        self.output_text.delete("0.0", "end")
        self.progress_bar.set(0)
        self.status_var.set("输出已清空")

    def execute(self):
        """执行文件处理操作"""
        source_dir = self.source_entry.get().strip()
        dest_dir = self.dest_entry.get().strip()

        # 验证输入
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("错误", "请选择有效的源目录")
            return

        if not dest_dir:
            messagebox.showerror("错误", "请选择目标目录")
            return

        # 获取其他参数
        is_move = self.operation_var.get() == "剪切"
        keep_structure = self.keep_structure_var.get()
        log_enabled = self.log_enabled_var.get()

        # 处理文件后缀
        extensions_text = self.extensions_entry.get().strip()
        extensions = []
        if extensions_text:
            extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions_text.split()]

        # 处理包含/排除关键词
        include_text = self.include_entry.get().strip()
        include_keywords = include_text.split() if include_text else None

        exclude_text = self.exclude_entry.get().strip()
        exclude_keywords = exclude_text.split() if exclude_text else None

        # 确认操作
        op_type = "移动" if is_move else "复制"
        confirm_msg = f"确定要{op_type}文件吗？\n\n"
        confirm_msg += f"源目录: {source_dir}\n"
        confirm_msg += f"目标目录: {dest_dir}\n"
        if extensions:
            confirm_msg += f"文件后缀: {', '.join(extensions)}\n"
        if include_keywords:
            confirm_msg += f"包含关键词: {', '.join(include_keywords)}\n"
        if exclude_keywords:
            confirm_msg += f"排除关键词: {', '.join(exclude_keywords)}\n"
        confirm_msg += f"保留文件夹结构: {'是' if keep_structure else '否'}\n"
        confirm_msg += f"日志记录: {'启用' if log_enabled else '禁用'}\n"

        if not messagebox.askyesno("确认操作", confirm_msg):
            return

        # 更新状态
        self.status_var.set(f"正在{op_type}文件...")
        self.progress_bar.set(0)
        self.root.update()

        # 清空输出区域
        self.output_text.delete("0.0", "end")

        # 重定向标准输出到文本区域
        class TextRedirector:
            def __init__(self, text_widget, progress_bar):
                self.text_widget = text_widget
                self.progress_bar = progress_bar
                self.total_files = 0
                self.processed_files = 0

            def write(self, string):
                self.text_widget.insert("end", string)
                self.text_widget.see("end")
                # 更新进度条（基于简单的启发式）
                if "处理文件:" in string:
                    self.processed_files += 1
                    if self.total_files > 0:
                        progress = min(self.processed_files / self.total_files, 1.0)
                        self.progress_bar.set(progress)

            def flush(self):
                pass

        # 保存原始标准输出
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # 重定向输出
            redirector = TextRedirector(self.output_text, self.progress_bar)
            sys.stdout = redirector
            sys.stderr = redirector

            # 执行文件处理
            process_files(
                source_dir,
                dest_dir,
                extensions,
                include_keywords,
                exclude_keywords,
                is_move,
                keep_structure,
                log_enabled
            )

            # 完成进度条
            self.progress_bar.set(1.0)
            messagebox.showinfo("完成", f"文件{op_type}操作已完成")
            self.status_var.set("操作完成")

        except Exception as e:
            error_msg = f"操作过程中发生错误: {str(e)}"
            self.output_text.insert("end", f"\n{error_msg}\n")
            messagebox.showerror("错误", error_msg)
            self.status_var.set("发生错误")

        finally:
            # 恢复原始标准输出
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def quit_app(self):
        """退出应用程序"""
        if messagebox.askyesno("确认退出", "确定要退出文件复制工具吗？"):
            self.root.quit()
            self.root.destroy()

    def run(self):
        """启动应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    app = ModernFileCopierUI()
    app.run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from file_copier import process_files, check_dependencies, analyze_file_types
from modern_icons import get_icon

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
        self.root.grid_rowconfigure(6, weight=1)  # 输出区域行可扩展
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
        # 标题
        title_label = ctk.CTkLabel(
            self.root,
            text="文件复制工具",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # 源目录框架
        source_frame = ctk.CTkFrame(self.root)
        source_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        source_frame.grid_columnconfigure(1, weight=1)

        source_label = ctk.CTkLabel(source_frame, text="源目录:", font=ctk.CTkFont(size=14, weight="bold"), image=get_icon("folder", size=(20, 20)), compound="left")
        source_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.source_entry = ctk.CTkEntry(source_frame, placeholder_text="选择要处理的源目录...")
        self.source_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        browse_btn = ctk.CTkButton(source_frame, text="浏览", command=self.browse_source, width=80, image=get_icon("folder", size=(16, 16)), compound="left")
        browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15)

        scan_btn = ctk.CTkButton(source_frame, text="扫描", command=self.scan_source, width=80, image=get_icon("search", size=(16, 16)), compound="left")
        scan_btn.grid(row=0, column=3, padx=(0, 15), pady=15)

        # 目标目录框架
        dest_frame = ctk.CTkFrame(self.root)
        dest_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        dest_frame.grid_columnconfigure(1, weight=1)

        dest_label = ctk.CTkLabel(dest_frame, text="目标目录:", font=ctk.CTkFont(size=14, weight="bold"), image=get_icon("folder", size=(20, 20)), compound="left")
        dest_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.dest_entry = ctk.CTkEntry(dest_frame, placeholder_text="选择文件复制/移动的目标目录...")
        self.dest_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        dest_browse_btn = ctk.CTkButton(dest_frame, text="浏览", command=self.browse_dest, width=80, image=get_icon("folder", size=(16, 16)), compound="left")
        dest_browse_btn.grid(row=0, column=2, padx=(0, 15), pady=15)

        # 操作选项框架
        options_frame = ctk.CTkFrame(self.root)
        options_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure((1, 2, 3, 4), weight=1)

        # 操作模式
        ctk.CTkLabel(options_frame, text="操作模式:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.operation_var = ctk.StringVar(value="复制")
        operation_combo = ctk.CTkComboBox(options_frame, values=["复制", "剪切"], variable=self.operation_var, state="readonly", width=120)
        operation_combo.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # 选项复选框
        self.keep_structure_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="保留原有文件夹结构", variable=self.keep_structure_var).grid(row=0, column=2, padx=15, pady=15, sticky="w")

        self.log_enabled_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="记录日志", variable=self.log_enabled_var).grid(row=0, column=3, padx=15, pady=15, sticky="w")

        # 颜色主题选择功能已移除

        # 外观模式切换
        ctk.CTkLabel(options_frame, text="外观模式:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=4, padx=15, pady=5, sticky="e")
        self.appearance_var = ctk.StringVar(value="系统")
        appearance_combo = ctk.CTkComboBox(
            options_frame,
            values=["系统", "浅色", "深色"],
            variable=self.appearance_var,
            state="readonly",
            width=100,
            command=self.change_appearance
        )
        appearance_combo.grid(row=0, column=5, padx=(5, 15), pady=5, sticky="e")

        # 文件筛选框架
        filter_frame = ctk.CTkFrame(self.root)
        filter_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure((0, 1), weight=1)

        # 文件后缀
        ctk.CTkLabel(filter_frame, text="文件后缀(空格分隔):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.extensions_entry = ctk.CTkEntry(filter_frame, placeholder_text="例如: pdf txt xlsx")
        self.extensions_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # 关键词筛选
        ctk.CTkLabel(filter_frame, text="包含关键词(空格分隔):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")
        self.include_entry = ctk.CTkEntry(filter_frame, placeholder_text="文件名包含的关键词")
        self.include_entry.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(filter_frame, text="排除关键词(空格分隔):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, padx=15, pady=(15, 5), sticky="w")
        self.exclude_entry = ctk.CTkEntry(filter_frame, placeholder_text="要排除的文件关键词")
        self.exclude_entry.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)  # 初始进度为0

        # 输出显示区域
        output_frame = ctk.CTkFrame(self.root)
        output_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(output_frame, text="输出信息:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.output_text = ctk.CTkTextbox(output_frame, font=ctk.CTkFont(family="Consolas", size=11))
        self.output_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # 按钮框架
        button_frame = ctk.CTkFrame(self.root)
        button_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
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
        status_bar.grid(row=8, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

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
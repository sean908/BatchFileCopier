#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from file_copier import process_files, check_dependencies

class FileCopierUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件复制工具")
        self.root.geometry("600x300")
        self.root.resizable(True, True)
        
        # 检查依赖
        check_dependencies()
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源目录选择
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="源目录:").pack(side=tk.LEFT, padx=5)
        self.source_entry = ttk.Entry(source_frame)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(source_frame, text="浏览...", command=self.browse_source).pack(side=tk.LEFT, padx=5)
        
        # 目标目录选择
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="目标目录:").pack(side=tk.LEFT, padx=5)
        self.dest_entry = ttk.Entry(dest_frame)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dest_frame, text="浏览...", command=self.browse_dest).pack(side=tk.LEFT, padx=5)
        
        # 操作选项
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="操作模式:").pack(side=tk.LEFT, padx=5)
        self.operation_var = tk.StringVar(value="复制")
        operation_combo = ttk.Combobox(options_frame, textvariable=self.operation_var, values=["复制", "剪切"], state="readonly", width=8)
        operation_combo.pack(side=tk.LEFT, padx=5)
        
        self.keep_structure_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="保留原有文件夹结构", variable=self.keep_structure_var).pack(side=tk.LEFT, padx=10)
        
        # 文件后缀
        ext_frame = ttk.Frame(main_frame)
        ext_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ext_frame, text="文件后缀(空格分隔):").pack(side=tk.LEFT, padx=5)
        self.extensions_entry = ttk.Entry(ext_frame)
        self.extensions_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 包含/排除关键词
        keywords_frame = ttk.Frame(main_frame)
        keywords_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(keywords_frame, text="包含关键词(空格分隔):").pack(side=tk.LEFT, padx=5)
        self.include_entry = ttk.Entry(keywords_frame)
        self.include_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        exclude_frame = ttk.Frame(main_frame)
        exclude_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exclude_frame, text="排除关键词(空格分隔):").pack(side=tk.LEFT, padx=5)
        self.exclude_entry = ttk.Entry(exclude_frame)
        self.exclude_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 执行按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="执行", command=self.execute).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="退出", command=root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_source(self):
        """浏览选择源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, directory)
    
    def browse_dest(self):
        """浏览选择目标目录"""
        directory = filedialog.askdirectory(title="选择目标目录")
        if directory:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, directory)
    
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
        
        if not messagebox.askyesno("确认操作", confirm_msg):
            return
        
        # 更新状态
        self.status_var.set(f"正在{op_type}文件...")
        self.root.update()
        
        try:
            # 执行文件处理
            process_files(
                source_dir,
                dest_dir,
                extensions,
                include_keywords,
                exclude_keywords,
                is_move,
                keep_structure
            )
            messagebox.showinfo("完成", f"文件{op_type}操作已完成")
            self.status_var.set("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"操作过程中发生错误: {str(e)}")
            self.status_var.set("发生错误")

def main():
    root = tk.Tk()
    app = FileCopierUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
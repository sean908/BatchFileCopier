#!/usr/bin/env python3
import os
import shutil
import argparse
import datetime
import sys
from pathlib import Path
import logging
from tqdm import tqdm

def setup_logger(dest_dir):
    """设置日志记录器"""
    # 获取目标目录的名称（去掉路径中的斜杠）
    dest_dir_name = os.path.basename(os.path.normpath(dest_dir))
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{dest_dir_name}_{timestamp}_copy.log"
    log_path = os.path.join(dest_dir, log_filename)
    
    # 创建日志记录器
    logger = logging.getLogger('FileOperations')
    logger.setLevel(logging.INFO)
    
    # 如果已经有处理器，先移除它们
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建文件处理器
    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    return logger

def should_process_file(filename, include_keywords, exclude_keywords, extensions):
    """判断文件是否应该被处理"""
    name_without_ext = os.path.splitext(filename)[0]
    
    # 检查文件扩展名
    if extensions and not any(filename.endswith(ext) for ext in extensions):
        return False
    
    # 检查排除关键词
    if exclude_keywords and any(keyword in name_without_ext for keyword in exclude_keywords):
        return False
    
    # 检查包含关键词
    if include_keywords and not any(keyword in name_without_ext for keyword in include_keywords):
        return False
    
    return True

def get_all_files(source_dir):
    """获取所有文件的列表"""
    all_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

def process_files(source_dir, dest_dir, extensions, include_keywords, exclude_keywords, is_move=False, keep_structure=False):
    """处理文件（复制或移动）"""
    # 确保目标目录存在
    os.makedirs(dest_dir, exist_ok=True)
    
    # 设置日志记录器
    logger = setup_logger(dest_dir)
    
    # 获取所有文件
    all_files = get_all_files(source_dir)
    files_to_process = [f for f in all_files if should_process_file(
        os.path.basename(f), include_keywords, exclude_keywords, extensions)]
    
    if not files_to_process:
        print("没有找到匹配的文件")
        return
    
    # 创建进度条
    pbar = tqdm(total=len(files_to_process), desc='处理进度', unit='file')
    
    for file_path in files_to_process:
        try:
            if keep_structure:
                # 保持原有文件夹结构
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(dest_dir, rel_path)
                # 确保目标文件的父目录存在
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            else:
                # 所有文件直接放在目标文件夹下
                dest_path = os.path.join(dest_dir, os.path.basename(file_path))
            
            # 执行复制或移动操作
            operation = shutil.move if is_move else shutil.copy2
            operation(file_path, dest_path)
            
            # 记录日志
            op_type = "移动" if is_move else "复制"
            logger.info(f"{op_type}文件: {file_path} -> {dest_path}")
            
            # 更新进度条
            pbar.update(1)
            
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时发生错误: {str(e)}")
            print(f"\n处理文件 {file_path} 时发生错误: {str(e)}", file=sys.stderr)
    
    pbar.close()

def check_dependencies():
    """检查并提示安装所需依赖"""
    try:
        import tqdm
    except ImportError:
        response = input("检测到缺少必要依赖 tqdm，是否立即安装？(Y/n): ")
        if response.lower() != 'n':
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
                print("依赖安装成功！")
            except subprocess.CalledProcessError:
                print("依赖安装失败，请手动执行: pip install tqdm", file=sys.stderr)
                sys.exit(1)
        else:
            print("程序运行需要 tqdm 依赖，请手动安装后再运行。", file=sys.stderr)
            sys.exit(1)

def main():
    # 创建自定义用法说明
    usage = """%(prog)s 源目录 目标目录 [后缀名...] [选项]

位置参数:
  源目录            要处理的源目录路径
  目标目录          文件复制/移动的目标目录路径
  后缀名            要处理的文件后缀名列表（例如：txt pdf）

选项:
  -h, --help       显示此帮助信息
  -i INCLUDE, --include INCLUDE
                   文件名包含的关键字（不含扩展名）
  -e EXCLUDE, --exclude EXCLUDE
                   要排除的文件名关键字（不含扩展名）
  -x, --move       使用移动而不是复制
  -k, --keep       保留原有的文件夹结构（默认不保留）
  -g, --gui        启动图形用户界面"""
    
    parser = argparse.ArgumentParser(description='文件复制/剪切工具', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('source', nargs='?', help='源目录路径')
    parser.add_argument('destination', nargs='?', help='目标目录路径')
    parser.add_argument('extensions', nargs='*', help='要处理的文件后缀名列表')
    parser.add_argument('-i', '--include', nargs='+', help='文件名包含的关键字（不含扩展名）')
    parser.add_argument('-e', '--exclude', nargs='+', help='要排除的文件名关键字（不含扩展名）')
    parser.add_argument('-x', '--move', action='store_true', help='使用移动而不是复制')
    parser.add_argument('-k', '--keep', action='store_true', help='保留原有的文件夹结构（默认不保留）')
    parser.add_argument('-g', '--gui', action='store_true', help='启动图形用户界面')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查是否启动GUI
    if args.gui:
        try:
            import tkinter as tk
            from file_copier_ui import main as gui_main
            gui_main()
            return
        except ImportError:
            print("错误：无法导入tkinter模块，请确保已安装Python的tkinter支持。", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"启动GUI时发生错误: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    # 命令行模式
    # 检查必要参数
    if not args.source or not args.destination:
        parser.print_help()
        sys.exit(1)
    
    # 检查依赖
    check_dependencies()
    
    # 确保源目录存在
    if not os.path.exists(args.source):
        print(f"错误：源目录 '{args.source}' 不存在", file=sys.stderr)
        sys.exit(1)
    
    # 处理文件扩展名
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions]
    
    # 执行文件处理
    process_files(
        args.source,
        args.destination,
        extensions,
        args.include,
        args.exclude,
        args.move,
        args.keep
    )

if __name__ == '__main__':
    main()
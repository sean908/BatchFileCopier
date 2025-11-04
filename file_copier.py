#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import argparse
import datetime
from pathlib import Path
import logging
from typing import List, Optional

try:
    from tqdm import tqdm
    import tqdm as tqdm_lib
except Exception:  # tqdm 可能未安装，在 CLI 中由 check_dependencies 处理
    tqdm = None  # type: ignore
    tqdm_lib = None  # type: ignore

import unicodedata


def setup_logger(dest_dir: str) -> logging.Logger:
    """创建按目标目录与时间命名的日志文件记录器。"""
    os.makedirs(dest_dir, exist_ok=True)
    dest_dir_name = os.path.basename(os.path.normpath(dest_dir))
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{dest_dir_name}_{timestamp}_copy.log"
    log_path = os.path.join(dest_dir, log_filename)

    logger = logging.getLogger('FileOperations')
    logger.setLevel(logging.INFO)
    # 清理已有的 handler，避免重复日志
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def should_process_file(
    filename: str,
    include_keywords: Optional[List[str]],
    exclude_keywords: Optional[List[str]],
    extensions: Optional[List[str]],
) -> bool:
    """根据扩展名与包含/排除关键字判断是否处理文件。"""
    name_without_ext = os.path.splitext(filename)[0]

    if extensions and not any(filename.lower().endswith(ext.lower()) for ext in extensions):
        return False
    if exclude_keywords and any(keyword in name_without_ext for keyword in exclude_keywords):
        return False
    if include_keywords and not any(keyword in name_without_ext for keyword in include_keywords):
        return False
    return True


def get_all_files(source_dir: str) -> List[str]:
    """递归获取目录下所有文件路径列表。"""
    all_files: List[str] = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files


def process_files(
    source_dir: str,
    dest_dir: str,
    extensions: Optional[List[str]],
    include_keywords: Optional[List[str]],
    exclude_keywords: Optional[List[str]],
    is_move: bool = False,
    keep_structure: bool = False,
    log_enabled: bool = True,
) -> None:
    """根据条件复制/移动文件，支持保留目录结构与输出日志。"""
    os.makedirs(dest_dir, exist_ok=True)

    logger: Optional[logging.Logger] = setup_logger(dest_dir) if log_enabled else None

    all_files = get_all_files(source_dir)
    files_to_process = [
        f for f in all_files
        if should_process_file(os.path.basename(f), include_keywords, exclude_keywords, extensions)
    ]

    if not files_to_process:
        print("未找到匹配的文件")
        return

    # 处理进度条
    if tqdm is None:
        # 无 tqdm 时的兜底：简单循环
        total = len(files_to_process)
        processed = 0
        for file_path in files_to_process:
            try:
                if keep_structure:
                    rel_path = os.path.relpath(file_path, source_dir)
                    dest_path = os.path.join(dest_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                else:
                    dest_path = os.path.join(dest_dir, os.path.basename(file_path))

                operation = shutil.move if is_move else shutil.copy2
                operation(file_path, dest_path)

                op_type = "移动" if is_move else "复制"
                log_msg = f"{op_type}文件: {file_path} -> {dest_path}"
                print("\n" + log_msg)
                if logger:
                    logger.info(log_msg)
                processed += 1
                print(f"处理进度: {processed}/{total}")
            except Exception as e:
                error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
                print("\n" + error_msg, file=sys.stderr)
                if logger:
                    logger.error(error_msg)
        return

    # 使用 tqdm 展示进度
    pbar = tqdm(total=len(files_to_process), desc='处理进度', unit='file')
    for file_path in files_to_process:
        try:
            if keep_structure:
                rel_path = os.path.relpath(file_path, source_dir)
                dest_path = os.path.join(dest_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            else:
                dest_path = os.path.join(dest_dir, os.path.basename(file_path))

            operation = shutil.move if is_move else shutil.copy2
            operation(file_path, dest_path)

            # 输出日志（与进度条分行显示）
            op_type = "移动" if is_move else "复制"
            log_msg = f"{op_type}文件: {file_path} -> {dest_path}"
            try:
                tqdm_lib.write(log_msg)
            except Exception:
                print("\n" + log_msg)
            if logger:
                logger.info(log_msg)

            pbar.update(1)
        except Exception as e:
            error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
            try:
                tqdm_lib.write(error_msg)
            except Exception:
                print("\n" + error_msg, file=sys.stderr)
            if logger:
                logger.error(error_msg)
    pbar.close()


def check_dependencies() -> None:
    """检查并提示安装运行所需依赖。"""
    try:
        import tqdm  # noqa: F401
    except ImportError:
        response = input("检测到缺少依赖 tqdm，是否现在安装？(Y/n): ")
        if response.lower() != 'n':
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
                print("依赖安装成功")
            except subprocess.CalledProcessError:
                print("依赖安装失败，请手动执行: pip install tqdm", file=sys.stderr)
                sys.exit(1)
        else:
            print("该程序需要 tqdm，请先安装后再运行。", file=sys.stderr)
            sys.exit(1)


def analyze_file_types(directory: str, tabbed: bool = False) -> None:
    """统计目录中的文件类型及数量。

    当 tabbed=True 时，使用制表符分隔三列（类型、数量、百分比），
    便于在 GUI 文本控件中通过 tab stops 实现像素级对齐；
    否则采用等宽对齐（适合终端显示）。
    """
    if not os.path.exists(directory):
        print(f"源目录 '{directory}' 不存在", file=sys.stderr)
        return

    file_types: dict[str, int] = {}
    total_files = 0

    # 遍历目录
    for root, _, files in os.walk(directory):
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            if not ext:
                ext = "无扩展名"
            file_types[ext] = file_types.get(ext, 0) + 1

    print(f"\n目录 '{directory}' 的文件类型统计")
    print(f"文件总数: {total_files}")
    print("\n文件类型统计：")

    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)

    if tabbed:
        # 使用制表符分隔三列，交由 GUI 通过 tab stops 对齐
        sep = '-' * 64
        print(sep)
        print("文件类型\t数量\t百分比")
        print(sep)
        for ext, count in sorted_types:
            percentage = (count / total_files) * 100 if total_files else 0.0
            label = ext if ext else '无扩展名'
            print(f"{label}\t{count}\t{percentage:.2f}%")
        print(sep)
    else:
        # 终端等宽对齐（中日韩全角字符宽度按2处理）
        def _eaw(ch: str) -> int:
            t = unicodedata.east_asian_width(ch)
            return 2 if t in ('W', 'F') else 1

        def disp_width(s: str) -> int:
            return sum(_eaw(c) for c in s)

        def lpad(s: object, width: int) -> str:
            s = str(s)
            pad = width - disp_width(s)
            return ' ' * pad + s if pad > 0 else s

        def rpad(s: object, width: int) -> str:
            s = str(s)
            pad = width - disp_width(s)
            return s + ' ' * pad if pad > 0 else s

        col1, col2, col3 = 16, 10, 10
        sep = '-' * (col1 + col2 + col3 + 2)
        print(sep)
        print(rpad('文件类型', col1) + ' ' + lpad('数量', col2) + ' ' + lpad('百分比', col3))
        print(sep)
        for ext, count in sorted_types:
            percentage = (count / total_files) * 100 if total_files else 0.0
            label = ext if ext else '无扩展名'
            print(rpad(label, col1) + ' ' + lpad(count, col2) + ' ' + lpad(f"{percentage:.2f}%", col3))
        print(sep)


def main() -> None:
    usage = """%(prog)s 源目录 目标目录 [扩展名...] [选项]

位置参数:
  源目录            要处理的源目录路径
  目标目录          文件复制/移动的目标目录路径
  扩展名            需要处理的文件扩展名列表，例如: txt pdf

可选参数:
  -h, --help       显示帮助信息
  -i, --include    文件名包含的关键字（多个用空格分隔）
  -e, --exclude    文件名排除的关键字（多个用空格分隔）
  -x, --move       使用移动而非复制
  -k, --keep       保留原有的文件夹结构
  -g, --gui        启动图形界面（若可用）
  -l, --list       统计并显示指定目录的文件类型
"""

    parser = argparse.ArgumentParser(
        description='文件复制/移动工具', usage=usage, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('source', nargs='?', help='源目录路径')
    parser.add_argument('destination', nargs='?', help='目标目录路径')
    parser.add_argument('extensions', nargs='*', help='需要处理的文件扩展名列表')
    parser.add_argument('-i', '--include', nargs='+', help='包含关键字（空格分隔）')
    parser.add_argument('-e', '--exclude', nargs='+', help='排除关键字（空格分隔）')
    parser.add_argument('-x', '--move', action='store_true', help='使用移动而非复制')
    parser.add_argument('-k', '--keep', action='store_true', help='保留原有的文件夹结构')
    parser.add_argument('-g', '--gui', action='store_true', help='启动图形界面')
    parser.add_argument('-l', '--list', help='统计并显示指定目录的文件类型')

    args = parser.parse_args()

    # 文件类型统计模式
    if args.list:
        analyze_file_types(args.list)
        return

    # GUI 模式
    if args.gui:
        try:
            import tkinter  # noqa: F401
            from file_copier_ui import main as gui_main
            gui_main()
            return
        except Exception as e:
            print(f"启动 GUI 失败: {str(e)}", file=sys.stderr)
            sys.exit(1)

    # CLI 模式
    if not args.source or not args.destination:
        parser.print_help()
        sys.exit(1)

    check_dependencies()

    if not os.path.exists(args.source):
        print(f"源目录 '{args.source}' 不存在", file=sys.stderr)
        sys.exit(1)

    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions]

    process_files(
        args.source,
        args.destination,
        extensions,
        args.include,
        args.exclude,
        args.move,
        args.keep,
    )


if __name__ == '__main__':
    main()

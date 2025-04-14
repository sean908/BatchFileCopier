#!/usr/bin/env python3
import sys
from file_copier import check_dependencies

def main():
    # 检查依赖
    check_dependencies()
    
    try:
        import tkinter as tk
        from file_copier_ui import main as gui_main
        gui_main()
    except ImportError:
        print("错误：无法导入tkinter模块，请确保已安装Python的tkinter支持。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"启动GUI时发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
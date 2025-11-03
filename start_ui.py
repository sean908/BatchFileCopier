#!/usr/bin/env python3
import sys
from file_copier import check_dependencies

def main():
    # 检查依赖
    check_dependencies()

    try:
        # 尝试导入CustomTkinter
        try:
            import customtkinter
            print("正在启动现代化UI...")
            from modern_file_copier_ui import main as modern_main
            modern_main()
        except ImportError as import_error:
            print(f"导入现代化UI失败: {str(import_error)}", file=sys.stderr)
            print("回退到经典UI界面", file=sys.stderr)
            # 如果CustomTkinter不可用，回退到经典UI
            import tkinter as tk
            from file_copier_ui import main as classic_main
            classic_main()
        except Exception as e:
            print(f"启动现代化UI时发生错误: {str(e)}", file=sys.stderr)
            print("尝试回退到经典UI...", file=sys.stderr)
            try:
                import tkinter as tk
                from file_copier_ui import main as classic_main
                classic_main()
            except Exception as fallback_error:
                print(f"启动经典UI也失败: {str(fallback_error)}", file=sys.stderr)
                sys.exit(1)
    except ImportError:
        print("错误：无法导入必要的GUI模块，请确保已安装Python的tkinter支持和customtkinter库。", file=sys.stderr)
        print("尝试安装依赖: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"启动GUI时发生未知错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
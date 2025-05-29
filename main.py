import sys
import os
from PyQt5.QtWidgets import QApplication
from todo_app_qt import TodoAppQt

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后和开发环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 添加这行
    window = TodoAppQt()
    window.show()
    sys.exit(app.exec_())
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from todo_app_qt import TodoAppQt
from utils import is_already_running

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后和开发环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # 检查程序是否已经运行
    if is_already_running():
        QMessageBox.warning(None, "提示", "程序已经在运行中！")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = TodoAppQt()
    window.setWindowTitle("待办事项提醒")
    window.show()
    sys.exit(app.exec_())
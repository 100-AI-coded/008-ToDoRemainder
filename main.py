import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
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
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 设置应用程序图标
    icon_path = resource_path("ui/todo.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # 检查程序是否已经运行
    if is_already_running():
        msg_box = QMessageBox()
        msg_box.setWindowTitle("提示")
        msg_box.setText("程序已经在运行中！")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()  # 使用exec_()而不是show()，确保消息框显示
        sys.exit(1)
    
    window = TodoAppQt()
    window.setWindowTitle("待办事项提醒")
    window.setWindowIcon(app_icon)  # 设置窗口图标
    window.show()
    sys.exit(app.exec_())
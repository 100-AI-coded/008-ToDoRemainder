import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from ui.main_window_qt import MainWindowQt
from ui.tray_icon_qt import TrayIconQt
from database.db_manager import DatabaseManager
from utils import get_app_data_dir
import sys

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后和开发环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TodoAppQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("待办事项提醒 - Author: Big-Dollar")
        self.setGeometry(100, 100, 800, 600)

        # 设置窗口图标
        icon_path = resource_path("ui/todo.ico")
        self.setWindowIcon(QIcon(icon_path))

        # 数据目录
        data_dir = get_app_data_dir()
        self.db = DatabaseManager(os.path.join(data_dir, "todos.db"))

        # 主窗口
        self.main_window = MainWindowQt(self, self.db, None)  # 先创建主窗口
        self.setCentralWidget(self.main_window)
        
        # 托盘图标
        self.tray_icon = TrayIconQt(self)
        self.tray_icon.show()
        self.main_window.tray_icon = self.tray_icon  # 设置托盘图标
        self.tray_icon.set_show_window_callback(self.show_window)

        # 初始化时更新托盘图标数量
        self.update_tray_icon_count()

    def update_tray_icon_count(self):
        """更新托盘图标显示的待办数量"""
        todos = self.db.get_all_todos()
        count = len([todo for todo in todos if not todo['completed']])
        self.tray_icon.update_icon_with_count(count)

    def show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()  # 将窗口提升到最前
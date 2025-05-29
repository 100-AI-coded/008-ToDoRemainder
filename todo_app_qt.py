import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ui.main_window_qt import MainWindowQt
from ui.tray_icon_qt import TrayIconQt
from database.db_manager import DatabaseManager
from utils import get_app_data_dir

class TodoAppQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("待办事项提醒 - Author: Big-Dollar")
        self.setGeometry(100, 100, 800, 600)

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
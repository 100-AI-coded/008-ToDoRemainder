from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication, QDialog
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from .todo_dialog import TodoDialog
import os
import sys
import winreg

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后和开发环境"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TrayIconQt(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(QIcon(resource_path("ui/todo.ico")), parent)
        self.parent = parent
        self.show_window_callback = None
        self.init_ui()
        self.activated.connect(self.on_tray_activated)

    def init_ui(self):
        """初始化托盘图标UI"""
        self.menu = QMenu()
        
        # 创建菜单项
        self.add_action = QAction("新增待办", self)
        self.show_action = QAction("显示主窗口", self)
        self.startup_action = QAction("", self)
        self.exit_action = QAction("退出", self)
        
        # 连接信号
        self.add_action.triggered.connect(self.on_add_todo)
        self.show_action.triggered.connect(self.on_show_window)
        self.startup_action.triggered.connect(self.toggle_startup)
        self.exit_action.triggered.connect(self.on_exit)
        
        # 添加菜单项
        self.menu.addAction(self.add_action)
        self.menu.addAction(self.show_action)
        self.menu.addAction(self.startup_action)
        self.menu.addAction(self.exit_action)
        
        self.setContextMenu(self.menu)
        self.update_startup_action_text()

    def update_startup_action_text(self):
        """根据当前状态更新菜单项文本"""
        if self.is_in_startup():
            self.startup_action.setText("移除开机启动")
        else:
            self.startup_action.setText("添加开机启动")

    def get_exe_path(self):
        if hasattr(sys, 'frozen'):
            return sys.executable
        else:
            return os.path.abspath(sys.argv[0])

    def is_in_startup(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, "ToDoRemainder")
            exe_path = self.get_exe_path()
            return exe_path in value
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)

    def add_to_startup(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        exe_path = self.get_exe_path()
        winreg.SetValueEx(key, "ToDoRemainder", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)

    def remove_from_startup(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "ToDoRemainder")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)

    def toggle_startup(self):
        if self.is_in_startup():
            self.remove_from_startup()
            self.showMessage("开机启动", "已移除开机启动项")
        else:
            self.add_to_startup()
            self.showMessage("开机启动", "已添加到开机启动项")
        self.update_startup_action_text()

    def on_add_todo(self):
        """处理添加待办事项"""
        dialog = TodoDialog()
        if dialog.exec_() == QDialog.Accepted:
            title, desc, due = dialog.get_data()
            if title.strip():
                self.parent.db.add_todo(title, desc, due)
                if hasattr(self.parent.main_window, 'load_todos'):
                    self.parent.main_window.load_todos()
                self.showMessage("待办事项提醒", "已成功添加新待办事项")

    def on_tray_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.on_show_window()

    def update_icon_with_count(self, count):
        """更新托盘图标显示待办数量"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        
        # 绘制基础图标
        icon = QIcon(resource_path("ui/todo.ico"))
        icon_pix = icon.pixmap(64, 64)
        painter.drawPixmap(0, 0, icon_pix)
        
        # 如果有待办事项，显示数量
        if count > 0:
            painter.setPen(QColor("red"))
            painter.setFont(QFont("Arial", 28, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignBottom | Qt.AlignRight, str(count))
        
        painter.end()
        self.setIcon(QIcon(pixmap))

    def set_show_window_callback(self, callback):
        """设置显示窗口的回调函数"""
        self.show_window_callback = callback

    def on_show_window(self):
        """显示主窗口"""
        if self.show_window_callback:
            self.show_window_callback()

    def on_exit(self):
        """退出应用程序"""
        self.parent.close()
        QApplication.instance().quit()
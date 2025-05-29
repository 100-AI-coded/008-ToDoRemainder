from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDialog, QApplication,
    QFrame, QHeaderView, QSpinBox, QSystemTrayIcon
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QUrl
from PyQt5.QtGui import QColor, QKeySequence, QFont, QPalette, QIcon, QCursor
from PyQt5.QtWidgets import QShortcut
import datetime
import webbrowser
import os
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from ui.todo_dialog import TodoDialog
from config import Config

class MainWindowQt(QWidget):
    def __init__(self, parent, db, tray_icon):
        super().__init__(parent)
        self.db = db
        self.tray_icon = tray_icon
        self.show_completed = False
        self.config = Config()
        
        self.init_ui()
        self.load_todos()
        self.setup_shortcuts()
        self.setup_styles()
        self.setup_reminder_timer()

    def show_help(self):
        """显示帮助信息"""
        webbrowser.open("https://github.com/100-AI-coded/008-ToDoRemainder")

    def setup_reminder_timer(self):
        """设置提醒定时器"""
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_overdue_todos)
        # 每分钟检查一次
        self.reminder_timer.start(60000)  # 60000毫秒 = 1分钟

    def check_overdue_todos(self):
        """检查过期待办事项"""
        try:
            now = datetime.datetime.now()
            last_reminder = self.config.get_last_reminder_time()
            
            if last_reminder:
                last_reminder_time = datetime.datetime.strptime(last_reminder, "%Y-%m-%d %H:%M:%S")
                # 检查是否达到提醒间隔
                if (now - last_reminder_time).total_seconds() < self.config.get_reminder_interval() * 60:
                    return
            
            # 获取所有未完成的待办事项
            todos = self.db.get_all_todos(completed=False)
            overdue_todos = []
            
            for todo in todos:
                try:
                    due = datetime.datetime.strptime(todo["due_date"], "%Y-%m-%d %H:%M:%S")
                    if due < now:
                        overdue_todos.append(todo)
                except:
                    continue
            
            if overdue_todos:
                # 更新最后提醒时间
                self.config.set_last_reminder_time(now.strftime("%Y-%m-%d %H:%M:%S"))
                # 显示提醒
                if hasattr(self.tray_icon, "showMessage"):
                    self.tray_icon.showMessage(
                        "待办事项提醒",
                        f"您有 {len(overdue_todos)} 个待办事项已过期，请尽快处理！",
                        QSystemTrayIcon.Warning,
                        5000  # 显示5秒
                    )
        except Exception as e:
            print(f"提醒检查出错: {str(e)}")
            # 出错时不中断程序运行

    def setup_styles(self):
        """设置全局样式"""
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", "微软雅黑";
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2d6da3;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                min-width: 100px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 1px solid #4a90e2;
            }
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #f0f0f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel {
                font-size: 14px;
            }
            QSpinBox {
                font-size: 14px;
            }
        """)

    def center_window(self):
        """将窗口居中显示"""
        # 获取当前活动屏幕
        screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()
        
        # 获取屏幕几何信息
        screen_geometry = screen.geometry()
        
        # 获取窗口的期望大小
        size_hint = self.sizeHint()
        if not size_hint.isValid():
            size_hint = self.size()
        
        # 计算居中位置
        x = screen_geometry.x() + (screen_geometry.width() - size_hint.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - size_hint.height()) // 2
        
        # 确保窗口不会超出屏幕边界
        x = max(screen_geometry.x(), min(x, screen_geometry.right() - size_hint.width()))
        y = max(screen_geometry.y(), min(y, screen_geometry.bottom() - size_hint.height()))
        
        # 移动窗口
        self.move(x, y)

    def setup_shortcuts(self):
        """设置全局快捷键"""
        self.add_shortcut = QShortcut(QKeySequence("Alt+N"), self)
        self.add_shortcut.activated.connect(self.add_todo_dialog)
        self.add_shortcut.setContext(Qt.ApplicationShortcut)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 设置窗口最小大小
        self.setMinimumSize(800, 600)
        
        # 顶部操作区
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.StyledPanel)
        top_layout = QVBoxLayout(top_frame)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 第一行：搜索相关
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键字搜索...")
        self.search_edit.returnPressed.connect(self.search_todos)
        search_btn = QPushButton("搜索")
        search_btn.setFixedWidth(60)
        search_btn.clicked.connect(self.search_todos)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_edit, 1)
        search_row.addWidget(search_btn)
        search_row.addStretch()
        top_layout.addLayout(search_row)

        # 第二行：排序、提醒间隔、按钮、帮助
        op_row = QHBoxLayout()
        op_row.setSpacing(8)
        sort_label = QLabel("排序:")
        self.sort_combo = QComboBox()
        self.sort_map = {
            "到期时间": "due_date",
            "标题": "title",
            "创建时间": "created_at"
        }
        self.sort_combo.addItems(list(self.sort_map.keys()))
        self.sort_combo.currentIndexChanged.connect(self.load_todos)
        op_row.addWidget(sort_label)
        op_row.addWidget(self.sort_combo)

        reminder_label = QLabel("提醒间隔:")
        self.reminder_spin = QSpinBox()
        self.reminder_spin.setRange(1, 1440)
        self.reminder_spin.setValue(self.config.get_reminder_interval())
        self.reminder_spin.setSuffix(" 分钟")
        self.reminder_spin.editingFinished.connect(self.update_reminder_interval)
        op_row.addWidget(reminder_label)
        op_row.addWidget(self.reminder_spin)

        add_btn = QPushButton("添加新待办")
        add_btn.setIcon(QIcon("ui/add.png"))
        add_btn.clicked.connect(self.add_todo_dialog)
        op_row.addWidget(add_btn)

        self.toggle_btn = QPushButton("显示已完成事项")
        self.toggle_btn.clicked.connect(self.toggle_completed)
        op_row.addWidget(self.toggle_btn)

        op_row.addStretch()
        help_btn = QPushButton("?")
        help_btn.setFixedSize(16, 16)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Microsoft YaHei', '微软雅黑';
                padding: 0;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        op_row.addWidget(help_btn)

        top_layout.addLayout(op_row)
        layout.addWidget(top_frame)

        # 表格区域
        table_frame = QFrame()
        table_frame.setFrameStyle(QFrame.StyledPanel)
        table_layout = QVBoxLayout(table_frame)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["标题", "描述", "到期时间", "状态"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.edit_selected)
        
        # 设置表格列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 标题列自适应
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 描述列自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 时间列适应内容
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 状态列适应内容
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

        # 底部操作区
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setSpacing(10)
        
        edit_btn = QPushButton("编辑")
        edit_btn.setIcon(QIcon("ui/edit.png"))  # 如果有图标的话
        edit_btn.clicked.connect(self.edit_selected)
        bottom_layout.addWidget(edit_btn)
        
        del_btn = QPushButton("删除")
        del_btn.setIcon(QIcon("ui/delete.png"))  # 如果有图标的话
        del_btn.clicked.connect(self.delete_selected)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b52a37;
            }
        """)
        bottom_layout.addWidget(del_btn)
        
        self.mark_btn = QPushButton("标记完成")
        self.mark_btn.setIcon(QIcon("ui/complete.png"))  # 如果有图标的话
        self.mark_btn.clicked.connect(self.toggle_completed_status)
        self.mark_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        bottom_layout.addWidget(self.mark_btn)
        
        layout.addWidget(bottom_frame)
        
        # 调整窗口大小并居中显示
        self.resize(800, 600)
        self.center_window()

    def _get_todo_status(self, todo, now):
        """获取待办事项状态"""
        due = None
        try:
            due = datetime.datetime.strptime(todo["due_date"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        
        if todo["completed"]:
            return "已完成", due, QColor("#28a745")  # 绿色
        elif due and due < now:
            return "已超期", due, QColor("#dc3545")  # 红色
        else:
            return "未完成", due, QColor("#ffc107")  # 黄色

    def _update_table_row(self, row, todo):
        """更新表格行"""
        now = datetime.datetime.now()
        status, due, status_color = self._get_todo_status(todo, now)
        
        # 设置单元格内容
        title_item = QTableWidgetItem(todo["title"])
        desc_item = QTableWidgetItem(todo["description"])
        due_item = QTableWidgetItem(todo["due_date"])
        status_item = QTableWidgetItem(status)
        
        # 设置状态颜色
        status_item.setForeground(status_color)
        
        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # 设置字体大小为12pt
        title_item.setFont(font)
        
        # 设置其他单元格字体
        normal_font = QFont()
        normal_font.setPointSize(12)  # 设置字体大小为12pt
        desc_item.setFont(normal_font)
        due_item.setFont(normal_font)
        status_item.setFont(normal_font)
        
        # 添加到表格
        self.table.setItem(row, 0, title_item)
        self.table.setItem(row, 1, desc_item)
        self.table.setItem(row, 2, due_item)
        self.table.setItem(row, 3, status_item)
        
        # 设置行颜色
        if (status == "未完成" and due and 0 < (due - now).total_seconds() < 86400) or status == "已超期":
            light_red = QColor(255, 200, 200)
            for col in range(4):
                self.table.item(row, col).setBackground(light_red)

    def _display_todos(self, todos):
        """显示待办事项列表"""
        self.table.setRowCount(0)
        for todo in todos:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._update_table_row(row, todo)
        
        # 更新托盘图标
        if hasattr(self.tray_icon, "update_icon_with_count"):
            count = sum(1 for todo in todos if not todo["completed"])
            self.tray_icon.update_icon_with_count(count)

    def toggle_completed(self):
        """切换显示已完成/未完成事项"""
        self.show_completed = not self.show_completed
        self.toggle_btn.setText("显示未完成事项" if self.show_completed else "显示已完成事项")
        self.load_todos()

    def load_todos(self):
        """加载所有待办事项"""
        sort_key = self.sort_map[self.sort_combo.currentText()]
        todos = self.db.get_all_todos(completed=self.show_completed, order_by=sort_key)
        self._display_todos(todos)
        
        # 更新标记按钮文本
        if self.show_completed:
            self.mark_btn.setText("取消完成")
        else:
            self.mark_btn.setText("标记完成")

    def search_todos(self):
        """搜索待办事项"""
        keyword = self.search_edit.text()
        todos = self.db.search_todos(keyword)
        sort_key = self.sort_map[self.sort_combo.currentText()]
        todos.sort(key=lambda x: x.get(sort_key, ""))
        
        if not self.show_completed:
            todos = [todo for todo in todos if not todo["completed"]]
        
        self._display_todos(todos)

    def add_todo_dialog(self):
        """添加新待办事项"""
        dialog = TodoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, desc, due = dialog.get_data()
            if not title.strip():
                QMessageBox.warning(self, "提示", "标题不能为空")
                return
            self.db.add_todo(title, desc, due)
            self.load_todos()

    def _get_selected_todo(self):
        """获取选中的待办事项"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择要操作的事项")
            return None
            
        row = selected_rows[0].row()
        title = self.table.item(row, 0).text()
        desc = self.table.item(row, 1).text()
        due = self.table.item(row, 2).text()
        
        todo = self.db.find_todo(title, desc, due)
        if not todo:
            QMessageBox.warning(self, "提示", "未找到该事项")
            return None
            
        return todo

    def edit_selected(self):
        """编辑选中的待办事项"""
        todo = self._get_selected_todo()
        if not todo:
            return
            
        dialog = TodoDialog(self, todo["title"], todo["description"], todo["due_date"])
        if dialog.exec_() == QDialog.Accepted:
            new_title, new_desc, new_due = dialog.get_data()
            if not new_title.strip():
                QMessageBox.warning(self, "提示", "标题不能为空")
                return
            self.db.update_todo(todo["id"], new_title, new_desc, new_due)
            self.load_todos()

    def delete_selected(self):
        """删除选中的待办事项"""
        todo = self._get_selected_todo()
        if not todo:
            return
            
        reply = QMessageBox.question(
            self, "确认删除", 
            "确定要删除该待办事项吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_todo(todo["id"])
            self.load_todos()

    def toggle_completed_status(self):
        """切换待办事项的完成状态"""
        todo = self._get_selected_todo()
        if not todo:
            return
            
        if todo["completed"]:
            # 如果当前是已完成状态，则取消完成
            reply = QMessageBox.question(
                self, "确认取消完成", 
                "确定要将该事项标记为未完成吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db.mark_completed(todo["id"], False)
                self.load_todos()
        else:
            # 如果当前是未完成状态，则标记为完成
            reply = QMessageBox.question(
                self, "确认标记", 
                "确定要将该事项标记为已完成吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db.mark_completed(todo["id"], True)
                self.load_todos()

    def closeEvent(self, event):
        """重写关闭事件"""
        event.ignore()
        self.hide()
        if hasattr(self.tray_icon, "showMessage"):
            self.tray_icon.showMessage(
                "待办事项提醒", 
                "程序已最小化到托盘，可在托盘区恢复窗口。"
            )

    def update_reminder_interval(self):
        """更新提醒间隔"""
        minutes = self.reminder_spin.value()
        self.config.set_reminder_interval(minutes)
        QMessageBox.information(self, "设置已保存", f"提醒间隔已设置为 {minutes} 分钟")
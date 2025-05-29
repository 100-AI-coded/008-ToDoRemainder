from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QDateTimeEdit, QFrame
)
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import webbrowser

class TodoDialog(QDialog):
    def __init__(self, parent=None, title="", description="", due_date=None):
        super().__init__(parent)
        self.setWindowTitle("待办事项")
        self.setMinimumWidth(400)
        
        self.setup_styles()
        self.init_ui(title, description, due_date)
        
        # 添加帮助按钮
        self.help_button = QPushButton("?", self)
        self.help_button.setFixedSize(20, 20)
        self.help_button.clicked.connect(self.show_help)
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                font-family: "Microsoft YaHei", "微软雅黑";
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
        # 延迟设置帮助按钮位置
        QTimer.singleShot(200, lambda: self.help_button.move(self.width() - 30, 10))

    def show_help(self):
        """显示帮助信息"""
        webbrowser.open("https://github.com/100-AI-coded/008-ToDoRemainder")

    def resizeEvent(self, event):
        """重写调整大小事件，保持帮助按钮位置"""
        super().resizeEvent(event)
        if hasattr(self, 'help_button'):
            self.help_button.move(self.width() - 30, 10)

    def setup_styles(self):
        """设置对话框样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                color: #333;
                margin-top: 5px;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 1px solid #4a90e2;
                background-color: white;
            }
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton#okButton {
                background-color: #4a90e2;
                color: white;
            }
            QPushButton#okButton:hover {
                background-color: #357abd;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
                color: white;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)

    def init_ui(self, title, description, due_date):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题输入
        title_label = QLabel("标题:")
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("请输入待办事项标题")
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)
        
        # 描述输入
        desc_label = QLabel("描述:")
        self.desc_edit = QTextEdit(description)
        self.desc_edit.setPlaceholderText("请输入待办事项描述（可选）")
        self.desc_edit.setMinimumHeight(100)
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_edit)
        
        # 到期时间输入
        due_label = QLabel("到期时间:")
        self.due_edit = QDateTimeEdit()
        self.due_edit.setCalendarPopup(True)
        self.due_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        if due_date:
            self.due_edit.setDateTime(QDateTime.fromString(due_date, "yyyy-MM-dd HH:mm:ss"))
        else:
            self.due_edit.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(due_label)
        layout.addWidget(self.due_edit)
        
        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(10)
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("okButton")
        ok_btn.setIcon(QIcon("ui/ok.png"))  # 如果有图标的话
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setIcon(QIcon("ui/cancel.png"))  # 如果有图标的话
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(btn_frame)

    def get_data(self):
        """获取对话框数据"""
        return (
            self.title_edit.text(),
            self.desc_edit.toPlainText(),
            self.due_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        )
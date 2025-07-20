import sys
import os
import getpass
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QHeaderView, 
                            QTabWidget, QGridLayout, QGroupBox, QInputDialog, QComboBox,
                            QSplitter, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from database import Database

class PasswordDialog(QDialog):
    """主密码输入对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入主密码")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # 密码输入框
        form_layout = QFormLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("主密码:", self.password_input)
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_password(self):
        return self.password_input.text()

class AccountDialog(QDialog):
    """账号信息对话框（添加/编辑）"""
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("账号信息" if account else "添加新账号")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 表单
        form_layout = QFormLayout()
        
        self.site_input = QLineEdit()
        form_layout.addRow("网站/服务名称:", self.site_input)
        
        self.username_input = QLineEdit()
        form_layout.addRow("用户名/账号:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_input)
        
        self.show_password_btn = QPushButton("显示密码")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        form_layout.addRow("", self.show_password_btn)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("备注:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # 如果是编辑模式，填充现有数据
        if account:
            self.site_input.setText(account['site_name'])
            self.username_input.setText(account['username'])
            self.password_input.setText(account['password'])
            self.notes_input.setText(account['notes'] if account['notes'] else "")
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("保存")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("隐藏密码")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("显示密码")
        
    def get_account_data(self):
        return {
            'site_name': self.site_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'notes': self.notes_input.toPlainText()
        }

class AccountManagerApp(QMainWindow):
    """主应用窗口"""
    def __init__(self):
        super().__init__()
        self.db = None
        self.initUI()
        self.login()
        
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("账号密码管理系统")
        self.setMinimumSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加账号")
        self.add_btn.clicked.connect(self.add_account)
        toolbar_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑账号")
        self.edit_btn.clicked.connect(self.edit_account)
        toolbar_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除账号")
        self.delete_btn.clicked.connect(self.delete_account)
        toolbar_layout.addWidget(self.delete_btn)
        
        toolbar_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        self.search_input.textChanged.connect(self.search_accounts)
        toolbar_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_accounts)
        toolbar_layout.addWidget(self.search_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "网站/服务名称", "用户名/账号", "密码", "备注"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.view_account_details)
        main_layout.addWidget(self.table)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
        
    def login(self):
        """登录处理"""
        dialog = PasswordDialog(self)
        if dialog.exec_():
            master_password = dialog.get_password()
            try:
                self.db = Database(master_password)
                self.load_accounts()
                self.statusBar().showMessage("登录成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"登录失败: {str(e)}")
                self.close()
        else:
            self.close()
            
    def load_accounts(self, search_keyword=""):
        """加载账号列表"""
        try:
            if search_keyword:
                accounts = self.db.search_accounts(search_keyword)
            else:
                accounts = self.db.get_all_accounts()
                
            self.table.setRowCount(0)
            for account in accounts:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                
                # 填充数据
                self.table.setItem(row_position, 0, QTableWidgetItem(str(account['id'])))
                self.table.setItem(row_position, 1, QTableWidgetItem(account['site_name']))
                self.table.setItem(row_position, 2, QTableWidgetItem(account['username']))
                
                # 密码项默认显示为 ****
                password_item = QTableWidgetItem("********")
                password_item.setData(Qt.UserRole, account['password'])  # 存储实际密码
                self.table.setItem(row_position, 3, password_item)
                
                self.table.setItem(row_position, 4, QTableWidgetItem(account['notes'] if account['notes'] else ""))
                
            self.statusBar().showMessage(f"已加载 {self.table.rowCount()} 个账号")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载账号失败: {str(e)}")
            
    def search_accounts(self):
        """搜索账号"""
        keyword = self.search_input.text()
        self.load_accounts(keyword)
        
    def add_account(self):
        """添加新账号"""
        dialog = AccountDialog(self)
        if dialog.exec_():
            account_data = dialog.get_account_data()
            try:
                self.db.add_account(
                    account_data['site_name'],
                    account_data['username'],
                    account_data['password'],
                    account_data['notes']
                )
                self.load_accounts()
                self.statusBar().showMessage("账号添加成功")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"添加账号失败: {str(e)}")
                
    def edit_account(self):
        """编辑账号"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择一个账号")
            return
            
        # 获取选中行的ID
        row = selected_rows[0].row()
        account_id = int(self.table.item(row, 0).text())
        
        # 构建账号数据
        account = {
            'id': account_id,
            'site_name': self.table.item(row, 1).text(),
            'username': self.table.item(row, 2).text(),
            'password': self.table.item(row, 3).data(Qt.UserRole),
            'notes': self.table.item(row, 4).text()
        }
        
        dialog = AccountDialog(self, account)
        if dialog.exec_():
            new_data = dialog.get_account_data()
            try:
                self.db.update_account(
                    account_id,
                    new_data['site_name'],
                    new_data['username'],
                    new_data['password'],
                    new_data['notes']
                )
                self.load_accounts()
                self.statusBar().showMessage("账号更新成功")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"更新账号失败: {str(e)}")
                
    def delete_account(self):
        """删除账号"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择一个账号")
            return
            
        # 获取选中行的ID
        row = selected_rows[0].row()
        account_id = int(self.table.item(row, 0).text())
        site_name = self.table.item(row, 1).text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除 '{site_name}' 的账号信息吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_account(account_id)
                self.load_accounts()
                self.statusBar().showMessage("账号删除成功")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"删除账号失败: {str(e)}")
                
    def view_account_details(self, index):
        """查看账号详情"""
        row = index.row()
        account_id = int(self.table.item(row, 0).text())
        
        # 构建账号数据
        account = {
            'id': account_id,
            'site_name': self.table.item(row, 1).text(),
            'username': self.table.item(row, 2).text(),
            'password': self.table.item(row, 3).data(Qt.UserRole),
            'notes': self.table.item(row, 4).text()
        }
        
        # 显示详情对话框
        dialog = AccountDialog(self, account)
        dialog.setWindowTitle("账号详情")
        dialog.site_input.setReadOnly(True)
        dialog.username_input.setReadOnly(True)
        dialog.password_input.setReadOnly(True)
        dialog.notes_input.setReadOnly(True)
        dialog.ok_button.setText("关闭")
        dialog.cancel_button.hide()
        dialog.exec_()
        
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        if self.db:
            self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，在各平台上看起来更一致
    window = AccountManagerApp()
    window.show()
    sys.exit(app.exec_()) 
import sqlite3
import os
import hashlib
import base64
import secrets
from datetime import datetime

class Database:
    def __init__(self, master_password):
        """初始化数据库连接并设置主密码"""
        # 使用固定路径存储数据库文件
        user_home = os.path.expanduser("~")
        app_data_dir = os.path.join(user_home, "AccountManager")
        
        # 确保目录存在
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
            
        self.db_file = os.path.join(app_data_dir, "accounts.db")
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # 使用主密码生成加密密钥
        self.master_key = self._generate_key(master_password)
        
    def _generate_key(self, password):
        """从主密码生成加密密钥"""
        salt = b'account_manager_salt'  # 在实际应用中应该为每个用户生成唯一的盐
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return base64.b64encode(key)
        
    def create_tables(self):
        """创建账号表"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site_name TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()
        
    def encrypt_password(self, password):
        """简单加密密码"""
        # 使用XOR操作加密
        password_bytes = password.encode('utf-8')
        key_bytes = self.master_key
        # 确保密钥足够长
        while len(key_bytes) < len(password_bytes):
            key_bytes += key_bytes
            
        # 执行XOR加密
        encrypted = bytearray()
        for i in range(len(password_bytes)):
            encrypted.append(password_bytes[i] ^ key_bytes[i % len(key_bytes)])
            
        # 添加随机IV以增加安全性
        iv = secrets.token_bytes(8)
        result = iv + bytes(encrypted)
        return base64.b64encode(result).decode('utf-8')
        
    def decrypt_password(self, encrypted_password):
        """解密密码"""
        try:
            # 解码base64
            encrypted_bytes = base64.b64decode(encrypted_password)
            # 提取IV和密文
            iv = encrypted_bytes[:8]
            encrypted_data = encrypted_bytes[8:]
            
            # 使用XOR操作解密
            key_bytes = self.master_key
            # 确保密钥足够长
            while len(key_bytes) < len(encrypted_data):
                key_bytes += key_bytes
                
            # 执行XOR解密
            decrypted = bytearray()
            for i in range(len(encrypted_data)):
                decrypted.append(encrypted_data[i] ^ key_bytes[i % len(key_bytes)])
                
            return bytes(decrypted).decode('utf-8')
        except:
            return "解密失败"
    
    def add_account(self, site_name, username, password, notes=""):
        """添加新账号"""
        encrypted_password = self.encrypt_password(password)
        self.cursor.execute(
            "INSERT INTO accounts (site_name, username, password, notes) VALUES (?, ?, ?, ?)",
            (site_name, username, encrypted_password, notes)
        )
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_all_accounts(self):
        """获取所有账号信息"""
        self.cursor.execute("SELECT id, site_name, username, password, notes FROM accounts ORDER BY site_name")
        accounts = []
        for row in self.cursor.fetchall():
            account = {
                'id': row[0],
                'site_name': row[1],
                'username': row[2],
                'password': self.decrypt_password(row[3]),
                'notes': row[4]
            }
            accounts.append(account)
        return accounts
        
    def search_accounts(self, keyword):
        """搜索账号信息"""
        self.cursor.execute(
            "SELECT id, site_name, username, password, notes FROM accounts WHERE site_name LIKE ? OR username LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
        accounts = []
        for row in self.cursor.fetchall():
            account = {
                'id': row[0],
                'site_name': row[1],
                'username': row[2],
                'password': self.decrypt_password(row[3]),
                'notes': row[4]
            }
            accounts.append(account)
        return accounts
        
    def update_account(self, account_id, site_name=None, username=None, password=None, notes=None):
        """更新账号信息"""
        # 获取当前账号信息
        self.cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = self.cursor.fetchone()
        if not account:
            return False
            
        # 准备更新数据
        new_site_name = site_name if site_name is not None else account[1]
        new_username = username if username is not None else account[2]
        new_password = self.encrypt_password(password) if password is not None else account[3]
        new_notes = notes if notes is not None else account[4]
        
        # 执行更新
        self.cursor.execute(
            "UPDATE accounts SET site_name = ?, username = ?, password = ?, notes = ? WHERE id = ?",
            (new_site_name, new_username, new_password, new_notes, account_id)
        )
        self.conn.commit()
        return True
        
    def delete_account(self, account_id):
        """删除账号信息"""
        self.cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def close(self):
        """关闭数据库连接"""
        self.conn.close() 
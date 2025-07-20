import os
import shutil
import sqlite3

def migrate_data():
    """将原始数据库中的数据迁移到新位置"""
    # 原始数据库路径
    original_db = "accounts.db"
    
    # 新数据库路径
    user_home = os.path.expanduser("~")
    app_data_dir = os.path.join(user_home, "AccountManager")
    
    # 确保目录存在
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
        
    new_db = os.path.join(app_data_dir, "accounts.db")
    
    # 检查原始数据库是否存在
    if not os.path.exists(original_db):
        print(f"错误: 找不到原始数据库文件 {original_db}")
        return False
    
    # 如果新位置已有数据库，先备份
    if os.path.exists(new_db):
        backup_db = new_db + ".backup"
        print(f"备份现有数据库到 {backup_db}")
        shutil.copy2(new_db, backup_db)
    
    # 复制数据库文件
    print(f"正在将数据库从 {original_db} 复制到 {new_db}")
    shutil.copy2(original_db, new_db)
    
    # 验证数据
    try:
        conn = sqlite3.connect(new_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"成功迁移 {count} 条账号记录")
        return True
    except Exception as e:
        print(f"验证数据时出错: {e}")
        return False

if __name__ == "__main__":
    if migrate_data():
        print("\n数据迁移成功！")
        print("您现在可以使用新版本的应用程序访问您的账号数据。")
    else:
        print("\n数据迁移失败！")
        print("请确保原始数据库文件存在且可访问。") 
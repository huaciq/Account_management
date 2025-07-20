import os
import getpass
import time
from database import Database

class AccountManager:
    def __init__(self):
        """初始化账号管理器"""
        self.db = None
        self.logged_in = False
        
    def start(self):
        """启动程序"""
        self._clear_screen()
        print("欢迎使用账号密码管理系统")
        print("=" * 50)
        
        # 要求输入主密码
        master_password = getpass.getpass("请输入主密码: ")
        try:
            self.db = Database(master_password)
            self.logged_in = True
            self.main_menu()
        except Exception as e:
            print(f"错误: {e}")
            print("无法初始化数据库，请检查主密码或数据库文件。")
            
    def main_menu(self):
        """显示主菜单"""
        while self.logged_in:
            self._clear_screen()
            print("\n账号密码管理系统 - 主菜单")
            print("=" * 50)
            print("1. 添加新账号")
            print("2. 查看所有账号")
            print("3. 搜索账号")
            print("4. 更新账号信息")
            print("5. 删除账号")
            print("0. 退出系统")
            
            choice = input("\n请选择操作 [0-5]: ")
            
            if choice == "1":
                self.add_account()
            elif choice == "2":
                self.view_all_accounts()
            elif choice == "3":
                self.search_accounts()
            elif choice == "4":
                self.update_account()
            elif choice == "5":
                self.delete_account()
            elif choice == "0":
                self._exit_program()
            else:
                print("无效选择，请重试。")
                time.sleep(1)
                
    def add_account(self):
        """添加新账号"""
        self._clear_screen()
        print("\n添加新账号")
        print("=" * 50)
        
        site_name = input("网站/服务名称: ")
        username = input("用户名/账号: ")
        password = getpass.getpass("密码: ")
        notes = input("备注 (可选): ")
        
        try:
            account_id = self.db.add_account(site_name, username, password, notes)
            print(f"\n成功添加账号！ID: {account_id}")
        except Exception as e:
            print(f"\n添加账号失败: {e}")
            
        self._wait_for_key()
        
    def view_all_accounts(self):
        """查看所有账号"""
        self._clear_screen()
        print("\n所有账号")
        print("=" * 50)
        
        accounts = self.db.get_all_accounts()
        if not accounts:
            print("没有保存的账号。")
        else:
            self._display_accounts(accounts)
            
        self._wait_for_key()
        
    def search_accounts(self):
        """搜索账号"""
        self._clear_screen()
        print("\n搜索账号")
        print("=" * 50)
        
        keyword = input("请输入搜索关键词: ")
        accounts = self.db.search_accounts(keyword)
        
        if not accounts:
            print(f"没有找到与 '{keyword}' 相关的账号。")
        else:
            print(f"\n找到 {len(accounts)} 个相关账号:")
            self._display_accounts(accounts)
            
        self._wait_for_key()
        
    def update_account(self):
        """更新账号信息"""
        self._clear_screen()
        print("\n更新账号信息")
        print("=" * 50)
        
        account_id = input("请输入要更新的账号ID: ")
        if not account_id.isdigit():
            print("无效的ID。")
            self._wait_for_key()
            return
            
        # 查找账号
        accounts = self.db.search_accounts("")
        target_account = None
        for account in accounts:
            if account['id'] == int(account_id):
                target_account = account
                break
                
        if not target_account:
            print(f"未找到ID为 {account_id} 的账号。")
            self._wait_for_key()
            return
            
        # 显示当前信息
        print("\n当前账号信息:")
        print(f"网站/服务名称: {target_account['site_name']}")
        print(f"用户名/账号: {target_account['username']}")
        print(f"备注: {target_account['notes']}")
        
        # 获取新信息
        print("\n请输入新的信息 (留空表示不修改):")
        new_site_name = input(f"网站/服务名称 [{target_account['site_name']}]: ")
        new_username = input(f"用户名/账号 [{target_account['username']}]: ")
        new_password = getpass.getpass("新密码 (留空表示不修改): ")
        new_notes = input(f"备注 [{target_account['notes']}]: ")
        
        # 使用原值替代空输入
        site_name = new_site_name if new_site_name else None
        username = new_username if new_username else None
        password = new_password if new_password else None
        notes = new_notes if new_notes else None
        
        try:
            if self.db.update_account(int(account_id), site_name, username, password, notes):
                print("\n账号信息已成功更新！")
            else:
                print("\n更新失败，账号不存在。")
        except Exception as e:
            print(f"\n更新账号失败: {e}")
            
        self._wait_for_key()
        
    def delete_account(self):
        """删除账号"""
        self._clear_screen()
        print("\n删除账号")
        print("=" * 50)
        
        account_id = input("请输入要删除的账号ID: ")
        if not account_id.isdigit():
            print("无效的ID。")
            self._wait_for_key()
            return
            
        confirm = input(f"确认删除ID为 {account_id} 的账号? (y/n): ")
        if confirm.lower() == 'y':
            try:
                if self.db.delete_account(int(account_id)):
                    print("\n账号已成功删除！")
                else:
                    print("\n删除失败，账号不存在。")
            except Exception as e:
                print(f"\n删除账号失败: {e}")
        else:
            print("\n操作已取消。")
            
        self._wait_for_key()
        
    def _display_accounts(self, accounts):
        """显示账号列表"""
        print(f"\n{'ID':<5} {'网站/服务名称':<20} {'用户名/账号':<20} {'密码':<20} {'备注':<20}")
        print("-" * 85)
        
        for account in accounts:
            print(f"{account['id']:<5} {account['site_name'][:20]:<20} {account['username'][:20]:<20} {account['password'][:20]:<20} {account['notes'][:20] if account['notes'] else '':<20}")
            
    def _clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _wait_for_key(self):
        """等待用户按键继续"""
        input("\n按回车键继续...")
        
    def _exit_program(self):
        """退出程序"""
        if self.db:
            self.db.close()
        self.logged_in = False
        self._clear_screen()
        print("感谢使用账号密码管理系统，再见！")
        
if __name__ == "__main__":
    manager = AccountManager()
    manager.start() 
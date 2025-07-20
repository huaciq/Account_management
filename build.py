import os
import subprocess
import sys
import shutil

def build_exe():
    """打包应用程序为exe文件"""
    print("开始打包应用程序...")
    
    # 确保输出目录存在
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # 使用PyInstaller打包
    cmd = [
        'pyinstaller',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name', 'AccountManager',
        '--add-data', 'README.md;.',
        '--add-data', '安装和使用说明.md;.',
        'gui_app.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("打包完成！")
        print(f"可执行文件位置: {os.path.abspath('dist/AccountManager.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe() 
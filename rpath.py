import os
import sys

def rpath(rel: str) -> str:
    #调用pyinstaller
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS  # sys._MEIPASS返回调用pyinstaller时创建临时目录的路径
    else:
        base = os.path.abspath('.') # '.'代表当前目录
    return os.path.join(base, rel)
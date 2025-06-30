import os
import webbrowser
import subprocess
import time
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # مسیر موقت PyInstaller
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))  # فولدر فعلی فایل اجرایی
    return os.path.join(base_path, relative_path)

# تغییر دایرکتوری به فولدر پروژه (جایی که manage.py هست)
os.chdir(resource_path("."))

# اجرای سرور
server = subprocess.Popen(["python", "manage.py", "runserver"])

# صبر کن تا سرور بالا بیاد
time.sleep(2)

# باز کردن مرورگر
webbrowser.open("http://127.0.0.1:8000")

# منتظر بمون تا کاربر سرور رو ببنده
server.wait()


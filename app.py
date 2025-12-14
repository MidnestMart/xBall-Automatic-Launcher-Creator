import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import shutil
import subprocess
import threading
from PIL import Image

# === НАСТРОЙКИ ДИЗАЙНА ===
ctk.set_appearance_mode("Light")  # Светлая тема (Белый фон)
ctk.set_default_color_theme("blue")  # Синяя тема

class XBallLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # === НАСТРОЙКИ ОКНА ===
        self.title("xBall Launcher Creator")
        
        # Размеры окна
        w_width, w_height = 850, 600
        
        # Центрирование окна на экране
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - w_width) // 2
        y = (screen_height - w_height) // 2
        
        self.geometry(f"{w_width}x{w_height}+{x}+{y}")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff") # Чисто белый фон

        # === ЛЕВАЯ ЧАСТЬ (ФОРМА) ===
        self.left_frame = ctk.CTkFrame(self, width=450, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=40, pady=30)

        # Логотип и Заголовок
        self.label_logo = ctk.CTkLabel(self.left_frame, text="xBall Creator", font=("Segoe UI", 12, "bold"), text_color="#1f6aa5")
        self.label_logo.pack(anchor="w", pady=(0, 5))

        self.label_title = ctk.CTkLabel(self.left_frame, text="Create your App.", font=("Segoe UI", 32, "bold"), text_color="#333333")
        self.label_title.pack(anchor="w", pady=(0, 0))

        self.label_sub = ctk.CTkLabel(self.left_frame, text="Web to Executable converter.", font=("Segoe UI", 14), text_color="#777777")
        self.label_sub.pack(anchor="w", pady=(0, 30))

        # 1. Поле: Название
        self.name_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Application Name", height=50, 
                                       border_color="#1f6aa5", fg_color="#f2f2f2", text_color="#000")
        self.name_entry.pack(fill="x", pady=(0, 15))

        # 2. Поле: URL
        self.url_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Website URL (https://...)", height=50,
                                      fg_color="#f2f2f2", text_color="#000")
        self.url_entry.pack(fill="x", pady=(0, 15))

        # 3. Поле: Иконка
        self.icon_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.icon_frame.pack(fill="x", pady=(0, 15))
        
        self.icon_entry = ctk.CTkEntry(self.icon_frame, placeholder_text="Icon path (.ico)", height=50,
                                       fg_color="#f2f2f2", text_color="#000")
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.icon_frame, text="...", width=50, height=50, 
                                        fg_color="#e0e0e0", text_color="#000", hover_color="#d0d0d0", 
                                        command=self.browse_icon)
        self.btn_browse.pack(side="right")

        # 4. Переключатель: Flash Player
        self.flash_switch = ctk.CTkSwitch(self.left_frame, text="Enable Flash Player (Ruffle)", 
                                          progress_color="#1f6aa5", text_color="#333")
        self.flash_switch.pack(anchor="w", pady=(10, 30))

        # Кнопка создания (Синяя)
        self.create_btn = ctk.CTkButton(self.left_frame, text="BUILD LAUNCHER", height=55, 
                                        font=("Segoe UI", 15, "bold"), fg_color="#1f6aa5", hover_color="#144870",
                                        command=self.start_build_thread)
        self.create_btn.pack(fill="x", pady=(0, 20))

        # Статус бар
        self.status_label = ctk.CTkLabel(self.left_frame, text="Ready to build", text_color="#888")
        self.status_label.pack(side="bottom", anchor="w")

        # === ПРАВАЯ ЧАСТЬ (КАРТИНКА) ===
        # Пытаемся загрузить картинку background.webp
        try:
            bg_image_data = Image.open("background.webp")
            # Подгоняем размер под правую часть окна (примерно 400x600)
            self.bg_image = ctk.CTkImage(light_image=bg_image_data, size=(400, 600))
            
            self.image_label = ctk.CTkLabel(self, text="", image=self.bg_image)
            self.image_label.pack(side="right", fill="both")
        except Exception:
            # Если картинки нет, делаем красивую синюю заглушку
            self.right_frame = ctk.CTkFrame(self, width=400, fg_color="#1f6aa5", corner_radius=0)
            self.right_frame.pack(side="right", fill="both")
            
            self.err_lbl = ctk.CTkLabel(self.right_frame, text="xBall\nVisuals", font=("Segoe UI", 40, "bold"), text_color="white")
            self.err_lbl.place(relx=0.5, rely=0.5, anchor="center")

    def browse_icon(self):
        filename = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if filename:
            self.icon_entry.delete(0, "end")
            self.icon_entry.insert(0, filename)

    def start_build_thread(self):
        threading.Thread(target=self.build_process).start()

    def build_process(self):
        app_name = self.name_entry.get()
        url = self.url_entry.get()
        icon_path = self.icon_entry.get()
        use_flash = self.flash_switch.get()

        if not app_name or not url:
            self.status_label.configure(text="Error: Fill all fields", text_color="red")
            return

        self.create_btn.configure(state="disabled", text="BUILDING...")
        self.status_label.configure(text="Generating core script...", text_color="#1f6aa5")

        try:
            # === 1. ГЕНЕРАЦИЯ КОДА ===
            ruffle_code = ""
            if use_flash:
                ruffle_code = """
def load_ruffle(window):
    js = \"\"\"
    var script = document.createElement('script');
    script.src = 'https://unpkg.com/@ruffle-rs/ruffle';
    document.head.appendChild(script);
    \"\"\"
    window.evaluate_js(js)
"""
            start_args = "webview.start(load_ruffle)" if use_flash else "webview.start()"

            script_content = f"""
import webview
import sys

{ruffle_code}

if __name__ == '__main__':
    # maximized=True — открывает на весь экран (с рамками)
    window = webview.create_window('{app_name}', '{url}', maximized=True)
    {start_args}
"""
            script_file = f"temp_build.py"
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script_content)

            # === 2. КОМПИЛЯЦИЯ ===
            self.status_label.configure(text="Compiling EXE (PyInstaller)...")
            
            cmd = ["pyinstaller", "--noconsole", "--onefile", f"--name={app_name}", "--clean", script_file]
            if icon_path and os.path.exists(icon_path):
                cmd.insert(4, f"--icon={icon_path}")

            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            process = subprocess.run(cmd, capture_output=True, text=True, creationflags=creation_flags)

            if process.returncode != 0:
                raise Exception(f"Compilation failed: {process.stderr}")

            # === 3. ПЕРЕМЕЩЕНИЕ В ПАПКУ ПОЛЬЗОВАТЕЛЯ ===
            self.status_label.configure(text="Installing to User Folder...")
            
            dist_folder = "dist"
            exe_name = f"{app_name}.exe"
            source_exe = os.path.join(dist_folder, exe_name)
            
            # Путь: C:\Users\NAME\xRCreate\Launcher\AppName
            user_home = os.path.expanduser("~")
            target_dir = os.path.join(user_home, "xRCreate", "Launcher", app_name)
            target_exe = os.path.join(target_dir, exe_name)

            if os.path.exists(source_exe):
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                if os.path.exists(target_exe):
                    os.remove(target_exe)

                shutil.move(source_exe, target_exe)
                
                # Чистка
                self.cleanup(app_name, script_file)

                self.status_label.configure(text="DONE!", text_color="#1f6aa5")
                messagebox.showinfo("xBall System", f"Success!\nApp installed at:\n{target_exe}")
            else:
                raise Exception("EXE file not found in dist.")

        except Exception as e:
            self.status_label.configure(text="Error occurred", text_color="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.create_btn.configure(state="normal", text="BUILD LAUNCHER")

    def cleanup(self, app_name, script_file):
        folders = ["build", "dist"]
        for folder in folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        
        files = [f"{app_name}.spec", script_file]
        for f in files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    app = XBallLauncher()
    app.mainloop()
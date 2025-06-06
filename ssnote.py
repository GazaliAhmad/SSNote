from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font, ttk
from tkinter import Menu
import json
import os
import ctypes
import time

CONFIG_FILE = "config.json"
LICENSE_TEXT = """MIT License

Copyright (c) 2025 Gazali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


THEMES = {
    "light": {
        "bg": "white",
        "fg": "black",
        "insertbackground": "black",
        "selectbackground": "#cce6ff",
        "button": "🌙"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "white",
        "insertbackground": "white",
        "selectbackground": "#444444",
        "button": "☀️"
    }
}

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("SSNote™")
        if os.path.exists("ssnote.ico"):
            self.root.iconbitmap("ssnote.ico")
        self.root.geometry("800x600")
        self.filename = None
        self.user_theme_override = None
        self.current_theme = "light"
        self.wrap_enabled = True
        self.auto_save_enabled = True
        self.auto_save_visible = False
        self.auto_save_locked = False
        self.last_saved_time = None

        self._init_fonts()
        self._load_config()
        self._create_widgets()
        self._create_menu()
        self._create_status_bar()
        self._bind_events()
        self._create_status_bar()
        self._update_status_bar()
        self._apply_theme()
        self._apply_wrap()
        self._init_file_from_config()
        self._refresh_recent_files_menu()

        self.root.after(120000, self._schedule_auto_save)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_fonts(self):
        self.available_fonts = list(font.families())
        self.current_font = tk.StringVar(value="Arial")
        self.current_size = tk.IntVar(value=12)

    def _load_config(self):
        self.config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config_data = json.load(f)
                    self.user_theme_override = self.config_data.get("theme")
                    self.wrap_enabled = self.config_data.get("wrap", True)
            except:
                self.config_data = {}

    def _detect_system_theme(self):
        try:
            key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            registry = ctypes.windll.advapi32.RegOpenKeyExW
            query = ctypes.windll.advapi32.RegQueryValueExW
            close = ctypes.windll.advapi32.RegCloseKey

            hkey = ctypes.c_void_p()
            if registry(0x80000001, key, 0, 0x20019, ctypes.byref(hkey)) == 0:
                value = ctypes.c_int()
                size = ctypes.c_uint(4)
                query(hkey, "AppsUseLightTheme", 0, None, ctypes.byref(value), ctypes.byref(size))
                close(hkey)
                return "light" if value.value == 1 else "dark"
        except:
            pass
        return "light"

    def _create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x')

        font_menu = ttk.Combobox(top_frame, textvariable=self.current_font, values=self.available_fonts, width=30)
        font_menu.pack(side='left', padx=5, pady=5)

        size_menu = ttk.Combobox(top_frame, textvariable=self.current_size, values=[str(i) for i in range(8, 33)], width=5)
        size_menu.pack(side='left', padx=5)

        self.wrap_button = tk.Button(top_frame, text="", command=self.toggle_wrap)
        self.wrap_button.pack(side='right', padx=5)

        self.theme_button = tk.Button(top_frame, text="", command=self.toggle_theme)
        self.theme_button.pack(side='right', padx=5)

        self.auto_save_button = tk.Button(top_frame, text="Auto-Save: ON", command=self.toggle_auto_save)
        self.auto_save_button.pack_forget()

        font_menu.bind("<<ComboboxSelected>>", self._update_font)
        size_menu.bind("<<ComboboxSelected>>", self._update_font)

        self.text_area = scrolledtext.ScrolledText(self.root, undo=True)
        self.text_area.pack(fill='both', expand=True)
        self._update_font()

    def _create_menu(self):
        self.menu_bar = Menu(self.root)
        file_menu = Menu(self.menu_bar, tearoff=0)
        edit_menu = Menu(self.menu_bar, tearoff=0)

        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()

        self.recent_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=self.menu_bar)

        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About SSNote™", command=self.show_about)
        help_menu.add_command(label="License", command=self.show_license)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def _bind_events(self):
        self.text_area.bind('<KeyRelease>', self._update_status)

    def _update_font(self, event=None):
        try:
            selected_font = self.current_font.get()
            selected_size = self.current_size.get()
            self.text_area.configure(font=(selected_font, selected_size))
        except tk.TclError:
            pass

    def _update_status(self, event=None):
        self._update_status_bar()

        content = self.text_area.get(1.0, 'end-1c')
        words = len(content.split())
        characters = len(content)
        name = os.path.basename(self.filename) if self.filename else "Untitled"
        status = f"File: {name} | Words: {words} | Characters: {characters}"
        if self.filename:
            status += f" | Auto-Save: {'ON' if self.auto_save_enabled else 'OFF'}"
        else:
            status += " | Auto-Save: Pending"
        self.status_bar.config(text=status)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.user_theme_override = self.current_theme
        self._save_config()
        self._apply_theme()

    def toggle_wrap(self):
        self.wrap_enabled = not self.wrap_enabled
        self._apply_wrap()
        self._save_config()

    def _apply_wrap(self):
        wrap_mode = 'word' if self.wrap_enabled else 'none'
        self.text_area.config(wrap=wrap_mode)
        self.wrap_button.config(text=f"Wrap: {'ON' if self.wrap_enabled else 'OFF'}")

    def _apply_theme(self):
        theme = THEMES[self.user_theme_override or self._detect_system_theme()]
        self.text_area.config(
            bg=theme["bg"],
            fg=theme["fg"],
            insertbackground=theme["insertbackground"],
            selectbackground=theme["selectbackground"]
        )
        self.theme_button.config(text=theme["button"])
        self.status_bar.config(bg=theme["bg"], fg=theme["fg"])
        self.root.config(bg=theme["bg"])

    def _save_config(self):
        self.config_data["theme"] = self.user_theme_override
        self.config_data["wrap"] = self.wrap_enabled
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f)

    def _update_config_last_file(self):
        self.config_data["last_file"] = self.filename
        self._update_recent_files(self.filename)
        self._save_config()

    def _init_file_from_config(self):
        last_file = self.config_data.get("last_file")
        if last_file and os.path.exists(last_file):
            try:
                with open(last_file, "r", encoding="utf-8") as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.filename = last_file
                self.last_saved_time = time.time()
                if not self.auto_save_visible:
                    self.auto_save_button.pack(side='right', padx=5)
                    self.auto_save_visible = True
                self._update_status()
            except Exception as e:
                print(f"Failed to load last file: {e}")
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Documents", "*.txt")])
            if not self.filename:
                return
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("")
            self.root.title(f"SSNote™ - {os.path.basename(self.filename)}")
            self.last_saved_time = time.time()
            self.text_area.edit_modified(False)
            self._update_status()


    def _refresh_recent_files_menu(self):
        self.recent_menu.delete(0, tk.END)
        recent = self.config_data.get("recent_files", [])
        cleaned = []
        for path in recent:
            if os.path.exists(path):
                cleaned.append(path)
                self.recent_menu.add_command(label=path, command=lambda p=path: self._open_recent_file(p))
        self.config_data["recent_files"] = cleaned
        self._save_config()

    def _update_recent_files(self, path):
        if not path:
            return
        files = self.config_data.get("recent_files", [])
        if path in files:
            files.remove(path)
        files.insert(0, path)
        self.config_data["recent_files"] = files[:5]

    def _open_recent_file(self, path):
        if self.filename:
            self.save_file(silent=True)
        try:
            with open(path, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.filename = path
            self._update_config_last_file()
            if not self.auto_save_visible:
                self.auto_save_button.pack(side='right', padx=5)
                self.auto_save_visible = True
            self.auto_save_locked = False
            self.last_saved_time = time.time()
            self._update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def _schedule_auto_save(self):
        self._auto_save()
        self.root.after(120000, self._schedule_auto_save)

    def _auto_save(self):
        if self.filename:
            if self.auto_save_enabled:
                self.save_file(silent=True)
        elif not self.auto_save_locked:
            result = messagebox.askyesno("Save Required", "File must be saved to enable auto-save.\nDo you want to save now?")
            if result:
                self.save_as_file()
            else:
                self.auto_save_locked = True

    def toggle_auto_save(self):
        self.auto_save_enabled = not self.auto_save_enabled
        self.auto_save_button.config(text=f"Auto-Save: {'ON' if self.auto_save_enabled else 'OFF'}")
        self._update_status()

    def _on_close(self):
        if self.filename:
            self.save_file(silent=True)
        self._save_config()
        self.root.destroy()

    def new_file(self):
        # Step 1: Auto-save current file silently
        if self.filename:
            try:
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", tk.END))
                self.last_saved_time = time.time()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to auto-save current file: {e}")
                return

        # Step 2: Prompt for new filename BEFORE clearing
        new_filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text Documents", "*.txt")])
        if not new_filename:
            return  # user cancelled — do nothing

        # Step 3: Clear and initialize new file
        self.text_area.delete("1.0", tk.END)
        self.filename = new_filename
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")  # create empty file

        self.root.title(f"SSNote™ - {os.path.basename(self.filename)}")
        self.last_saved_time = time.time()
        self.auto_save_button.pack_forget()
        self.auto_save_visible = False
        self.auto_save_locked = False
        self.text_area.edit_modified(False)
        self._update_status()

    def open_file(self):
        if self.filename:
            self.save_file(silent=True)
        self.filename = filedialog.askopenfilename(defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self._update_config_last_file()
            if not self.auto_save_visible:
                self.auto_save_button.pack(side='right', padx=5)
                self.auto_save_visible = True
            self.auto_save_locked = False
            self._update_status()

    def save_file(self, silent=False):
        if not self.filename:
            self.save_as_file()
        else:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.last_saved_time = time.time()
            self._update_config_last_file()
            if not silent:
                messagebox.showinfo("Saved", "File saved.")
            self._update_status()
            if not self.auto_save_visible:
                self.auto_save_button.pack(side='right', padx=5)
                self.auto_save_visible = True
            self.auto_save_locked = False

    def save_as_file(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if self.filename:
            self.save_file()

    
    
    def _create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("SSNote™ ready.")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

    def _update_status_bar(self):
        filename = os.path.basename(self.filename) if self.filename else "Untitled"
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        
        
        if self.last_saved_time is not None and isinstance(self.last_saved_time, (int, float)):
            elapsed = int(time.time() - self.last_saved_time)
            if elapsed < 60:
                saved = f"{elapsed} sec ago"
            else:
                saved = f"{elapsed // 60} min ago"
        else:
            saved = "Not yet saved"

        self.status_var.set(f"[ {filename} ] | Words: {words} | Characters: {chars} | Last saved: {saved}")
        self.root.after(1000, self._update_status_bar)


    def show_about(self):
        messagebox.showinfo("About SSNote™", "SSNote™\nStupidly Simple Notepad\nVersion 1.0\n\nBuilt by Gazali\nFree under MIT License")

    def show_license(self):
        license_window = tk.Toplevel(self.root)
        license_window.title("MIT License")
        text = tk.Text(license_window, wrap="word", height=30, width=80)
        text.insert(tk.END, LICENSE_TEXT)
        text.config(state="disabled")
        text.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    notepad = Notepad(root)
    root.mainloop()

    
    
    def _create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("SSNote™ ready.")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

    def _update_status_bar(self):
        filename = os.path.basename(self.filename) if self.filename else "Untitled"
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        
        
        if self.last_saved_time is not None and isinstance(self.last_saved_time, (int, float)):
            elapsed = int(time.time() - self.last_saved_time)
            if elapsed < 60:
                saved = f"{elapsed} sec ago"
            else:
                saved = f"{elapsed // 60} min ago"
        else:
            saved = "Not yet saved"

        self.status_var.set(f"[ {filename} ] | Words: {words} | Characters: {chars} | Last saved: {saved}")
        self.root.after(1000, self._update_status_bar)


    def show_about(self):
        messagebox.showinfo("About SSNote™", "SSNote™\nStupidly Simple Notepad\nVersion 1.0\n\nBuilt by Gazali\nFree under MIT License")

    def show_license(self):
        license_window = tk.Toplevel(self.root)
        license_window.title("MIT License")
        text = tk.Text(license_window, wrap="word", height=30, width=80)
        text.insert(tk.END, LICENSE_TEXT)
        text.config(state="disabled")
        text.pack(expand=1, fill="both")
#!/usr/bin/env python3
import os
import sys
import json
import argparse
import locale
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

IMAGE_EXTS = {
    ".png", ".jpeg", ".jpg", ".webp", ".bmp", ".gif",
    ".tiff", ".tif", ".heic", ".avif",
}

LOG_FILE = "rename_history.json"

# ==========================================
# ЛОКАЛИЗАЦИЯ (СЛОВАРИ)
# ==========================================
STRINGS = {
    "ru": {
        "title": "Переименовать в JPG",
        "folder": "Папка:",
        "browse": "Обзор...",
        "mode": "Режим:",
        "mode_1": "Добавить .jpg",
        "mode_2": "Заменить расширение",
        "recursive": "Включая вложенные папки",
        "dry_run": "Тест (без изменений)",
        "run": "▶ Запустить",
        "undo": "↩ Отменить последнее",
        "no_folder": "Выберите папку!",
        "undo_title": "Отмена",
        "undo_empty": "Нет файла истории для отмены.",
        "undo_ok": "Успешно отменено {} переименований.",
        "undo_err": "Ошибка при отмене: {}",
        "log_skip_jpg": "⏭ Пропущен (уже .jpg): {}",
        "log_skip_not_img": "⏭ Пропущен (не изображение): {}",
        "log_conflict": "⚠️ Конфликт: {} → {} (уже существует)",
        "log_dry": "🔍 (тест) {} → {}",
        "log_ok": "✅ {} → {}",
        "log_err": "❌ Ошибка: {} — {}",
        "log_summary": "\n📊 Итог: переименовано {}, пропущено {}",
        "lang": "Язык:",
    },
    "en": {
        "title": "Rename to JPG",
        "folder": "Folder:",
        "browse": "Browse...",
        "mode": "Mode:",
        "mode_1": "Append .jpg",
        "mode_2": "Replace extension",
        "recursive": "Include subfolders",
        "dry_run": "Dry-run (no changes)",
        "run": "▶ Run",
        "undo": "↩ Undo last",
        "no_folder": "Please select a folder!",
        "undo_title": "Undo",
        "undo_empty": "No history file to undo.",
        "undo_ok": "Successfully undone {} renames.",
        "undo_err": "Error during undo: {}",
        "log_skip_jpg": "⏭ Skipped (already .jpg): {}",
        "log_skip_not_img": "⏭ Skipped (not an image): {}",
        "log_conflict": "⚠️ Conflict: {} → {} (already exists)",
        "log_dry": "🔍 (dry-run) {} → {}",
        "log_ok": "✅ {} → {}",
        "log_err": "❌ Error: {} — {}",
        "log_summary": "\n📊 Summary: renamed {}, skipped {}",
        "lang": "Language:",
    }
}

def detect_lang():
    try:
        loc = locale.getlocale()[0] or ""
    except Exception:
        loc = ""
    return "ru" if loc.lower().startswith("ru") else "en"

# ==========================================
# ЛОГИКА
# ==========================================
def get_files(folder_path, recursive=False):
    file_list = []
    if recursive:
        for root, _, files in os.walk(folder_path):
            for f in files:
                file_list.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder_path):
            path = os.path.join(folder_path, f)
            if os.path.isfile(path):
                file_list.append(path)
    return sorted(file_list)

def process_files(folder_path, mode, recursive=False, dry_run=False, log_callback=None, lang="ru"):
    t = STRINGS[lang]
    if not os.path.isdir(folder_path):
        msg = f"❌ Folder not found: {folder_path}" if lang=="en" else f"❌ Папка не найдена: {folder_path}"
        return log_callback(msg) if log_callback else print(msg)

    files = get_files(folder_path, recursive)
    renamed_count = 0
    skipped_count = 0
    history = []

    for old_path in files:
        filename = os.path.basename(old_path)
        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        def log(text):
            if log_callback: log_callback(text)
            else: print(text)

        if ext_lower == ".jpg":
            log(t["log_skip_jpg"].format(filename))
            skipped_count += 1
            continue

        if ext_lower and ext_lower not in IMAGE_EXTS:
            log(t["log_skip_not_img"].format(filename))
            skipped_count += 1
            continue

        new_filename = filename + ".jpg" if mode == "1" else name + ".jpg"
        new_path = os.path.join(os.path.dirname(old_path), new_filename)

        if os.path.exists(new_path):
            log(t["log_conflict"].format(filename, new_filename))
            skipped_count += 1
            continue

        if dry_run:
            log(t["log_dry"].format(filename, new_filename))
            renamed_count += 1
            continue

        try:
            os.rename(old_path, new_path)
            log(t["log_ok"].format(filename, new_filename))
            renamed_count += 1
            history.append({"old": old_path, "new": new_path})
        except OSError as e:
            log(t["log_err"].format(filename, e))
            skipped_count += 1

    if history:
        try:
            existing_history = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    existing_history = json.load(f)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_history.append({"timestamp": timestamp, "changes": history})
            
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Log error: {e}")

    log(t["log_summary"].format(renamed_count, skipped_count))

def undo_last(lang="ru"):
    t = STRINGS[lang]
    if not os.path.exists(LOG_FILE):
        return t["undo_empty"]
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        if not history:
            return t["undo_empty"]
        
        last_op = history.pop()
        restored = 0
        for item in last_op["changes"]:
            old_path, new_path = item["old"], item["new"]
            if os.path.exists(new_path):
                os.rename(new_path, old_path)
                restored += 1
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return t["undo_ok"].format(restored)
    except Exception as e:
        return t["undo_err"].format(e)

# ==========================================
# GUI
# ==========================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Вишнево-белая палитра
        self.bg_color = "#E5E7EB"
        self.cherry = "#800020"
        self.cherry_hover = "#5c0017"
        self.text_color = "#1F2937"
        
        self.root.configure(bg=self.bg_color)
        
        self.lang_var = tk.StringVar(value=detect_lang())
        
        self.folder_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="1")
        self.recursive_var = tk.BooleanVar(value=False)
        self.dry_run_var = tk.BooleanVar(value=False)

        self.t = STRINGS[self.lang_var.get()]
        
        self.build_ui()
        self.update_lang() # Первичная отрисовка текста

    def build_ui(self):
        # 1. Язык (сверху справа)
        frame_lang = tk.Frame(self.root, bg=self.bg_color)
        frame_lang.pack(fill=tk.X, padx=10, pady=5)
        self.lbl_lang = tk.Label(frame_lang, bg=self.bg_color, fg=self.text_color)
        self.lbl_lang.pack(side=tk.LEFT)
        
        self.rb_ru = tk.Radiobutton(frame_lang, text="RU", variable=self.lang_var, value="ru", command=self.update_lang, bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.rb_ru.pack(side=tk.LEFT, padx=5)
        
        self.rb_en = tk.Radiobutton(frame_lang, text="EN", variable=self.lang_var, value="en", command=self.update_lang, bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.rb_en.pack(side=tk.LEFT)

        # 2. Выбор папки
        frame_path = tk.Frame(self.root, pady=10, padx=10, bg=self.bg_color)
        frame_path.pack(fill=tk.X)
        self.lbl_folder = tk.Label(frame_path, bg=self.bg_color, fg=self.text_color)
        self.lbl_folder.pack(side=tk.LEFT)
        tk.Entry(frame_path, textvariable=self.folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.btn_browse = tk.Button(frame_path, command=self.browse_folder, bg=self.bg_color, fg=self.cherry, relief=tk.GROOVE)
        self.btn_browse.pack(side=tk.LEFT)

        # 3. Настройки
        frame_opts = tk.Frame(self.root, padx=10, pady=5, bg=self.bg_color)
        frame_opts.pack(fill=tk.X)
        
        self.lbl_mode = tk.Label(frame_opts, bg=self.bg_color, fg=self.text_color)
        self.lbl_mode.grid(row=0, column=0, sticky=tk.W)
        
        self.rb_mode1 = tk.Radiobutton(frame_opts, variable=self.mode_var, value="1", bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.rb_mode1.grid(row=0, column=1, sticky=tk.W)
        
        self.rb_mode2 = tk.Radiobutton(frame_opts, variable=self.mode_var, value="2", bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.rb_mode2.grid(row=0, column=2, sticky=tk.W)

        self.chk_recursive = tk.Checkbutton(frame_opts, variable=self.recursive_var, bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.chk_recursive.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.chk_dry = tk.Checkbutton(frame_opts, variable=self.dry_run_var, bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.bg_color)
        self.chk_dry.grid(row=1, column=2, sticky=tk.W, pady=5)

        # 4. Кнопки
        frame_btns = tk.Frame(self.root, pady=15, bg=self.bg_color)
        frame_btns.pack()
        
        self.btn_run = tk.Button(frame_btns, command=self.run_script, bg=self.cherry, fg="white", font=("Segoe UI", 10, "bold"), width=18, relief=tk.FLAT, cursor="hand2")
        self.btn_run.pack(side=tk.LEFT, padx=10)
        
        self.btn_undo = tk.Button(frame_btns, command=self.run_undo, bg="white", fg=self.cherry, font=("Segoe UI", 10), width=20, relief=tk.GROOVE, cursor="hand2", bd=1)
        self.btn_undo.pack(side=tk.LEFT, padx=10)

        # 5. Лог с полосой прокрутки
        # Создаем фрейм, чтобы текст и скроллбар стояли рядом
        frame_log = tk.Frame(self.root, bg=self.bg_color)
        frame_log.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Создаем скроллбар (в вишневом цвете не получится, Tkinter использует системный)
        scrollbar = tk.Scrollbar(frame_log)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Создаем текстовое поле и привязываем к скроллбару
        self.log_text = tk.Text(frame_log, height=15, padx=10, pady=10, state=tk.DISABLED, bg="#F3F4F6", fg=self.text_color, font=("Consolas", 10), relief=tk.FLAT, bd=1, yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Связываем скроллбар с полем
        scrollbar.config(command=self.log_text.yview)

    def update_lang(self):
        self.t = STRINGS[self.lang_var.get()]
        self.root.title(self.t["title"])
        self.lbl_lang.config(text=self.t["lang"])
        self.lbl_folder.config(text=self.t["folder"])
        self.btn_browse.config(text=self.t["browse"])
        self.lbl_mode.config(text=self.t["mode"])
        self.rb_mode1.config(text=self.t["mode_1"])
        self.rb_mode2.config(text=self.t["mode_2"])
        self.chk_recursive.config(text=self.t["recursive"])
        self.chk_dry.config(text=self.t["dry_run"])
        self.btn_run.config(text=self.t["run"])
        self.btn_undo.config(text=self.t["undo"])

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_script(self):
        folder = self.folder_var.get()
        if not folder:
            messagebox.showwarning(self.t["title"], self.t["no_folder"])
            return
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        process_files(
            folder_path=folder,
            mode=self.mode_var.get(),
            recursive=self.recursive_var.get(),
            dry_run=self.dry_run_var.get(),
            log_callback=self.log,
            lang=self.lang_var.get()
        )

    def run_undo(self):
        result = undo_last(lang=self.lang_var.get())
        messagebox.showinfo(self.t["undo_title"], result)

# ==========================================
# CLI
# ==========================================
def main_cli():
    parser = argparse.ArgumentParser(description="Batch rename to .jpg")
    parser.add_argument("folder", help="Folder path")
    parser.add_argument("--mode", choices=["1", "2"], default="1")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--undo", action="store_true")
    parser.add_argument("--lang", choices=["ru", "en"], default=detect_lang())
    
    args = parser.parse_args()

    if args.undo:
        print(undo_last(lang=args.lang))
        return

    process_files(
        folder_path=args.folder,
        mode=args.mode,
        recursive=args.recursive,
        dry_run=args.dry_run,
        lang=args.lang
    )

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        
    if len(sys.argv) > 1:
        main_cli()
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
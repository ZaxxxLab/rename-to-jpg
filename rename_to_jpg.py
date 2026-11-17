#!/usr/bin/env python3
"""
rename_to_jpg.py — batch-rename image files to .jpg / массовое переименование
файлов изображений в .jpg

Modes / Режимы:
  1 (default) — append .jpg: photo.png → photo.png.jpg
  2 — replace extension: photo.png → photo.jpg

Only files with image extensions (.png, .jpeg, .webp, .bmp, .gif, .tiff, .tif,
.heic, .avif) and files without an extension are renamed. Everything else
(pdf, docx, exe, etc.) is skipped so you don't break a file by accident.

NOTE: this script does NOT convert files. It only changes the name. Renaming
a PNG to .jpg leaves the content as PNG, and some programs may fail to open it.
"""

import argparse
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

IMAGE_EXTS = {
    ".png", ".jpeg", ".jpg", ".webp", ".bmp", ".gif",
    ".tiff", ".tif", ".heic", ".avif",
}

# ---------------------------------------------------------------- translations
STRINGS = {
    "en": {
        "folder_not_found": "❌ Folder not found: {path}",
        "read_error": "❌ Could not read folder: {err}",
        "skip_already": "⏭ Skipped (already .jpg): {name}",
        "skip_not_image": "⏭ Skipped (not an image): {name}",
        "conflict": "⚠️ Conflict: {old} → {new} (already exists, skipped)",
        "dry_run": "🔍 (dry-run) {old} → {new}",
        "renamed": "✅ {old} → {new}",
        "rename_error": "❌ Error renaming {name}: {err}",
        "summary": "\n📊 {prefix}renamed {renamed}, skipped {skipped}",
        "dry_prefix": "Dry-run: ",
        "processing": "\n📁 Processing folder: {path}\n",
        "enter_folder": "Enter folder path: ",
        "no_path": "❌ No path given",
        "modes": "Modes:\n  1 - Append .jpg (keep name)\n  2 - Replace extension with .jpg",
        "choose_mode": "\nChoose mode (1/2) [1]: ",
        "bad_choice": "❌ Invalid choice",
        "help_folder": "Path to folder (prompted if omitted)",
        "help_mode": "1 — append .jpg (default), 2 — replace extension with .jpg",
        "help_dry": "Show what would be done without touching files",
        "help_lang": "UI language: en or ru (default: auto)",
        "desc": "Batch-rename image files to .jpg",
        "epilog": (
            "Examples:\n"
            "  python rename_to_jpg.py C:\\Photos\n"
            "  python rename_to_jpg.py C:\\Photos --mode 2\n"
            "  python rename_to_jpg.py C:\\Photos --dry-run\n"
            "  python rename_to_jpg.py C:\\Photos --lang ru\n"
        ),
    },
    "ru": {
        "folder_not_found": "❌ Папка не найдена: {path}",
        "read_error": "❌ Не удалось прочитать папку: {err}",
        "skip_already": "⏭ Пропущен (уже .jpg): {name}",
        "skip_not_image": "⏭ Пропущен (не изображение): {name}",
        "conflict": "⚠️ Конфликт: {old} → {new} (уже существует, пропущен)",
        "dry_run": "🔍 (dry-run) {old} → {new}",
        "renamed": "✅ {old} → {new}",
        "rename_error": "❌ Ошибка при переименовании {name}: {err}",
        "summary": "\n📊 {prefix}переименовано {renamed}, пропущено {skipped}",
        "dry_prefix": "Dry-run: ",
        "processing": "\n📁 Обработка папки: {path}\n",
        "enter_folder": "Введите путь к папке: ",
        "no_path": "❌ Путь не указан",
        "modes": "Режимы:\n  1 - Только добавить .jpg (не меняя имя)\n  2 - Заменить расширение на .jpg",
        "choose_mode": "\nВыберите режим (1/2) [1]: ",
        "bad_choice": "❌ Неверный выбор",
        "help_folder": "Путь к папке (если не указан — будет запрошен)",
        "help_mode": "1 — добавить .jpg в конец (по умолчанию), 2 — заменить расширение на .jpg",
        "help_dry": "Показать, что будет сделано, но не менять файлы",
        "help_lang": "Язык интерфейса: en или ru (по умолчанию: авто)",
        "desc": "Массовое переименование файлов изображений в .jpg",
        "epilog": (
            "Примеры:\n"
            "  python rename_to_jpg.py C:\\Photos\n"
            "  python rename_to_jpg.py C:\\Photos --mode 2\n"
            "  python rename_to_jpg.py C:\\Photos --dry-run\n"
            "  python rename_to_jpg.py C:\\Photos --lang ru\n"
        ),
    },
}


def detect_lang() -> str:
    """Auto-detect language from the system locale. Falls back to English."""
    try:
        import locale
        loc = locale.getlocale()[0] or ""
    except Exception:
        loc = ""
    return "ru" if loc.lower().startswith("ru") else "en"


def t(lang: str, key: str, **kwargs) -> str:
    return STRINGS[lang][key].format(**kwargs)


# ---------------------------------------------------------------- core logic
def rename_files_to_jpg(
    folder_path: str,
    add_jpg_only: bool = True,
    dry_run: bool = False,
    lang: str = "en",
) -> None:
    if not os.path.isdir(folder_path):
        print(t(lang, "folder_not_found", path=folder_path))
        return

    try:
        files = sorted(os.listdir(folder_path))
    except OSError as e:
        print(t(lang, "read_error", err=e))
        return

    renamed_count = 0
    skipped_count = 0

    for filename in files:
        old_path = os.path.join(folder_path, filename)

        if os.path.isdir(old_path):
            continue

        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        if ext_lower == ".jpg":
            print(t(lang, "skip_already", name=filename))
            skipped_count += 1
            continue

        if ext_lower and ext_lower not in IMAGE_EXTS:
            print(t(lang, "skip_not_image", name=filename))
            skipped_count += 1
            continue

        new_filename = filename + ".jpg" if add_jpg_only else name + ".jpg"
        new_path = os.path.join(folder_path, new_filename)

        if os.path.exists(new_path):
            print(t(lang, "conflict", old=filename, new=new_filename))
            skipped_count += 1
            continue

        if dry_run:
            print(t(lang, "dry_run", old=filename, new=new_filename))
            renamed_count += 1
            continue

        try:
            os.rename(old_path, new_path)
            print(t(lang, "renamed", old=filename, new=new_filename))
            renamed_count += 1
        except OSError as e:
            print(t(lang, "rename_error", name=filename, err=e))
            skipped_count += 1

    prefix = t(lang, "dry_prefix") if dry_run else ""
    print(t(lang, "summary", prefix=prefix, renamed=renamed_count, skipped=skipped_count))


# ---------------------------------------------------------------- CLI
def parse_args(argv=None):
    # Pre-scan --lang so help text is already in the right language.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--lang", choices=["en", "ru"], default=None)
    known, _ = pre.parse_known_args(argv)
    lang = known.lang or detect_lang()

    parser = argparse.ArgumentParser(
        description=t(lang, "desc"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=t(lang, "epilog"),
    )
    parser.add_argument("folder", nargs="?", help=t(lang, "help_folder"))
    parser.add_argument(
        "--mode", choices=["1", "2"], default=None, help=t(lang, "help_mode")
    )
    parser.add_argument(
        "--dry-run", action="store_true", help=t(lang, "help_dry")
    )
    parser.add_argument(
        "--lang", choices=["en", "ru"], default=None, help=t(lang, "help_lang")
    )
    args = parser.parse_args(argv)
    args.lang = args.lang or lang
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    lang = args.lang

    folder = args.folder
    if not folder:
        folder = input(t(lang, "enter_folder")).strip()
    if not folder:
        print(t(lang, "no_path"))
        return 1

    print(t(lang, "processing", path=folder))

    mode = args.mode
    if mode is None:
        print(t(lang, "modes"))
        mode = input(t(lang, "choose_mode")).strip() or "1"

    if mode not in ("1", "2"):
        print(t(lang, "bad_choice"))
        return 1

    rename_files_to_jpg(
        folder,
        add_jpg_only=(mode == "1"),
        dry_run=args.dry_run,
        lang=lang,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
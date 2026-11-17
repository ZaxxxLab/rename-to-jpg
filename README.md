# rename_to_jpg

A small cross-platform utility that batch-renames image files to the `.jpg` extension. Available as a modern **GUI application** or a **command-line tool**. No dependencies, no installation — just Python 3.8+ (or a prebuilt binary from [Releases](../../releases)).

> **This is not a converter.** The script changes file names only. Renaming a PNG to `.jpg` leaves the content as PNG, and some programs may fail to open it. If you need real conversion, use ImageMagick, `pillow`, or `ffmpeg`.

## Features

- **Beautiful GUI:** Select folders visually, toggle options, and see the results in real-time.
- **Multi-language:** English and Russian UI (auto-detected).
- **Undo:** Accidentally renamed 500 files? One click rolls it back.
- **Recursive:** Optionally include all subfolders.
- **Safe:** Skips non-image files (like `.pdf` or `.exe`) to prevent breaking them.
- **Dry-run mode:** Preview changes before applying them.

## Screenshots

![Interface](docs/screenshot-main.png)
![Result](docs/screenshot-result.png)


> \*\*This is not a converter.\*\* The script changes file names only. Renaming a PNG to `.jpg` leaves the content as PNG, and some programs may fail to open it. If you need real conversion, use ImageMagick, `pillow`, or `ffmpeg`.



\## Why



Photo dumps, exports from messaging apps, and scraped datasets often contain files with the wrong extension (`.jpeg`, `.png`, `.webp`, or no extension at all). Some tools expect `.jpg` specifically. This script fixes the names in bulk, safely:



\- Only touches files that look like images (`.png`, `.jpeg`, `.webp`, `.bmp`, `.gif`, `.tiff`, `.tif`, `.heic`, `.avif`) and files with no extension.

\- Skips everything else (`.pdf`, `.docx`, `.exe`, …) so you don't break a file by accident.

\- Refuses to overwrite an existing file.

\- Never aborts the whole run because of one error.



\## Usage



```bash

python rename\_to\_jpg.py <folder> \[--mode 1|2] \[--dry-run] \[--lang en|ru]


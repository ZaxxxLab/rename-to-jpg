\# rename\_to\_jpg



A small cross-platform command-line utility that batch-renames image files to the `.jpg` extension. No dependencies, no installation — just Python 3.8+ (or a prebuilt binary from \[Releases](../../releases)).



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


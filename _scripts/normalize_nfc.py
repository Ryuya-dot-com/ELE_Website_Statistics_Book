#!/usr/bin/env python3
"""
Post-render script: normalize rendered HTML and keep the root index in sync.

macOS generates NFD (decomposed) Unicode in file paths and HTML content,
but GitHub Pages / Git stores filenames in NFC (composed) form. This mismatch
causes 404 errors for chapters with dakuten/handakuten characters
(e.g., デ, ベ, ジ, ド, etc.) in Japanese filenames.

Quarto exposes the active output directory via QUARTO_PROJECT_OUTPUT_DIR, so
this script normalizes whichever HTML output directory was used for the render.
When the output dir is the default _book, it also refreshes the project-root
index.html from _book/index.html so the top page is available without a manual
copy step.
"""

import unicodedata
import os
import glob
import sys
import shutil


def get_output_dir(project_root):
    output_dir = os.getenv("QUARTO_PROJECT_OUTPUT_DIR", "_book")
    if os.path.isabs(output_dir):
        return output_dir
    return os.path.join(project_root, output_dir)


def sync_root_index(project_root, output_dir):
    output_dir_name = os.path.basename(os.path.normpath(output_dir))
    if output_dir_name != "_book":
        return

    source_index = os.path.join(output_dir, "index.html")
    target_index = os.path.join(project_root, "index.html")

    if not os.path.isfile(source_index):
        return

    try:
        shutil.copy2(source_index, target_index)
        print("[normalize_nfc] Synced root index.html from _book/index.html.")
    except Exception as e:
        print(f"[normalize_nfc] Warning: Could not sync root index.html: {e}", file=sys.stderr)

def normalize_html_files():
    # Determine project root (script is in _scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = get_output_dir(project_root)

    if not os.path.isdir(output_dir):
        print(f"[normalize_nfc] Output directory not found at {output_dir}", file=sys.stderr)
        sys.exit(0)  # Don't fail the build

    fixed_count = 0
    total_count = 0

    for html_file in glob.glob(os.path.join(output_dir, '**', '*.html'), recursive=True):
        total_count += 1
        try:
            with open(html_file, 'rb') as f:
                content = f.read()
            text = content.decode('utf-8')
            nfc_text = unicodedata.normalize('NFC', text)
            if text != nfc_text:
                with open(html_file, 'wb') as f:
                    f.write(nfc_text.encode('utf-8'))
                fixed_count += 1
        except Exception as e:
            print(f"[normalize_nfc] Warning: Could not process {html_file}: {e}", file=sys.stderr)

    print(f"[normalize_nfc] Processed {total_count} HTML files, normalized {fixed_count} from NFD to NFC.")
    sync_root_index(project_root, output_dir)

if __name__ == '__main__':
    normalize_html_files()

#!/usr/bin/env python3
"""
Post-render script: Normalize HTML files from NFD to NFC Unicode form.

macOS generates NFD (decomposed) Unicode in file paths and HTML content,
but GitHub Pages / Git stores filenames in NFC (composed) form.
This mismatch causes 404 errors for chapters with dakuten/handakuten
characters (e.g., デ, ベ, ジ, ド, etc.) in Japanese filenames.

This script normalizes all HTML content in _book/ to NFC after Quarto render.
"""

import unicodedata
import os
import glob
import sys

def normalize_html_files():
    # Determine project root (script is in _scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    book_dir = os.path.join(project_root, '_book')

    if not os.path.isdir(book_dir):
        print(f"[normalize_nfc] _book directory not found at {book_dir}", file=sys.stderr)
        sys.exit(0)  # Don't fail the build

    fixed_count = 0
    total_count = 0

    for html_file in glob.glob(os.path.join(book_dir, '**', '*.html'), recursive=True):
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

if __name__ == '__main__':
    normalize_html_files()

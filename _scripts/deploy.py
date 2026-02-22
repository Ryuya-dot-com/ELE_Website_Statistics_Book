#!/usr/bin/env python3
"""
Deploy script: Copy _book/ with NFC-normalized filenames, then deploy to gh-pages.

macOS APFS returns filenames in NFD (decomposed) Unicode form, but GitHub Pages
requires NFC (composed) form. This script copies _book/ to a temp directory with
NFC filenames before deploying via ghp-import.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unicodedata

EXCLUDE_EXTENSIONS = {".epub"}


def copy_with_nfc(src, dst):
    """Copy src directory to dst with all filenames normalized to NFC."""
    normalized_count = 0
    excluded_count = 0
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        nfc_rel = unicodedata.normalize('NFC', rel)
        dst_dir = os.path.join(dst, nfc_rel)
        os.makedirs(dst_dir, exist_ok=True)

        for f in files:
            if os.path.splitext(f)[1].lower() in EXCLUDE_EXTENSIONS:
                excluded_count += 1
                continue
            nfc_name = unicodedata.normalize('NFC', f)
            shutil.copy2(os.path.join(root, f), os.path.join(dst_dir, nfc_name))
            if f != nfc_name:
                normalized_count += 1
    return normalized_count, excluded_count


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    book_dir = os.path.join(project_root, '_book')

    if not os.path.isdir(book_dir):
        print(f"Error: _book directory not found at {book_dir}", file=sys.stderr)
        sys.exit(1)

    msg = sys.argv[1] if len(sys.argv) > 1 else "Built site for gh-pages"

    with tempfile.TemporaryDirectory() as tmpdir:
        nfc_dir = os.path.join(tmpdir, '_book_nfc')
        normalized_count, excluded_count = copy_with_nfc(book_dir, nfc_dir)
        print(
            "[deploy] Copied _book/ "
            f"(normalized NFC filenames: {normalized_count}, "
            f"excluded files: {excluded_count})"
        )

        result = subprocess.run(
            [sys.executable, '-m', 'ghp_import', '-n', '-p', '-f', '-m', msg, nfc_dir],
            cwd=project_root,
        )
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()

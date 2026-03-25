#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_OUTPUT_DIR="${TMPDIR:-/tmp}/ele_stats_book_html"
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
SYNC_TO_BOOK=0

usage() {
  cat <<'EOF'
Usage:
  _scripts/render_book_html.sh [--output-dir DIR] [--sync] [-- quarto args...]

Options:
  --output-dir DIR  Render HTML to DIR instead of /tmp/ele_stats_book_html
  --sync            After rendering, rsync the HTML site back to ./_book and
                    refresh ./index.html from ./_book/index.html
  --                Pass remaining arguments directly to `quarto render`

Examples:
  _scripts/render_book_html.sh
  _scripts/render_book_html.sh --sync
  _scripts/render_book_html.sh --output-dir /tmp/book-preview -- index.qmd
EOF
}

QUARTO_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --sync)
      SYNC_TO_BOOK=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      QUARTO_ARGS+=("$@")
      break
      ;;
    *)
      QUARTO_ARGS+=("$1")
      shift
      ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

echo "[render_book_html] Rendering HTML to: $OUTPUT_DIR"
(
  cd "$PROJECT_ROOT"
  if [[ ${#QUARTO_ARGS[@]} -gt 0 ]]; then
    /usr/local/bin/quarto render "${QUARTO_ARGS[@]}" --to html --output-dir "$OUTPUT_DIR"
  else
    /usr/local/bin/quarto render --to html --output-dir "$OUTPUT_DIR"
  fi
)

echo "[render_book_html] HTML output is ready at: $OUTPUT_DIR"

if [[ "$SYNC_TO_BOOK" -eq 1 ]]; then
  echo "[render_book_html] Syncing rendered site back to $PROJECT_ROOT/_book"
  rsync -a --delete "$OUTPUT_DIR"/ "$PROJECT_ROOT/_book"/
  cp "$PROJECT_ROOT/_book/index.html" "$PROJECT_ROOT/index.html"
  echo "[render_book_html] Updated $PROJECT_ROOT/_book and $PROJECT_ROOT/index.html"
fi

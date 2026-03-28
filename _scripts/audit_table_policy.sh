#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
cd "$ROOT"

count_matches() {
  local pattern="$1"
  local file="$2"
  local out
  out=$(rg -c -- "$pattern" "$file" 2>/dev/null || true)
  printf '%s' "${out:-0}"
}

count_code_fence_matches() {
  local pattern="$1"
  local file="$2"
  python3 - "$pattern" "$file" <<'PY'
import re
import sys

pattern, path = sys.argv[1], sys.argv[2]
regex = re.compile(pattern)
count = 0
in_code = False

with open(path, encoding="utf-8") as handle:
    for line in handle:
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code and regex.search(line):
            count += 1

print(count)
PY
}

has_match() {
  local pattern="$1"
  local file="$2"
  if rg -q -- "$pattern" "$file" 2>/dev/null; then
    printf 'yes'
  else
    printf 'no'
  fi
}

printf 'file\tgt_calls\tdt_calls\tkable_calls\twrapper_defs\twrapper_calls\texception_helper_defs\texception_helper_calls\tsource_md_table_lines\tfreeze_exists\tfreeze_has_pipe_table\tfreeze_has_cache_lib_refs\tstale_freeze_candidate\n'

while IFS= read -r file; do
  gt_calls=$(count_code_fence_matches '(^|[^0-9A-Za-z_`])(?:gt|gt::gt)\(' "$file")
  dt_calls=$(count_code_fence_matches '(^|[^0-9A-Za-z_`])(?:DT::datatable|datatable)\(' "$file")
  kable_calls=$(count_code_fence_matches '(^|[^0-9A-Za-z_`])(?:knitr::kable|kable)\(' "$file")
  wrapper_defs=$(count_code_fence_matches '^(?:book_gt|book_kable|gt_light|lite_gt|book_table|causal_static_table)\s*<-\s*(?:function|gt::)|^gt\s*<-\s*gt::gt' "$file")
  wrapper_calls=$(count_code_fence_matches '(?:book_gt|book_kable|gt_light|lite_gt|book_table|causal_static_table)\(' "$file")
  exception_helper_defs=$(count_code_fence_matches '^(?:rma_summary_tbl|compare_models_tbl|rma_to_gt|compare_models_gt)\s*<-\s*function' "$file")
  exception_helper_calls=$(count_code_fence_matches '(?:rma_summary_tbl|compare_models_tbl|rma_to_gt|compare_models_gt)\(' "$file")
  source_md_table_lines=$(count_matches '^\| ' "$file")

  base="${file%.qmd}"
  freeze_path="_freeze/${base}/execute-results/html.json"

  if [[ -f "$freeze_path" ]]; then
    freeze_exists='yes'
    freeze_has_pipe_table=$(has_match 'Table:' "$freeze_path")
    freeze_has_cache_lib_refs=$(has_match 'DT/htmlwidgets/lib|htmlwidgets/lib/' "$freeze_path")
  else
    freeze_exists='no'
    freeze_has_pipe_table='no'
    freeze_has_cache_lib_refs='no'
  fi

  stale_freeze_candidate='no'
  if [[ "$freeze_exists" == 'yes' && "$wrapper_defs" == '0' && "$wrapper_calls" == '0' && "$gt_calls" != '0' && "$freeze_has_pipe_table" == 'yes' && "$source_md_table_lines" == '0' ]]; then
    stale_freeze_candidate='yes'
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$file" \
    "$gt_calls" \
    "$dt_calls" \
    "$kable_calls" \
    "$wrapper_defs" \
    "$wrapper_calls" \
    "$exception_helper_defs" \
    "$exception_helper_calls" \
    "$source_md_table_lines" \
    "$freeze_exists" \
    "$freeze_has_pipe_table" \
    "$freeze_has_cache_lib_refs" \
    "$stale_freeze_candidate"
done < <(rg --files -g '*.qmd' | sort)

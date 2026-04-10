#!/bin/bash

AQUADASH_JOB_PREFIX="cd /opt/aquadash/sensors && python3 -m services."
AQUADASH_CRONTAB_BEGIN="# AQUADASH_SENSORS_BEGIN"
AQUADASH_CRONTAB_END="# AQUADASH_SENSORS_END"

aquadash_crontab_strip_managed() {
  local existing_crontab
  existing_crontab="$(crontab -l 2>/dev/null || true)"

  local without_markers
  without_markers="$(
    printf '%s\n' "$existing_crontab" |
      awk -v begin="$AQUADASH_CRONTAB_BEGIN" -v end="$AQUADASH_CRONTAB_END" '
        $0 == begin { inblock=1; next }
        $0 == end { inblock=0; next }
        !inblock { print }
      '
  )"

  printf '%s\n' "$without_markers" | grep -vF "$AQUADASH_JOB_PREFIX" || true
}


aquadash_crontab_install_jobs() {
  local jobs
  jobs="$1"

  local filtered
  filtered="$(aquadash_crontab_strip_managed)"

  {
    printf '%s\n' "$filtered"
    printf '%s\n' "$AQUADASH_CRONTAB_BEGIN"
    printf '%s\n' "$jobs"
    printf '%s\n' "$AQUADASH_CRONTAB_END"
  } | crontab
}


aquadash_crontab_remove_jobs() {
  aquadash_crontab_strip_managed | crontab
}

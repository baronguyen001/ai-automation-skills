#!/usr/bin/env bash
# Install, list, or remove a cron job that runs a script on a schedule.
# No secrets live in this file. Pass everything at call time.
#   ./cron_linux.sh install "0 9 * * *" "/srv/proj" "python scraper.py"
#   ./cron_linux.sh list
#   ./cron_linux.sh remove "scraper.py"
set -euo pipefail

action="${1:-list}"

case "$action" in
  install)
    schedule="${2:?cron expression required, e.g. '0 9 * * *'}"
    workdir="${3:?working directory required}"
    command="${4:?command required, e.g. 'python scraper.py'}"
    slug="$(printf '%s' "$command" | tr -cs 'a-zA-Z0-9' '-')"
    tag="# cron-dispatch:${slug}"
    lock="/tmp/cron-dispatch-${slug}.lock"
    line="$schedule cd $workdir && flock -n $lock $command >> $workdir/cron.log 2>&1 $tag"
    # replace any existing line with the same tag, then append the new one
    ( crontab -l 2>/dev/null | grep -vF "$tag"; printf '%s\n' "$line" ) | crontab -
    echo "Installed: $line"
    ;;
  list)
    crontab -l 2>/dev/null | grep "cron-dispatch" || echo "no cron-dispatch jobs"
    ;;
  remove)
    match="${2:?substring to remove required}"
    crontab -l 2>/dev/null | grep -vF "$match" | crontab -
    echo "Removed cron lines matching: $match"
    ;;
  *)
    echo "usage: $0 {install|list|remove} ..." >&2
    exit 1
    ;;
esac

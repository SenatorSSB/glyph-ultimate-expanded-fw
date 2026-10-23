#!/bin/bash
# Source only in the approved execution shell. Device calls are read-only.
capture_all() {
  local d="$1" id cursor=0 n next
  mkdir "$d" || return
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-start.jsonl" --output "$d/status-start.json" status || return
  "$PY" "$CONFIG" --read --port "$PORT" --backup-out "$d/config.json" --timeout-sec 5 > "$d/config-command.log" 2>&1 || return
  "$PY" "$IDENTITY" --port "$PORT" --context configurator --session "KGA-ID48-R2-$(basename "$d")" --timeout 2 > "$d/identity.json" || return
  for n in {0..8}; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/list-$cursor.jsonl" --output "$d/list-$cursor.json" list --page "$cursor" --page-size 8 || return
    next=$("$PY" "$FROZEN" cursor "$d/list-$cursor.json") || return
    if [ "$next" = 0 ]; then break; fi
    test "$next" -gt "$cursor" || return 1
    cursor="$next"
  done
  test "$next" = 0 || return 1
  "$PY" "$FROZEN" ids "$d" > "$d/ids.txt" || return
  while IFS= read -r id; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/read-$id.jsonl" --output "$d/read-$id.json" read --profile-id "$id" || return
  done < "$d/ids.txt"
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-end.jsonl" --output "$d/status-end.json" status || return
  "$PY" "$CHECK" snapshot "$d"
}

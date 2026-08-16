#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 /path/to/payload.json" >&2
  exit 2
fi

PAYLOAD_PATH="$1"
PUBLISH_DIR="${PUBLISH_DIR:-/home/shinkato/workspace/daily_vocab_feed_publisher}"
FEED_DIR="${PUBLISH_DIR}/chatgpt_feed"
ARCHIVE_DIR="${FEED_DIR}/archive"
LOCK_DIR="${PUBLISH_DIR}/.feed_publish_lock"

if [ ! -f "$PAYLOAD_PATH" ]; then
  echo "payload does not exist: $PAYLOAD_PATH" >&2
  exit 2
fi

python3 - "$PAYLOAD_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)

for key in ("words", "phrases"):
    items = payload.get(key)
    if not isinstance(items, list) or len(items) != 5:
        raise SystemExit(f"payload must contain exactly 5 {key}")
    for item in items:
        if not isinstance(item, dict) or not all(item.get(field) for field in ("term", "meaning", "example")):
            raise SystemExit(f"each {key} item must contain term, meaning, and example")
PY

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "another feed publication is already running" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR"' EXIT HUP INT TERM

git -C "$PUBLISH_DIR" fetch origin main
git -C "$PUBLISH_DIR" merge --ff-only origin/main

mkdir -p "$ARCHIVE_DIR"
FEED_STAMP="$(date '+%Y-%m-%d_%H%M%S')"
ARCHIVE_PATH="${ARCHIVE_DIR}/${FEED_STAMP}.json"

cp "$PAYLOAD_PATH" "${FEED_DIR}/latest.json"
cp "$PAYLOAD_PATH" "$ARCHIVE_PATH"
python3 "${PUBLISH_DIR}/scripts/build_chatgpt_feed_index.py" "$FEED_DIR"

git -C "$PUBLISH_DIR" add -- \
  chatgpt_feed/latest.json \
  chatgpt_feed/history.json \
  "chatgpt_feed/archive/${FEED_STAMP}.json"

if git -C "$PUBLISH_DIR" diff --cached --quiet -- chatgpt_feed; then
  echo "feed already up to date"
  exit 0
fi

git -C "$PUBLISH_DIR" commit -m "Archive ChatGPT vocabulary feed" -- \
  chatgpt_feed/latest.json \
  chatgpt_feed/history.json \
  "chatgpt_feed/archive/${FEED_STAMP}.json"
git -C "$PUBLISH_DIR" push origin HEAD:main

echo "published ${ARCHIVE_PATH}"

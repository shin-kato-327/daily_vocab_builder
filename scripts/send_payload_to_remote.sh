#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 /path/to/payload.json [send-curated args...]" >&2
  exit 1
fi

PAYLOAD_PATH="$1"
shift
REMOTE_HOST="${REMOTE_HOST:-shinkato@192.168.68.61}"
REMOTE_DIR="${REMOTE_DIR:-/home/shinkato/workspace/daily_vocab_builder}"
REMOTE_PAYLOAD="${REMOTE_DIR}/incoming_payload.json"
LOCAL_REPO="${LOCAL_REPO:-/Users/skat/workspace/vocabulary_builder}"
FEED_PATH="${LOCAL_REPO}/chatgpt_feed/latest.json"

ssh "$REMOTE_HOST" "cat > ${REMOTE_PAYLOAD}" < "$PAYLOAD_PATH"
ssh "$REMOTE_HOST" "cd ${REMOTE_DIR} && python3 -m vocabulary_builder send-curated --payload-file ${REMOTE_PAYLOAD} $* && rm -f ${REMOTE_PAYLOAD}"

mkdir -p "${LOCAL_REPO}/chatgpt_feed"
cp "$PAYLOAD_PATH" "$FEED_PATH"

git -C "$LOCAL_REPO" add -- chatgpt_feed/latest.json
if ! git -C "$LOCAL_REPO" diff --cached --quiet -- chatgpt_feed/latest.json; then
  git -C "$LOCAL_REPO" commit --only -m "Update ChatGPT vocabulary feed" -- chatgpt_feed/latest.json
  git -C "$LOCAL_REPO" push origin HEAD:main
fi

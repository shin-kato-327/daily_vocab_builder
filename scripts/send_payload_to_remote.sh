#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 /path/to/payload.json [send-curated args...]" >&2
  exit 1
fi

PAYLOAD_PATH="$1"
shift
REMOTE_HOST="${REMOTE_HOST:-shinkato@192.168.68.52}"
REMOTE_DIR="${REMOTE_DIR:-/home/shinkato/workspace/daily_vocab_builder}"
REMOTE_PAYLOAD="${REMOTE_DIR}/incoming_payload.json"

ssh "$REMOTE_HOST" "cat > ${REMOTE_PAYLOAD}" < "$PAYLOAD_PATH"
ssh "$REMOTE_HOST" "cd ${REMOTE_DIR} && python3 -m vocabulary_builder send-curated --payload-file ${REMOTE_PAYLOAD} $* && rm -f ${REMOTE_PAYLOAD}"

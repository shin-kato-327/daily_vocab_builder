"""CLI for building and sending a daily vocabulary lesson."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from vocabulary_builder.state import build_daily_pack, load_state, record_pack
from vocabulary_builder.telegram import send


def publish_feed(payload_file: str) -> None:
    configured = os.environ.get("VOCAB_FEED_PUBLISHER")
    script = (
        Path(configured)
        if configured
        else Path("/home/shinkato/workspace/daily_vocab_builder/scripts/publish_chatgpt_feed.sh")
    )
    if script.is_file():
        subprocess.run([str(script), payload_file], check=True)


def format_message(pack) -> str:
    lines = [f"Daily English Practice — {pack.date_label}", "", "5 new words"]
    for idx, word in enumerate(pack.words, start=1):
        lines.append(f"{idx}. {word['term']} — {word['meaning']}")
        lines.append(f"   Example: {word['example']}")

    lines.extend(["", "5 American phrases / slang"])
    for idx, phrase in enumerate(pack.phrases, start=1):
        lines.append(f"{idx}. {phrase['term']} — {phrase['meaning']}")
        lines.append(f"   Example: {phrase['example']}")

    return "\n".join(lines)


def load_payload(payload_file: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    payload = json.loads(Path(payload_file).read_text())
    return payload["words"], payload["phrases"]


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-message")
    build_parser.add_argument("--payload-file", required=True)

    send_parser = subparsers.add_parser("send-curated")
    send_parser.add_argument("--payload-file", required=True)
    send_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    state = load_state()
    words, phrases = load_payload(args.payload_file)
    pack = build_daily_pack(words, phrases, state)
    message = format_message(pack)

    if args.command == "build-message" or args.dry_run:
        print(message)
        return 0

    send(message)
    record_pack(pack, state)
    publish_feed(args.payload_file)
    print("Sent daily vocabulary message to Telegram and published the ChatGPT feed.")
    return 0

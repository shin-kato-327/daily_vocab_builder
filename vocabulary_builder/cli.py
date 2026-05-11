"""CLI for building and sending a daily vocabulary lesson."""

from __future__ import annotations

import argparse

from vocabulary_builder.content import PHRASES, WORDS
from vocabulary_builder.state import build_daily_pack
from vocabulary_builder.telegram import send


def format_message(pack) -> str:
    lines = [f"Daily English Practice — {pack.date_label}", "", "5 new words"]
    for idx, word in enumerate(pack.words, start=1):
        lines.append(f"{idx}. {word['term']} — {word['meaning']}")
        lines.append(f"   Example: {word['example']}")

    lines.extend(["", "5 American phrases / slang"])
    for idx, phrase in enumerate(pack.phrases, start=1):
        lines.append(f"{idx}. {phrase['term']} — {phrase['meaning']}")
        lines.append(f"   Example: {phrase['example']}")

    lines.extend(["", "5 review quizzes"])
    for quiz in pack.quizzes:
        lines.append(f"{quiz['number']}. What does \"{quiz['term']}\" mean?")
        for option_idx, option in enumerate(quiz["options"]):
            letter = "ABCD"[option_idx]
            lines.append(f"   {letter}. {option}")

    lines.extend(["", "Answers"])
    for quiz in pack.quizzes:
        lines.append(f"{quiz['number']}. {quiz['answer']} — {quiz['meaning']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build-message")
    send_parser = subparsers.add_parser("send-daily")
    send_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "build-message" or args.dry_run:
        pack = build_daily_pack(WORDS, PHRASES, persist=False)
        message = format_message(pack)
        print(message)
        return 0

    pack = build_daily_pack(WORDS, PHRASES)
    message = format_message(pack)
    send(message)
    print("Sent daily vocabulary message to Telegram.")
    return 0

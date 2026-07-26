#!/usr/bin/env python3
"""Build the public index of archived ChatGPT vocabulary payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    feed_dir = Path(sys.argv[1])
    archive_dir = feed_dir / "archive"
    entries = []

    for path in sorted(archive_dir.glob("*.json"), reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries.append(
            {
                "file": f"archive/{path.name}",
                "words": len(payload.get("words", [])),
                "phrases": len(payload.get("phrases", [])),
            }
        )

    index = {
        "latest": "latest.json",
        "archive_count": len(entries),
        "archives": entries,
    }
    (feed_dir / "history.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

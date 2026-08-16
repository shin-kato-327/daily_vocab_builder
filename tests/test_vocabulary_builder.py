from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from vocabulary_builder.cli import format_message, load_payload, publish_feed
from vocabulary_builder.state import DailyPack, build_daily_pack, load_state, record_pack


class VocabularyBuilderTests(unittest.TestCase):
    def test_build_daily_pack_counts(self) -> None:
        state = load_state(Path("/tmp/does-not-exist.json"))
        words = [
            {"term": f"word-{idx}", "meaning": f"meaning-{idx}", "example": f"example-{idx}"}
            for idx in range(1, 6)
        ]
        phrases = [
            {"term": f"phrase {idx}", "meaning": f"phrase meaning {idx}", "example": f"phrase example {idx}"}
            for idx in range(1, 6)
        ]
        pack = build_daily_pack(words, phrases, state, when=date(2026, 5, 10))
        self.assertEqual(len(pack.words), 5)
        self.assertEqual(len(pack.phrases), 5)
        self.assertEqual(len(pack.quizzes), 5)

    def test_format_message_contains_sections(self) -> None:
        pack = DailyPack(
            words=[
                {"term": "lucid", "meaning": "very clear", "example": "That was a lucid answer."}
            ] * 5,
            phrases=[
                {
                    "term": "shoot me a text",
                    "meaning": "send me a text message",
                    "example": "Shoot me a text later.",
                }
            ] * 5,
            quizzes=[
                {
                    "number": 1,
                    "term": "shoot me a text",
                    "options": ["send me a text message", "go to sleep", "drive fast", "tell a joke"],
                    "answer": "A",
                    "meaning": "send me a text message",
                }
            ] * 5,
            date_label="2026-05-10",
        )
        message = format_message(pack)
        self.assertIn("5 new words", message)
        self.assertIn("5 American phrases / slang", message)
        self.assertNotIn("review quizzes", message)
        self.assertNotIn("Answers", message)

    def test_record_pack_persists_sent_history(self) -> None:
        with TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state = load_state(state_path)
            pack = DailyPack(
                words=[
                    {"term": "lucid", "meaning": "very clear", "example": "That was a lucid answer."}
                ] * 5,
                phrases=[
                    {
                        "term": "shoot me a text",
                        "meaning": "send me a text message",
                        "example": "Shoot me a text later.",
                    }
                ] * 5,
                quizzes=[],
                date_label="2026-05-10",
            )
            record_pack(pack, state, state_path=state_path)
            saved = load_state(state_path)
            self.assertEqual(saved["generation_count"], 1)
            self.assertEqual(len(saved["sent_words"]), 5)
            self.assertEqual(len(saved["sent_phrases"]), 5)

    def test_load_payload_reads_words_and_phrases(self) -> None:
        with TemporaryDirectory() as tmpdir:
            payload_path = Path(tmpdir) / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "words": [{"term": "lucid", "meaning": "clear", "example": "A lucid note."}],
                        "phrases": [{"term": "my bad", "meaning": "my mistake", "example": "My bad."}],
                    }
                )
            )
            words, phrases = load_payload(str(payload_path))
            self.assertEqual(words[0]["term"], "lucid")
            self.assertEqual(phrases[0]["term"], "my bad")

    def test_publish_feed_runs_configured_publisher(self) -> None:
        with TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "publisher.sh"
            script.write_text("#!/bin/sh\n")
            payload = Path(tmpdir) / "payload.json"
            payload.write_text("{}")
            with patch.dict("os.environ", {"VOCAB_FEED_PUBLISHER": str(script)}):
                with patch("vocabulary_builder.cli.subprocess.run") as run:
                    publish_feed(str(payload))
            run.assert_called_once_with([str(script), str(payload)], check=True)


if __name__ == "__main__":
    unittest.main()

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from vocabulary_builder.cli import format_message
from vocabulary_builder.content import PHRASES, WORDS
from vocabulary_builder.state import DailyPack, build_daily_pack


class VocabularyBuilderTests(unittest.TestCase):
    def test_build_daily_pack_counts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            pack = build_daily_pack(
                WORDS, PHRASES, when=date(2026, 5, 10), state_path=state_path
            )
            self.assertEqual(len(pack.words), 5)
            self.assertEqual(len(pack.phrases), 5)
            self.assertEqual(len(pack.quizzes), 5)

    def test_format_message_contains_sections(self) -> None:
        pack = DailyPack(
            words=WORDS[:5],
            phrases=PHRASES[:5],
            quizzes=[
                {
                    "number": 1,
                    "term": "hit the books",
                    "options": ["to study seriously", "to sleep", "to argue", "to drive"],
                    "answer": "A",
                    "meaning": "to study seriously",
                }
            ] * 5,
            date_label="2026-05-10",
        )
        message = format_message(pack)
        self.assertIn("5 new words", message)
        self.assertIn("5 American phrases / slang", message)
        self.assertIn("5 review quizzes", message)


if __name__ == "__main__":
    unittest.main()

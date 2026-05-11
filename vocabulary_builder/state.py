"""State management for sent-history and phrase review."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


STATE_PATH = Path(".vocabulary_state.json")


@dataclass
class DailyPack:
    words: list[dict]
    phrases: list[dict]
    quizzes: list[dict]
    date_label: str


def load_state(state_path: Path = STATE_PATH) -> dict:
    if not state_path.exists():
        return {
            "sent_words": [],
            "sent_phrases": [],
            "generation_count": 0,
        }
    return json.loads(state_path.read_text())


def save_state(state: dict, state_path: Path = STATE_PATH) -> None:
    state_path.write_text(json.dumps(state, indent=2))


def normalize_term(term: str) -> str:
    cleaned = term.strip().lower().replace("’", "'")
    return " ".join(cleaned.split())


def get_used_terms(state: dict, key: str) -> set[str]:
    return {normalize_term(item["term"]) for item in state.get(key, [])}


def get_recent_terms(state: dict, key: str, limit: int = 200) -> list[str]:
    return [item["term"] for item in state.get(key, [])[-limit:]]


def validate_generated_items(
    items: list[dict[str, str]], used_terms: set[str], label: str, expected_count: int = 5
) -> None:
    if len(items) != expected_count:
        raise ValueError(f"expected {expected_count} {label}, got {len(items)}")

    seen_in_batch = set()
    for item in items:
        if sorted(item.keys()) != ["example", "meaning", "term"]:
            raise ValueError(f"{label} items must contain exactly term, meaning, example")
        if not item["term"].strip() or not item["meaning"].strip() or not item["example"].strip():
            raise ValueError(f"{label} items must not be blank")

        normalized = normalize_term(item["term"])
        if normalized in seen_in_batch:
            raise ValueError(f"duplicate {label} in the same batch: {item['term']}")
        if normalized in used_terms:
            raise ValueError(f"repeated {label} from history: {item['term']}")
        seen_in_batch.add(normalized)


def build_daily_pack(
    words: list[dict[str, str]],
    phrases: list[dict[str, str]],
    state: dict[str, Any],
    when: date | None = None,
) -> DailyPack:
    today = when or date.today()
    rng = random.Random(f"{today.isoformat()}::{state.get('generation_count', 0)}")
    validate_generated_items(words, get_used_terms(state, "sent_words"), "words")
    validate_generated_items(phrases, get_used_terms(state, "sent_phrases"), "phrases")
    quizzes = build_quizzes(state.get("sent_phrases", []), phrases, rng)
    return DailyPack(
        words=words,
        phrases=phrases,
        quizzes=quizzes,
        date_label=today.isoformat(),
    )


def build_quizzes(
    sent_phrases: list[dict[str, str]], current_phrases: list[dict[str, str]], rng: random.Random
) -> list[dict]:
    recent_history = sent_phrases[-20:]
    review_pool = _dedupe_phrase_entries(recent_history + current_phrases)
    review_terms = review_pool[-5:]
    meaning_pool = [item["meaning"] for item in _dedupe_phrase_entries(sent_phrases + current_phrases)]
    quizzes = []
    for idx, phrase in enumerate(review_terms, start=1):
        correct = phrase["meaning"]
        distractors = [meaning for meaning in meaning_pool if meaning != correct]
        options = _pick_options(correct, distractors, rng)
        rng.shuffle(options)
        answer = "ABCD"[options.index(correct)]
        quizzes.append(
            {
                "number": idx,
                "term": phrase["term"],
                "options": options,
                "answer": answer,
                "meaning": correct,
            }
        )
    return quizzes


def record_pack(pack: DailyPack, state: dict[str, Any], state_path: Path = STATE_PATH) -> None:
    state.setdefault("sent_words", [])
    state.setdefault("sent_phrases", [])
    state.setdefault("generation_count", 0)

    for word in pack.words:
        state["sent_words"].append({**word, "sent_at": pack.date_label})
    for phrase in pack.phrases:
        state["sent_phrases"].append({**phrase, "sent_at": pack.date_label})

    state["generation_count"] += 1
    save_state(state, state_path)


def _dedupe_phrase_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    deduped = []
    for entry in entries:
        normalized = normalize_term(entry["term"])
        if normalized in seen:
            continue
        deduped.append(entry)
        seen.add(normalized)
    return deduped


def _pick_options(correct: str, distractors: list[str], rng: random.Random) -> list[str]:
    unique_distractors = []
    seen = set()
    for distractor in distractors:
        if distractor not in seen:
            unique_distractors.append(distractor)
            seen.add(distractor)

    filler = [
        "to become extremely expensive very quickly",
        "to avoid making a clear decision",
        "to speak in an overly formal way",
        "to leave without saying anything",
        "to agree only because of social pressure",
    ]
    for item in filler:
        if item != correct and item not in seen:
            unique_distractors.append(item)
            seen.add(item)

    return rng.sample(unique_distractors, 3) + [correct]

"""State management for daily rotation and review history."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path


STATE_PATH = Path(".vocabulary_state.json")


@dataclass
class DailyPack:
    words: list[dict]
    phrases: list[dict]
    quizzes: list[dict]
    date_label: str


def load_state(state_path: Path = STATE_PATH) -> dict:
    if not state_path.exists():
        return {"used_words": [], "used_phrases": [], "phrase_history": [], "cycles": 0}
    return json.loads(state_path.read_text())


def save_state(state: dict, state_path: Path = STATE_PATH) -> None:
    state_path.write_text(json.dumps(state, indent=2))


def _pick_entries(entries: list[dict], used_indices: list[int], count: int,
                  rng: random.Random) -> tuple[list[dict], list[int], bool]:
    remaining = [idx for idx in range(len(entries)) if idx not in used_indices]
    cycled = False
    if len(remaining) < count:
        used_indices = []
        remaining = list(range(len(entries)))
        cycled = True
    chosen_indices = rng.sample(remaining, count)
    chosen = [entries[idx] for idx in chosen_indices]
    return chosen, used_indices + chosen_indices, cycled


def build_daily_pack(words: list[dict], phrases: list[dict], when: date | None = None,
                     persist: bool = True, state_path: Path = STATE_PATH) -> DailyPack:
    today = when or date.today()
    state = load_state(state_path)
    rng = random.Random(today.isoformat())

    day_words, used_words, words_cycled = _pick_entries(
        words, state["used_words"], 5, rng
    )
    day_phrases, used_phrases, phrases_cycled = _pick_entries(
        phrases, state["used_phrases"], 5, rng
    )

    state["used_words"] = used_words
    state["used_phrases"] = used_phrases
    if words_cycled or phrases_cycled:
        state["cycles"] += 1

    for phrase in day_phrases:
        state["phrase_history"].append(phrase["term"])
    state["phrase_history"] = state["phrase_history"][-20:]

    quizzes = build_quizzes(phrases, state["phrase_history"], rng)
    if persist:
        save_state(state, state_path)
    return DailyPack(
        words=day_words,
        phrases=day_phrases,
        quizzes=quizzes,
        date_label=today.isoformat(),
    )


def build_quizzes(phrases: list[dict], history_terms: list[str], rng: random.Random) -> list[dict]:
    phrase_map = {item["term"]: item for item in phrases}
    review_terms = [term for term in history_terms if term in phrase_map]
    if len(review_terms) < 5:
        extras = [item["term"] for item in phrases if item["term"] not in review_terms]
        review_terms.extend(extras[: 5 - len(review_terms)])
    review_terms = review_terms[-5:]

    all_meanings = [item["meaning"] for item in phrases]
    quizzes = []
    for idx, term in enumerate(review_terms, start=1):
        correct = phrase_map[term]["meaning"]
        distractors = [meaning for meaning in all_meanings if meaning != correct]
        options = rng.sample(distractors, 3) + [correct]
        rng.shuffle(options)
        answer = "ABCD"[options.index(correct)]
        quizzes.append(
            {
                "number": idx,
                "term": term,
                "options": options,
                "answer": answer,
                "meaning": correct,
            }
        )
    return quizzes

# Vocabulary Builder

Send yourself a daily Telegram lesson with:

- 5 new English words
- 5 American phrases / slang expressions
- 5 review quizzes about phrase meanings

## Setup

1. Copy `.env.example` to `.env`
2. Fill in `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. Create a payload JSON file with `words` and `phrases`
4. Test locally:

```bash
cd /Users/skat/workspace/vocabulary_builder
python3 -m vocabulary_builder build-message --payload-file sample.json
python3 -m vocabulary_builder send-curated --payload-file sample.json --dry-run
python3 -m vocabulary_builder send-curated --payload-file sample.json
```

## Payload format

```json
{
  "words": [
    {"term": "lucid", "meaning": "very clear and easy to understand", "example": "Her explanation was lucid and concise."}
  ],
  "phrases": [
    {"term": "shoot me a text", "meaning": "send me a text message", "example": "Shoot me a text when you get there."}
  ]
}
```

## Daily automation

The intended setup is:

- Codex automation generates a fresh payload locally using your ChatGPT/Codex subscription.
- This project sends that curated payload to Telegram and records sent history in `.vocabulary_state.json`.
- The helper script `scripts/send_payload_to_remote.sh` copies a generated payload to the remote server and triggers `send-curated` there, so the remote host stays the source of truth for message delivery and history.

## How freshness works

- The app stores every previously sent word and phrase in `.vocabulary_state.json`.
- Incoming payloads are rejected if any word or phrase has already been sent before.
- Phrase quizzes are built from recent sent phrases, so review can repeat even though new lesson items do not.

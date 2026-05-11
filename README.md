# Vocabulary Builder

Send yourself a daily Telegram lesson with:

- 5 new English words
- 5 American phrases / slang expressions
- 5 review quizzes about phrase meanings

## Setup

1. Copy `.env.example` to `.env`
2. Fill in `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. Test locally:

```bash
cd /Users/skat/workspace/vocabulary_builder
python3 -m vocabulary_builder build-message
python3 -m vocabulary_builder send-daily --dry-run
python3 -m vocabulary_builder send-daily
```

## Daily automation

Run this command once per day:

```bash
cd /Users/skat/workspace/vocabulary_builder
python3 -m vocabulary_builder send-daily
```

The app stores rotation history in `.vocabulary_state.json` so words and phrases do not repeat until the bank cycles.

# ChatGPT vocabulary feed

`latest.json` contains the most recent vocabulary payload successfully delivered
to Telegram. Every delivered list is also retained in `archive/`, and
`history.json` provides a machine-readable archive index.

Use this stable raw URL in ChatGPT:

```text
https://raw.githubusercontent.com/shin-kato-327/daily_vocab_builder/main/chatgpt_feed/latest.json
```

Suggested prompt:

```text
Retrieve this JSON file and use it as my latest vocabulary list:
https://raw.githubusercontent.com/shin-kato-327/daily_vocab_builder/main/chatgpt_feed/latest.json
```

For periodic memory review:

```text
Read the archive index below, choose vocabulary from several older files, and
test my memory without showing the answers first:
https://raw.githubusercontent.com/shin-kato-327/daily_vocab_builder/main/chatgpt_feed/history.json
```

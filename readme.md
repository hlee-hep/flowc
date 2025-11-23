# flowc

flowc is a lightweight automation system for personal productivity routines.
It connects Git logs, Notion, Telegram, Email, and arXiv, and uses GPT models
to summarize or rewrite content.

## Features
- Summarize Git commits
- Rewrite daily logs and TODOs
- Generate arXiv digests (GPT-5.1)
- Send Telegram / Email reports
- Update Notion daily pages
- Modular Flows (dawn / morning / evening)

## Structure
- `flows/` — Automations (MorningFlow, EveningFlow, DawnFlow)
- `services/` and `connectors/` - External integrations (Git, Notion, Telegram, Email, arXiv)
- `ai/` — OpenAI wrapper, prompt templates, summarization helpers
- `config.py` — API keys and environment settings

## How It Works
Services gather raw data.  
AI transforms text using GPT via `AI.ask()`.  
Prompts are centrally managed in `PromptManager`.

## Status
Work in progress. Adding more flows and automation soon.

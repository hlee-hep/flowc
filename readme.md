# flowc - Personal Automation Flow Engine

`flowc` is a lightweight automation system that generates daily digests from Git commits, arXiv papers, InspireHEP, Notion logs, Telegram, and Email.  
It provides a simple, modular structure for building scheduled “morning” and “evening” workflows powered by OpenAI models.

---

## Features

- **Git commit summarization**  
  Collects recent commits and produces compact or detailed summaries.

- **Daily paper highlights**  
  - **Morning:** Fetches top-cited or trending papers from **InspireHEP** and summarizes them via AI.  
  - **Evening:** Retrieves the latest papers from **arXiv** and generates concise or multi-sentence digests.

- **Notion daily log integration**  
  Converts raw daily notes into clean, coherent summaries.

- **Telegram & Email reporting**  
  Sends short Telegram digests and full HTML reports via email.

- **Caching & retrying**  
  Automatic TTL-based caching and retry mechanisms reduce API usage and noise.

- **Modular service-based design**  
  Easy to extend and customize with additional services or flows.

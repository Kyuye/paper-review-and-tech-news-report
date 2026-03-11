# Publisher automation

This directory contains the automation scripts used by GitHub Actions to:

1) Crawl trend/news and paper candidates
2) Generate candidate-pack Markdown for manual writing
3) Generate GitBook template files (KO + EN)
4) Create a draft PR
5) Send a preview notification (Discord webhook)

## Workflows

- `/.github/workflows/daily_draft.yml`
  - Runs **weekdays 18:00 Asia/Seoul (09:00 UTC)**
  - Generates candidate packs and opens/updates a PR on `draft/YYYY-MM-DD-kind`
  - Sends Discord notification with the PR link

## Required GitHub Secrets

### Discord (preview notifications)
- `DISCORD_WEBHOOK_URL` (Discord channel webhook URL)

Notes:
- This workflow does not use OpenAI API or LinkedIn API.
- You review the candidate pack in Discord/PR, then use ChatGPT web manually and merge the PR to publish on GitBook.

## Config files (committed)

- `config/site.yaml`: base URL and lookback windows
- `config/topics.yaml`: 8-category taxonomy + keyword hints
- `config/sources.yaml`: RSS/Atom feeds for trends/news
- `config/paper_queries.yaml`: paper search queries (Europe PMC)

## Local run (optional)

```bash
cd tools/publisher

# Run as if it's Tue 18:00 KST:
RUN_DATETIME_OVERRIDE="2026-03-03T18:00:00+09:00" \
python3 -m tools.publisher.run_draft
```

Preview outputs are written under:
- `ko/`, `en/`
- `previews/`

## Safety / compliance

- Paper reviews are abstract/metadata-only.
- No paywalled content is copied.
- Final prose is written manually after reviewing the candidate pack.

## Discord webhook setup

1) Discord channel → Edit Channel → Integrations → Webhooks
2) Create webhook → Copy webhook URL
3) GitHub repo → Settings → Secrets and variables → Actions → New repository secret
   - Name: `DISCORD_WEBHOOK_URL`
   - Secret: (the webhook URL)

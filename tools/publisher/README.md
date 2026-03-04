# Publisher automation

This directory contains the automation scripts used by GitHub Actions to:

1) Generate GitBook-ready Markdown pages (KO + EN)
2) Generate an explanatory SVG for Tue/Thu paper reviews
3) Create a draft PR (preview)
4) Email a preview (PR link + LinkedIn draft text)
5) After PR merge, post to LinkedIn via LinkedIn API

## Workflows

- `/.github/workflows/daily_draft.yml`
  - Runs **weekdays 18:00 Asia/Seoul (09:00 UTC)**
  - Generates content and opens/updates a PR on `draft/YYYY-MM-DD-kind`
  - Sends preview email with the PR link
- `/.github/workflows/on_merge_linkedin.yml`
  - Runs when a PR is merged into `main`
  - Posts LinkedIn text from `previews/linkedin/YYYY-MM-DD_ko.txt` (default) using markers embedded in PR body
  - Comments on the PR with `Posted to LinkedIn: <id>` to prevent duplicate posts

## Required GitHub Secrets

### OpenAI (LLM)
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (example: `gpt-4.1-mini`)
- (optional) `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)

### Email (SMTP)
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `EMAIL_FROM`
- `EMAIL_TO`

### LinkedIn (personal account)
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_AUTHOR_URN` (example: `urn:li:person:...`)

Notes:
- Token lifetimes depend on LinkedIn app configuration. If posting fails with auth errors, refresh the token.
- The automation posts **only after PR merge**, so you always approve content before posting.

## Config files (committed)

- `config/site.yaml`: base URL, lookback windows, LinkedIn language defaults
- `config/topics.yaml`: 8-category taxonomy + keyword hints
- `config/sources.yaml`: RSS/Atom feeds for trends/news
- `config/paper_queries.yaml`: paper search queries (Europe PMC)

## Local run (optional)

```bash
cd tools/publisher

# Run as if it's Tue 18:00 KST:
RUN_DATETIME_OVERRIDE="2026-03-03T18:00:00+09:00" \
OPENAI_API_KEY="..." OPENAI_MODEL="..." \
python3 -m tools.publisher.run_draft
```

Preview outputs are written under:
- `ko/`, `en/`
- `assets/images/`
- `previews/`

## Safety / compliance

- Paper reviews are abstract/metadata-only.
- No paywalled content is copied.
- The SVG is author-generated (not reused from the paper).

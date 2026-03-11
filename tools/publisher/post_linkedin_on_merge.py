from __future__ import annotations

import os
import re
from pathlib import Path

from .github_api import (
    GitHubClient,
    create_issue_comment,
    get_pull_request,
    list_issue_comments,
)
from .linkedin_api import post_text
from .settings import load_site_config, repo_root


_MARKER_RE = re.compile(r"<!--\s*publisher:(?P<k>[a-zA-Z0-9_]+)=(?P<v>[^ ]+)\s*-->")


def _parse_markers(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _MARKER_RE.finditer(body or ""):
        out[m.group("k")] = m.group("v")
    return out


def main() -> int:
    gh_token = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
    if not gh_token:
        raise RuntimeError("Missing GITHUB_TOKEN (or GH_TOKEN)")
    owner = (os.getenv("GITHUB_REPOSITORY") or "").split("/")[0]
    repo = (os.getenv("GITHUB_REPOSITORY") or "").split("/")[1]
    pr_number = int(os.getenv("PR_NUMBER") or "0")
    if not owner or not repo or not pr_number:
        raise RuntimeError("Missing GITHUB_REPOSITORY or PR_NUMBER")

    access_token = (os.getenv("LINKEDIN_ACCESS_TOKEN") or "").strip()
    author_urn = (os.getenv("LINKEDIN_AUTHOR_URN") or "").strip()
    if not access_token or not author_urn:
        raise RuntimeError("Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN")

    gh = GitHubClient(token=gh_token)
    pr = get_pull_request(gh=gh, owner=owner, repo=repo, pull_number=pr_number)
    markers = _parse_markers(pr.get("body") or "")

    cfg = load_site_config()
    root = repo_root()

    # Dedupe: if already commented, skip.
    comments = list_issue_comments(gh=gh, owner=owner, repo=repo, issue_number=pr_number)
    if any("Posted to LinkedIn:" in (c.get("body") or "") for c in comments):
        return 0

    langs = cfg.linkedin_post_langs or ("ko",)
    posted_ids: list[str] = []
    for lang in langs:
        key = f"linkedin_{lang}"
        preview_path = markers.get(key, "")
        if not preview_path:
            continue
        p = root / preview_path
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8").strip()
        # Replace placeholder with GitBook URL if available.
        gitbook_key = f"gitbook_{lang}"
        if markers.get(gitbook_key):
            gitbook_url = f"{cfg.gitbook_base_url}/{markers[gitbook_key].replace('.md','')}"
            text = text.replace("{GITBOOK_URL}", gitbook_url)
        res = post_text(access_token=access_token, author_urn=author_urn, text=text)
        if res.ok and res.id:
            posted_ids.append(res.id)

    if posted_ids:
        create_issue_comment(
            gh=gh,
            owner=owner,
            repo=repo,
            issue_number=pr_number,
            body="Posted to LinkedIn: " + ", ".join(posted_ids),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


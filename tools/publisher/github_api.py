from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class GitHubClient:
    token: str
    api_base: str = "https://api.github.com"

    def get(self, path: str) -> dict:
        url = f"{self.api_base}{path}"
        req = Request(url, headers=self._headers())
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def post(self, path: str, payload: dict) -> dict:
        url = f"{self.api_base}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = Request(url, method="POST", data=body, headers=self._headers({"Content-Type": "application/json"}))
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace") or "{}")

    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if extra:
            h.update(extra)
        return h


def list_issue_comments(*, gh: GitHubClient, owner: str, repo: str, issue_number: int) -> list[dict]:
    return gh.get(f"/repos/{owner}/{repo}/issues/{issue_number}/comments")


def create_issue_comment(*, gh: GitHubClient, owner: str, repo: str, issue_number: int, body: str) -> dict:
    return gh.post(f"/repos/{owner}/{repo}/issues/{issue_number}/comments", {"body": body})


def get_pull_request(*, gh: GitHubClient, owner: str, repo: str, pull_number: int) -> dict:
    return gh.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")


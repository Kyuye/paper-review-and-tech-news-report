from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.publisher.news_collect import NewsItem
from tools.publisher.paper_collect import Paper
from tools.publisher.run_draft import main as run_draft_main
from tools.publisher.settings import SiteConfig, Topic


def _site_config() -> SiteConfig:
    return SiteConfig(
        gitbook_base_url="https://example.gitbook.io/site",
        timezone="Asia/Seoul",
        news_lookback_days=3,
        news_per_topic_max=2,
        paper_lookback_days=14,
        paper_deep_review_count=1,
        paper_recommend_count=3,
    )


def _topics() -> list[Topic]:
    return [
        Topic(
            slug="biomanufacturing",
            ko="바이오제조/스케일업",
            en="Biomanufacturing & Scale-up",
            priority=100,
            keywords=("biomanufacturing", "fermentation"),
        ),
        Topic(
            slug="biofoundry_ai",
            ko="바이오파운드리·자동화·AI",
            en="Biofoundry/Automation & AI",
            priority=90,
            keywords=("biofoundry", "automation"),
        ),
    ]


class TestManualWorkflow(unittest.TestCase):
    def test_run_draft_generates_trends_candidate_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            item = NewsItem(
                title="Biomanufacturing expansion",
                url="https://example.com/news",
                published_at=datetime.fromisoformat("2026-03-13T09:00:00+00:00"),
                source_name="Example Source",
                entity_type="media",
                summary="Biomanufacturing update",
                default_topics=("biomanufacturing",),
            )
            with patch("tools.publisher.run_draft.repo_root", return_value=root), \
                patch("tools.publisher.run_draft.load_site_config", return_value=_site_config()), \
                patch("tools.publisher.run_draft.load_topics", return_value=_topics()), \
                patch("tools.publisher.run_draft.load_sources", return_value=[]), \
                patch("tools.publisher.run_draft.collect_news", return_value=([item], [])), \
                patch("tools.publisher.run_draft.update_indexes", side_effect=lambda *_: None), \
                patch.dict(os.environ, {"RUN_DATETIME_OVERRIDE": "2026-03-13T18:00:00+09:00"}, clear=False):
                result = run_draft_main()

            self.assertEqual(result, 0)
            self.assertTrue((root / "previews" / "manual" / "2026-03-13-trends.md").exists())
            self.assertTrue((root / "ko" / "trends" / "2026-03-13.md").exists())
            self.assertTrue((root / "en" / "trends" / "2026-03-13.md").exists())
            self.assertTrue((root / "previews" / "notifications" / "latest.md").exists())

    def test_run_draft_generates_paper_review_candidate_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            papers = [
                Paper(
                    title="Synthetic biology platform paper",
                    abstract="A biofoundry automation platform for synthetic biology.",
                    doi="10.1000/example",
                    url="https://doi.org/10.1000/example",
                    published_date="2026-03-12",
                    venue="Example Journal",
                    year="2026",
                    authors="A. Author",
                    source="europepmc",
                ),
                Paper(
                    title="Recommended paper",
                    abstract="Secondary paper abstract.",
                    doi="10.1000/rec",
                    url="https://doi.org/10.1000/rec",
                    published_date="2026-03-11",
                    venue="Example Journal",
                    year="2026",
                    authors="B. Author",
                    source="europepmc",
                ),
            ]
            with patch("tools.publisher.run_draft.repo_root", return_value=root), \
                patch("tools.publisher.run_draft.load_site_config", return_value=_site_config()), \
                patch("tools.publisher.run_draft.load_topics", return_value=_topics()), \
                patch("tools.publisher.run_draft.load_paper_queries", return_value=[{"name": "x", "query": "x"}]), \
                patch("tools.publisher.run_draft.collect_papers", return_value=papers), \
                patch("tools.publisher.run_draft.update_indexes", side_effect=lambda *_: None), \
                patch.dict(os.environ, {"RUN_DATETIME_OVERRIDE": "2026-03-12T18:00:00+09:00"}, clear=False):
                result = run_draft_main()

            self.assertEqual(result, 0)
            self.assertTrue((root / "previews" / "manual" / "2026-03-12-paper-review.md").exists())
            self.assertTrue((root / "previews" / "notifications" / "latest.md").exists())
            self.assertTrue(any((root / "ko" / "paper-reviews").glob("2026-03-12-*.md")))
            self.assertTrue(any((root / "en" / "paper-reviews").glob("2026-03-12-*.md")))


if __name__ == "__main__":
    unittest.main()

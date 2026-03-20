from __future__ import annotations

import unittest
from unittest.mock import patch

from tools.publisher.paper_collect import collect_papers
from tools.publisher.settings import PaperJournal, PaperSearchConfig


def _config() -> PaperSearchConfig:
    return PaperSearchConfig(
        journals=(
            PaperJournal(name="Nature Biotechnology", group="nature"),
            PaperJournal(name="Cell", group="cell"),
        ),
        search_queries=("synthetic biology neuron",),
        synbio_keywords=("synthetic biology", "gene circuit", "reporter"),
        neural_keywords=("neural circuit", "neuron", "synapse"),
    )


class TestPaperCollect(unittest.TestCase):
    def test_collect_papers_filters_by_whitelist_and_keywords(self) -> None:
        payload = {
            "message": {
                "items": [
                    {
                        "DOI": "10.1000/good",
                        "title": ["Synthetic biology reporter for neural circuit activity"],
                        "abstract": "<jats:p>An engineered reporter for neuron and synapse recording.</jats:p>",
                        "container-title": ["Nature Biotechnology"],
                        "published-online": {"date-parts": [[2026, 3, 18]]},
                        "author": [{"given": "A", "family": "Author"}],
                        "URL": "https://doi.org/10.1000/good",
                    },
                    {
                        "DOI": "10.1000/badjournal",
                        "title": ["Synthetic biology reporter for neurons"],
                        "abstract": "<jats:p>Neuron reporter.</jats:p>",
                        "container-title": ["Frontiers in Neuroscience"],
                        "published-online": {"date-parts": [[2026, 3, 18]]},
                        "author": [{"given": "B", "family": "Author"}],
                        "URL": "https://doi.org/10.1000/badjournal",
                    },
                    {
                        "DOI": "10.1000/nonsynbio",
                        "title": ["Neural circuit atlas in mouse brain"],
                        "abstract": "<jats:p>Neuron and synapse mapping without engineering.</jats:p>",
                        "container-title": ["Cell"],
                        "published-online": {"date-parts": [[2026, 3, 17]]},
                        "author": [{"given": "C", "family": "Author"}],
                        "URL": "https://doi.org/10.1000/nonsynbio",
                    },
                ]
            }
        }

        with patch("tools.publisher.paper_collect._get_json", return_value=payload):
            papers = collect_papers(config=_config(), lookback_days=14)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].doi, "10.1000/good")
        self.assertEqual(papers[0].venue, "Nature Biotechnology")
        self.assertEqual(papers[0].source, "nature")
        self.assertIn("Matched neural keywords", papers[0].match_reason)
        self.assertIn("matched synbio keywords", papers[0].match_reason)


if __name__ == "__main__":
    unittest.main()

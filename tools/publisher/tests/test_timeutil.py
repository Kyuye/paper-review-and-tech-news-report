from __future__ import annotations

import unittest
from datetime import datetime

from tools.publisher.timeutil import draft_context


class TestTimeutil(unittest.TestCase):
    def test_draft_context_weekdays(self) -> None:
        # Tuesday -> paper_review
        ctx = draft_context(datetime.fromisoformat("2026-03-03T18:00:00+09:00"))
        self.assertIsNotNone(ctx)
        assert ctx is not None
        self.assertEqual(ctx.kind, "paper_review")

        # Wednesday -> trends
        ctx = draft_context(datetime.fromisoformat("2026-03-04T18:00:00+09:00"))
        self.assertIsNotNone(ctx)
        assert ctx is not None
        self.assertEqual(ctx.kind, "trends")

        # Sunday -> none
        ctx = draft_context(datetime.fromisoformat("2026-03-08T18:00:00+09:00"))
        self.assertIsNone(ctx)


if __name__ == "__main__":
    unittest.main()

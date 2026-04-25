from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from memory_core.marker_io import insert_between_markers


class MarkerIoTests(unittest.TestCase):
    def test_insert_between_markers_replaces_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "marker.md"
            path.write_text(
                "# Example\n\n## Entries\n<!-- MEMORY_CONTENT_START -->\nNo records yet.\n<!-- MEMORY_CONTENT_END -->\n",
                encoding="utf-8",
            )
            insert_between_markers(path, "### First Entry\n- ok: yes")
            text = path.read_text(encoding="utf-8")
            self.assertIn("### First Entry", text)
            self.assertNotIn("No records yet.", text)
            self.assertLess(text.index("<!-- MEMORY_CONTENT_START -->"), text.index("### First Entry"))
            self.assertLess(text.index("### First Entry"), text.index("<!-- MEMORY_CONTENT_END -->"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from memory_core import TurnContext, add_manual_memory, process_turn, rebuild_indexes

from tests.test_support import bootstrap_root


class MemoryRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self._temp_dir.name)
        bootstrap_root(self.root)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_short_term_routes_module_inspiration_to_sparks(self) -> None:
        result = add_manual_memory(
            self.root,
            content="Test spark",
            memory_type="short",
            module="inspiration",
        )
        self.assertEqual(result.event.memory_type, "short_term_memory")
        self.assertIn("03_Short_Term_Memory/sparks/", result.target_path)
        self.assertTrue((self.root / result.target_path).exists())
        short_index = (self.root / "03_Short_Term_Memory" / "short_index.md").read_text(encoding="utf-8")
        self.assertIn("| `sparks/` | Inspiration | 1 |", short_index)

    def test_short_term_unknown_subtype_falls_back_to_inbox(self) -> None:
        result = add_manual_memory(
            self.root,
            content="Sort this later",
            memory_type="short",
            subtype="mystery_bucket",
        )
        self.assertEqual(result.target_path, "03_Short_Term_Memory/inbox.md")
        inbox = (self.root / result.target_path).read_text(encoding="utf-8")
        self.assertIn("Sort this later", inbox)

    def test_project_research_routes_to_note_and_updates_indexes(self) -> None:
        result = add_manual_memory(
            self.root,
            content="Test research note",
            memory_type="project",
            project_name="Commorai Work Memory",
            module="research",
        )
        self.assertIn("/research/notes/", result.target_path)
        self.assertTrue((self.root / result.target_path).exists())
        research_index = next((self.root / "02_Project_Memory").glob("P_*/research/research_index.md"))
        memory_log = next((self.root / "02_Project_Memory").glob("P_*/memory_log.md"))
        self.assertIn("Test research note", research_index.read_text(encoding="utf-8"))
        self.assertIn("Test research note", memory_log.read_text(encoding="utf-8"))

    def test_base_routes_preferences_and_updates_base_index(self) -> None:
        result = add_manual_memory(
            self.root,
            content="Prefer structured output first",
            memory_type="base",
            field="preferences",
        )
        self.assertEqual(result.target_path, "01_Base_Memory/preferences.md")
        preferences = (self.root / result.target_path).read_text(encoding="utf-8")
        self.assertIn("Prefer structured output first", preferences)
        base_index = (self.root / "01_Base_Memory" / "base_index.md").read_text(encoding="utf-8")
        self.assertIn("| `preferences.md` | `preferences` | 1 |", base_index)

    def test_duplicate_write_is_skipped_and_logged(self) -> None:
        first = add_manual_memory(
            self.root,
            content="Deduplicate this",
            memory_type="short",
            module="inspiration",
        )
        second = add_manual_memory(
            self.root,
            content="Deduplicate this",
            memory_type="short",
            module="inspiration",
        )
        sparks = list((self.root / "03_Short_Term_Memory" / "sparks").glob("*.md"))
        self.assertEqual(len(sparks), 1)
        self.assertEqual(second.event.status, "duplicate_skipped")
        self.assertEqual(second.target_path, first.target_path)
        log_text = (self.root / "00_System" / "logs" / "memory_events.jsonl").read_text(encoding="utf-8")
        self.assertIn('"status": "duplicate_skipped"', log_text)

    def test_base_conflict_is_recorded(self) -> None:
        add_manual_memory(
            self.root,
            content="Prefer structured output first",
            memory_type="base",
            field="preferences",
            title="Team Output Preference",
        )
        second = add_manual_memory(
            self.root,
            content="Prefer loose exploratory output first",
            memory_type="base",
            field="preferences",
            title="Team Output Preference",
        )
        self.assertEqual(second.event.status, "conflict_recorded")
        conflicts = (self.root / "01_Base_Memory" / "conflicts.md").read_text(encoding="utf-8")
        self.assertIn("Conflict: Team Output Preference", conflicts)
        self.assertIn("Prefer loose exploratory output first", conflicts)

    def test_capture_turn_routes_conservatively_without_base_promotion(self) -> None:
        results = process_turn(
            TurnContext(
                session_id="s1",
                turn_id="t1",
                active_project="Commorai Work Memory",
                user_text="请记录这个项目的研究要点",
                assistant_text="我会记录到正确位置",
            ),
            self.root,
        )
        self.assertTrue(results)
        self.assertTrue(any(item.event.memory_type in {"project_memory", "short_term_memory"} for item in results))
        self.assertFalse(any(item.event.memory_type == "base_memory" for item in results))

    def test_rebuild_indexes_refreshes_counts(self) -> None:
        add_manual_memory(
            self.root,
            content="Prefer structured output first",
            memory_type="base",
            field="preferences",
        )
        add_manual_memory(
            self.root,
            content="Project research note",
            memory_type="project",
            project_name="Commorai Work Memory",
            module="research",
        )
        add_manual_memory(
            self.root,
            content="Idea bucket",
            memory_type="short",
            module="inspiration",
        )
        (self.root / "01_Base_Memory" / "base_index.md").write_text("stale\n", encoding="utf-8")
        (self.root / "03_Short_Term_Memory" / "short_index.md").write_text("stale\n", encoding="utf-8")
        (self.root / "02_Project_Memory" / "project_index.md").write_text("stale\n", encoding="utf-8")
        rebuild_indexes(self.root)
        self.assertIn("preferences", (self.root / "01_Base_Memory" / "base_index.md").read_text(encoding="utf-8"))
        self.assertIn("sparks/", (self.root / "03_Short_Term_Memory" / "short_index.md").read_text(encoding="utf-8"))
        self.assertIn("Commorai Work Memory", (self.root / "02_Project_Memory" / "project_index.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

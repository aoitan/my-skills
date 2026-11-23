from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "garden_search.py"
SPEC = importlib.util.spec_from_file_location("garden_search", SCRIPT)
assert SPEC and SPEC.loader
garden_search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(garden_search)


class RootPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.explicit_root = self.base / "explicit"
        self.environment_root = self.base / "environment"
        self.config_root = self.base / "configured"
        for root in (self.explicit_root, self.environment_root, self.config_root):
            root.mkdir()
        self.config = self.base / "config.json"
        self.config.write_text(
            json.dumps({"garden_root": str(self.config_root)}), encoding="utf-8"
        )

    def test_explicit_root_takes_precedence(self) -> None:
        with patch.dict(os.environ, {"GARDEN_ROOT": str(self.environment_root)}):
            result = garden_search.root_path(str(self.explicit_root), str(self.config))

        self.assertEqual(result, self.explicit_root.resolve())

    def test_environment_root_takes_precedence_over_config(self) -> None:
        with patch.dict(os.environ, {"GARDEN_ROOT": str(self.environment_root)}):
            result = garden_search.root_path(None, str(self.config))

        self.assertEqual(result, self.environment_root.resolve())

    def test_config_supplies_root(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = garden_search.root_path(None, str(self.config))

        self.assertEqual(result, self.config_root.resolve())

    def test_missing_configuration_has_no_machine_specific_fallback(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(garden_search.GardenError, "not configured"):
                garden_search.root_path(None, str(self.base / "missing.json"))


class BacklinksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name).resolve()
        self.write("projects/kelpie/index.md", "title: Kelpie\naliases:\n  - whistle-dog\n")
        self.write("projects/rlm/index.md", "title: RLM\n")
        self.write("projects/kelpie/graph-loop.md", 'title: "Kelpieを実行基盤として捉える"\n')

    def write(self, path: str, front_matter: str, body: str = "") -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"---\n{front_matter}---\n\n{body}\n", encoding="utf-8")

    def link(self, path: str, target: str) -> None:
        self.write(path, f"title: source {path}\n", f"[[{target}]]")

    def backlinks(self, query: str) -> dict:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            garden_search.command_backlinks(self.root, query)
        return json.loads(output.getvalue())

    def paths(self, query: str) -> list[str]:
        return [node["path"] for node in self.backlinks(query)["nodes"]]

    def test_index_query_excludes_links_to_other_indexes(self) -> None:
        self.link("a.md", "projects/kelpie/index")
        self.link("b.md", "projects/rlm/index")
        self.assertEqual(self.paths("projects/kelpie/index.md"), ["a.md"])

    def test_path_title_and_filename_queries_agree(self) -> None:
        self.link("by-path.md", "projects/kelpie/graph-loop|label")
        self.link("by-title.md", "Kelpieを実行基盤として捉える")
        self.link("by-filename.md", "graph-loop")
        expected = ["by-filename.md", "by-path.md", "by-title.md"]
        for query in ("projects/kelpie/graph-loop.md", "graph-loop", "Kelpieを実行基盤として捉える"):
            with self.subTest(query=query):
                self.assertEqual(self.paths(query), expected)

    def test_directory_alias_and_partial_path_reach_index(self) -> None:
        self.link("a.md", "projects/kelpie/")
        self.link("b.md", "whistle-dog")
        self.link("c.md", "kelpie/index")
        self.link("d.md", "kelpie")
        self.assertEqual(self.paths("projects/kelpie/index"), ["a.md", "b.md", "c.md", "d.md"])

    def test_relative_and_table_escaped_links(self) -> None:
        self.link("projects/rlm/note.md", "../kelpie/graph-loop.md")
        self.link("table.md", "projects/kelpie/graph-loop\\|label")
        self.assertEqual(
            self.paths("projects/kelpie/graph-loop"), ["projects/rlm/note.md", "table.md"]
        )

    def test_exact_path_wins_over_title_and_filename(self) -> None:
        self.write("other/unrelated.md", "title: projects/kelpie/graph-loop\n")
        self.write("other/graph-loop.md", "title: other loop\n")
        self.link("a.md", "projects/kelpie/graph-loop")
        self.assertEqual(self.paths("other/unrelated"), [])
        self.assertEqual(self.paths("other/graph-loop"), [])

    def test_link_to_moved_note_is_found_and_labelled(self) -> None:
        self.link("a.md", "inbox/graph-loop")
        node = self.backlinks("projects/kelpie/graph-loop")["nodes"][0]
        self.assertEqual(node["path"], "a.md")
        self.assertEqual(node["matching_links"][0]["resolution"], "moved-filename")

    def test_ambiguous_filename_is_labelled(self) -> None:
        self.write("other/graph-loop.md", "title: other loop\n")
        self.link("a.md", "graph-loop")
        node = self.backlinks("projects/kelpie/graph-loop")["nodes"][0]
        self.assertEqual(node["matching_links"][0]["candidates"], 2)

    def test_stale_index_link_does_not_match_other_indexes(self) -> None:
        self.link("a.md", "projects/removed/index")
        self.assertEqual(self.paths("projects/kelpie/index"), [])

    def test_unresolved_query_finds_dangling_links(self) -> None:
        self.link("a.md", "まだないノート")
        result = self.backlinks("まだないノート")
        self.assertEqual(result["resolved"], [])
        self.assertEqual([node["path"] for node in result["nodes"]], ["a.md"])


if __name__ == "__main__":
    unittest.main()

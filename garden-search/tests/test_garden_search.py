from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()

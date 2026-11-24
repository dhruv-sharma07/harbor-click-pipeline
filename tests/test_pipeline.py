"""
Unit Tests for Harbor Task Generation Pipeline
Verifies Harbor v0.25.x specification compliance and generation logic.
"""

import unittest
import tempfile
from pathlib import Path
from harbor_taskgen.config import HARBOR_SCHEMA_VERSION, DEFAULT_BASELINE_COMMIT
from harbor_taskgen.git_miner import ClickTaskCatalog
from harbor_taskgen.generator import TaskGenerator
from harbor_taskgen.linter import HarborLinter

class TestHarborPipeline(unittest.TestCase):
    def test_catalog_tasks_present(self):
        tasks = ClickTaskCatalog.get_all_tasks()
        self.assertGreaterEqual(len(tasks), 3)
        for t in tasks:
            self.assertTrue(t.metadata.name.startswith("click-"))
            self.assertEqual(t.metadata.baseline_commit, DEFAULT_BASELINE_COMMIT)
            self.assertGreater(len(t.instruction), 100)
            self.assertGreater(len(t.solution_patch), 0)
            self.assertGreater(len(t.test_patch), 0)

    def test_task_generator_and_linter(self):
        tasks = ClickTaskCatalog.get_all_tasks()
        generator = TaskGenerator()
        linter = HarborLinter()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            for task in tasks:
                task_dir = generator.generate(task, tmp_path)
                
                # Check files exist
                self.assertTrue((task_dir / "task.toml").exists())
                self.assertTrue((task_dir / "instruction.md").exists())
                self.assertTrue((task_dir / "environment" / "Dockerfile").exists())
                self.assertTrue((task_dir / "solution" / "solve.sh").exists())
                self.assertTrue((task_dir / "tests" / "test.sh").exists())
                self.assertTrue((task_dir / "tests" / "test_verifier.py").exists())

                # Lint with Harbor v0.25 linter
                passed, errors, warnings = linter.lint_task(task_dir)
                self.assertTrue(passed, f"Linter failed on {task.metadata.name}: {errors}")
                self.assertEqual(len(errors), 0)

    def test_linter_detects_missing_file(self):
        generator = TaskGenerator()
        linter = HarborLinter()
        task = ClickTaskCatalog.get_all_tasks()[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            task_dir = generator.generate(task, tmp_path)
            
            # Remove task.toml
            (task_dir / "task.toml").unlink()

            passed, errors, warnings = linter.lint_task(task_dir)
            self.assertFalse(passed)
            self.assertTrue(any("Missing required Harbor file: 'task.toml'" in err for err in errors))

if __name__ == "__main__":
    unittest.main()

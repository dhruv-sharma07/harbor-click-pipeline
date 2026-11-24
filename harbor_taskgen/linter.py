"""
Harbor v0.25.x Task Linter
Validates containerized task packages against Harbor standardized architecture.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

class HarborLinter:
    REQUIRED_FILES = [
        "task.toml",
        "instruction.md",
        "environment/Dockerfile",
        "solution/solve.sh",
        "tests/test.sh"
    ]

    REQUIRED_TOML_SECTIONS = [
        "schema_version",
        "[metadata]",
        "[agent]",
        "[verifier]",
        "[environment]"
    ]

    def lint_task(self, task_dir: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Runs full Harbor v0.25.x verification against a task directory.
        Returns: (passed, errors, warnings)
        """
        errors = []
        warnings = []
        task_dir = Path(task_dir)

        if not task_dir.exists() or not task_dir.is_dir():
            return False, [f"Directory does not exist: {task_dir}"], []

        # 1. Check required files
        for rel_path in self.REQUIRED_FILES:
            target = task_dir / rel_path
            if not target.exists():
                errors.append(f"Missing required Harbor file: '{rel_path}'")
            elif target.stat().st_size == 0:
                errors.append(f"Required Harbor file is empty: '{rel_path}'")

        # 2. Check task.toml structure and schema
        toml_path = task_dir / "task.toml"
        if toml_path.exists():
            with open(toml_path, "r", encoding="utf-8") as f:
                toml_text = f.read()

            for sec in self.REQUIRED_TOML_SECTIONS:
                if sec not in toml_text:
                    errors.append(f"task.toml missing required key/section: '{sec}'")

            if 'schema_version = "0.25' not in toml_text:
                warnings.append("task.toml does not explicitly specify Harbor schema_version 0.25.x")

        # 3. Check instruction.md
        inst_path = task_dir / "instruction.md"
        if inst_path.exists():
            with open(inst_path, "r", encoding="utf-8") as f:
                inst_text = f.read()
            if len(inst_text.strip()) < 50:
                warnings.append("instruction.md is unusually short (< 50 characters)")

        # 4. Check test.sh reward output contract
        test_sh_path = task_dir / "tests" / "test.sh"
        if test_sh_path.exists():
            with open(test_sh_path, "r", encoding="utf-8") as f:
                test_sh_text = f.read()
            if "/logs/verifier/reward" not in test_sh_text:
                errors.append("tests/test.sh violates Harbor contract: does not write to /logs/verifier/reward.txt or .json")

        # 5. Check environment/Dockerfile
        dockerfile_path = task_dir / "environment" / "Dockerfile"
        if dockerfile_path.exists():
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                df_text = f.read()
            if "FROM " not in df_text:
                errors.append("environment/Dockerfile does not contain a valid FROM directive")
            if "pallets/click" not in df_text and "click" not in df_text:
                warnings.append("environment/Dockerfile does not reference pallets/click repository")

        passed = len(errors) == 0
        return passed, errors, warnings

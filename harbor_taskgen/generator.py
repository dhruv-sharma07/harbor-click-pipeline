"""
Harbor Task Package Generator
Synthesizes compliant Harbor v0.25.x task structures for pallets/click.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from .config import TaskDefinition, HARBOR_SCHEMA_VERSION

class TaskGenerator:
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        template_path = self.templates_dir / template_name
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Simple template substitution
        for key, val in context.items():
            if isinstance(val, list):
                val_str = json.dumps(val)
            elif isinstance(val, bool):
                val_str = "true" if val else "false"
            else:
                val_str = str(val)
            content = content.replace(f"{{{{ {key} }}}}", val_str)
            content = content.replace(f"{{{{{key}}}}}", val_str)
            
        # Clean up any leftover conditionals if any
        lines = []
        for line in content.splitlines():
            if "{%" in line and "%}" in line:
                # Handle simple {% if key %}line{% endif %}
                import re
                m = re.search(r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}", line)
                if m:
                    cond_var, inner = m.groups()
                    if context.get(cond_var):
                        line = re.sub(r"{%\s*if\s+\w+\s*%}(.*?){%\s*endif\s*%}", r"\1", line)
                    else:
                        line = ""
            if line.strip() != "":
                lines.append(line)
        return "\n".join(lines) + "\n"

    def generate(self, task: TaskDefinition, output_dir: Path) -> Path:
        """
        Generate complete containerized task package conforming to Harbor v0.25.x.
        """
        task_dir = output_dir / task.metadata.name
        env_dir = task_dir / "environment"
        solution_dir = task_dir / "solution"
        tests_dir = task_dir / "tests"

        for d in [task_dir, env_dir, solution_dir, tests_dir]:
            d.mkdir(parents=True, exist_ok=True)

        context = {
            "schema_version": HARBOR_SCHEMA_VERSION,
            "name": task.metadata.name,
            "author": task.metadata.author,
            "difficulty": task.metadata.difficulty,
            "category": task.metadata.category,
            "tags": task.metadata.tags,
            "summary": task.metadata.summary,
            "baseline_commit": task.metadata.baseline_commit,
            "issue_id": task.metadata.issue_id,
            "agent_timeout_sec": task.agent_timeout_sec,
            "verifier_timeout_sec": task.verifier_timeout_sec,
            "os": task.env_config.os,
            "base_image": task.env_config.base_image,
            "cpus": task.env_config.cpus,
            "memory_mb": task.env_config.memory_mb,
            "storage_mb": task.env_config.storage_mb,
            "gpus": task.env_config.gpus,
            "instruction": task.instruction,
            "solution_patch": task.solution_patch,
        }

        # 1. Render task.toml
        task_toml_content = self._render_template("task.toml.jinja", context)
        with open(task_dir / "task.toml", "w", encoding="utf-8") as f:
            f.write(task_toml_content)

        # 2. Render instruction.md
        instruction_content = self._render_template("instruction.md.jinja", context)
        with open(task_dir / "instruction.md", "w", encoding="utf-8") as f:
            f.write(instruction_content)

        # 3. Render environment/Dockerfile
        dockerfile_content = self._render_template("Dockerfile.jinja", context)
        with open(env_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        # 4. Render solution/solve.sh
        solve_content = self._render_template("solve.sh.jinja", context)
        with open(solution_dir / "solve.sh", "w", encoding="utf-8", newline="\n") as f:
            f.write(solve_content)

        # 5. Render tests/test.sh
        test_sh_content = self._render_template("test.sh.jinja", context)
        with open(tests_dir / "test.sh", "w", encoding="utf-8", newline="\n") as f:
            f.write(test_sh_content)

        # 6. Write tests/test_verifier.py
        with open(tests_dir / "test_verifier.py", "w", encoding="utf-8") as f:
            f.write(task.test_patch)

        return task_dir

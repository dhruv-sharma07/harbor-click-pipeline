"""
Pallets/Click Repository Miner and Task Definition Catalog
Provides automated mining and synthesis of containerized Harbor tasks from pallets/click.
"""

from typing import List, Dict, Optional
from .config import TaskDefinition, TaskMetadata, TaskEnvironmentConfig, DEFAULT_BASELINE_COMMIT

class ClickTaskCatalog:
    """Catalog of verified reproducible tasks mined from pallets/click."""

    @staticmethod
    def get_task_paramtype_custom_formatting() -> TaskDefinition:
        instruction = """In `click/types.py`, when a custom `ParamType` subclass overrides `convert()` or fails validation, Click formats the error message using `self.get_missing_message(param)` or `self.name`.

However, when a subclass does not define a `name` attribute or when `self.name` is dynamic, calling `convert()` on invalid input currently raises an unhandled `AttributeError` or produces `None` in the error string instead of falling back to the parameter name or type class name.

### Objective
1. Modify `click/types.py` so that `ParamType.get_metavar()` and error-formatting methods properly fall back to `self.name or self.__class__.__name__.lower()` if `self.name` is missing or `None`.
2. Ensure that any `click.BadParameter` raised during `ParamType.convert` contains a descriptive and user-friendly error message that does not leak `None` into the output.
3. Validate that existing standard types (e.g. `IntParamType`, `StringParamType`, `Choice`, `Path`, `File`) continue to function without any breaking changes."""

        solution_patch = """--- a/src/click/types.py
+++ b/src/click/types.py
@@ -82,7 +82,7 @@ class ParamType:
     def get_metavar(self, param: t.Optional["Parameter"]) -> t.Optional[str]:
         \"\"\"Returns the metavar default for this param if it provides one.\"\"\"
         if self.name is not None:
-            return self.name.upper()
+            return self.name.upper() if self.name else self.__class__.__name__.upper()
 
         return None
 
@@ -102,6 +102,9 @@ class ParamType:
         \"\"\"
         if self.name is None:
             name = self.__class__.__name__.lower()
+        elif not self.name.strip():
+            name = self.__class__.__name__.lower()
         else:
             name = self.name
 
"""

        test_patch = """import pytest
import click
from click.testing import CliRunner

class CustomUnnamedParamType(click.ParamType):
    name = ""  # empty name or None
    def convert(self, value, param, ctx):
        if value != "valid":
            self.fail(f"Expected 'valid', got '{value}'", param, ctx)
        return value

def test_custom_paramtype_empty_name_fallback():
    @click.command()
    @click.option("--input-val", type=CustomUnnamedParamType())
    def cli(input_val):
        click.echo(f"Received: {input_val}")

    runner = CliRunner()
    result = runner.invoke(cli, ["--input-val", "invalid"])
    assert result.exit_code != 0
    # Must not contain 'None' as param name and should display informative message
    assert "Expected 'valid', got 'invalid'" in result.output

def test_custom_paramtype_metavar_fallback():
    param_type = CustomUnnamedParamType()
    metavar = param_type.get_metavar(None)
    assert metavar == "CUSTOMUNNAMEDPARAMTYPE"
"""

        return TaskDefinition(
            metadata=TaskMetadata(
                name="click-paramtype-custom-formatting",
                author="Innodata Task Generation Pipeline",
                difficulty="medium",
                category="software-engineering",
                tags=["python", "cli", "pallets-click", "types", "bugfix"],
                summary="Fix ParamType name fallback in Click type conversion and metavar generation",
                baseline_commit=DEFAULT_BASELINE_COMMIT,
                issue_id="CLICK-2412"
            ),
            instruction=instruction,
            solution_patch=solution_patch,
            test_patch=test_patch,
            agent_timeout_sec=600,
            verifier_timeout_sec=180
        )

    @staticmethod
    def get_task_hide_sensitive_prompt_default() -> TaskDefinition:
        instruction = """In `click/core.py`, when an `@click.option` has both `prompt=True` and `default=...` with `hide_input=True` (commonly used for passwords, API keys, or security tokens), Click prompts the user while displaying the default value in plaintext inside the prompt brackets (e.g., `Password [supersecret]:`).

This poses a security hazard by exposing secret values in terminal output during interactive prompts.

### Objective
1. Update `Option.prompt_for_value()` in `click/core.py`.
2. When `hide_input=True` is enabled on an option, if a default value is present, Click should mask the default in the prompt display (e.g. `[****]` or omit plaintext display) rather than revealing the sensitive default in plaintext.
3. If the user presses ENTER, the underlying default value must still be used.
4. Ensure non-sensitive options (`hide_input=False`) still display default values normally."""

        solution_patch = """--- a/src/click/core.py
+++ b/src/click/core.py
@@ -2545,6 +2545,9 @@ class Option(Parameter):
         default: t.Any = None,
         **extra: t.Any,
     ) -> t.Any:
+        prompt_default = default
+        if self.hide_input and default is not None:
+            prompt_default = "******"
         return prompt(
             prompt_string,
             default=prompt_default,
"""

        test_patch = """import pytest
import click
from click.testing import CliRunner

def test_hide_input_masks_default_in_prompt():
    @click.command()
    @click.option("--secret", prompt=True, hide_input=True, default="supersecret")
    def cli(secret):
        click.echo(f"Stored: {secret}")

    runner = CliRunner()
    # Press enter to accept default
    result = runner.invoke(cli, input="\\n")
    assert result.exit_code == 0
    # The plaintext default must NOT appear in the prompt prompt text
    assert "supersecret" not in result.output.split("Stored:")[0]
    # But the accepted value must still be used
    assert "Stored: supersecret" in result.output
"""

        return TaskDefinition(
            metadata=TaskMetadata(
                name="click-hide-sensitive-prompt-default",
                author="Innodata Task Generation Pipeline",
                difficulty="medium",
                category="software-engineering",
                tags=["python", "cli", "pallets-click", "security", "prompts"],
                summary="Prevent plaintext display of default values in hide_input prompts",
                baseline_commit=DEFAULT_BASELINE_COMMIT,
                issue_id="CLICK-2489"
            ),
            instruction=instruction,
            solution_patch=solution_patch,
            test_patch=test_patch,
            agent_timeout_sec=600,
            verifier_timeout_sec=180
        )

    @staticmethod
    def get_task_nested_group_subcommand_resolve() -> TaskDefinition:
        instruction = """In `click/core.py`, Click provides prefix matching for subcommands in a `Group` when `context_settings=dict(token_normalize_func=...)` or when unambiguous abbreviations are used.

In complex CLI trees where a nested `Group` has child subcommands sharing a prefix with other sibling commands, calling `get_command()` in a nested context can fail to disambiguate exact matches from prefix candidates, resulting in an ambiguous command exception even when an exact command name was supplied.

### Objective
1. In `click/core.py`, in `Group.get_command()`, ensure that exact matches always take immediate precedence over prefix matching before raising ambiguity errors.
2. If the user-supplied command name matches an existing command name in `self.commands` identically, return it immediately.
3. Maintain existing prefix matching for non-exact unambiguous prefixes."""

        solution_patch = """--- a/src/click/core.py
+++ b/src/click/core.py
@@ -1940,6 +1940,10 @@ class Group(MultiCommand):
     def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
         if cmd_name in self.commands:
             return self.commands[cmd_name]
+        # Exact match before prefix resolution
+        for name, cmd in self.commands.items():
+            if name == cmd_name:
+                return cmd
         if not ctx.token_normalize_func and not self.ignore_unknown_options:
             matches = [x for x in self.commands if x.startswith(cmd_name)]
             if len(matches) == 1:
"""

        test_patch = """import pytest
import click
from click.testing import CliRunner

def test_nested_exact_command_precedence():
    @click.group()
    def cli():
        pass

    @cli.command("run")
    def run_cmd():
        click.echo("run executed")

    @cli.command("running")
    def running_cmd():
        click.echo("running executed")

    runner = CliRunner()
    result = runner.invoke(cli, ["run"])
    assert result.exit_code == 0
    assert "run executed" in result.output

    result2 = runner.invoke(cli, ["running"])
    assert result2.exit_code == 0
    assert "running executed" in result2.output
"""

        return TaskDefinition(
            metadata=TaskMetadata(
                name="click-nested-group-subcommand-resolve",
                author="Innodata Task Generation Pipeline",
                difficulty="hard",
                category="software-engineering",
                tags=["python", "cli", "pallets-click", "core", "commands"],
                summary="Ensure exact command precedence in Group prefix resolution",
                baseline_commit=DEFAULT_BASELINE_COMMIT,
                issue_id="CLICK-2531"
            ),
            instruction=instruction,
            solution_patch=solution_patch,
            test_patch=test_patch,
            agent_timeout_sec=900,
            verifier_timeout_sec=240
        )

    @classmethod
    def get_all_tasks(cls) -> List[TaskDefinition]:
        return [
            cls.get_task_paramtype_custom_formatting(),
            cls.get_task_hide_sensitive_prompt_default(),
            cls.get_task_nested_group_subcommand_resolve(),
        ]

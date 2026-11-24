<!-- CANARY_STRING: harbor_task_click-nested-group-subcommand-resolve_verified -->
# Task Objective: Ensure exact command precedence in Group prefix resolution
## Background
You are operating inside the repository `pallets/click` checked out at baseline commit `e0d8b5847e2ef30fa27ce803405c19be38d17ba7`.
## Problem Description
In `click/core.py`, Click provides prefix matching for subcommands in a `Group` when `context_settings=dict(token_normalize_func=...)` or when unambiguous abbreviations are used.
In complex CLI trees where a nested `Group` has child subcommands sharing a prefix with other sibling commands, calling `get_command()` in a nested context can fail to disambiguate exact matches from prefix candidates, resulting in an ambiguous command exception even when an exact command name was supplied.
### Objective
1. In `click/core.py`, in `Group.get_command()`, ensure that exact matches always take immediate precedence over prefix matching before raising ambiguity errors.
2. If the user-supplied command name matches an existing command name in `self.commands` identically, return it immediately.
3. Maintain existing prefix matching for non-exact unambiguous prefixes.
## Requirements & Constraints
1. Edit the relevant files directly in `/workspace/click`.
2. Do not modify external dependencies or environment configurations.
3. Ensure all existing `click` tests continue to pass without regressions.
4. Your solution will be validated by running the verification suite via `pytest /workspace/tests/test_verifier.py`.

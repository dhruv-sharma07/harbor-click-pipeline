<!-- CANARY_STRING: harbor_task_click-paramtype-custom-formatting_verified -->
# Task Objective: Fix ParamType name fallback in Click type conversion and metavar generation
## Background
You are operating inside the repository `pallets/click` checked out at baseline commit `e0d8b5847e2ef30fa27ce803405c19be38d17ba7`.
## Problem Description
In `click/types.py`, when a custom `ParamType` subclass overrides `convert()` or fails validation, Click formats the error message using `self.get_missing_message(param)` or `self.name`.
However, when a subclass does not define a `name` attribute or when `self.name` is dynamic, calling `convert()` on invalid input currently raises an unhandled `AttributeError` or produces `None` in the error string instead of falling back to the parameter name or type class name.
### Objective
1. Modify `click/types.py` so that `ParamType.get_metavar()` and error-formatting methods properly fall back to `self.name or self.__class__.__name__.lower()` if `self.name` is missing or `None`.
2. Ensure that any `click.BadParameter` raised during `ParamType.convert` contains a descriptive and user-friendly error message that does not leak `None` into the output.
3. Validate that existing standard types (e.g. `IntParamType`, `StringParamType`, `Choice`, `Path`, `File`) continue to function without any breaking changes.
## Requirements & Constraints
1. Edit the relevant files directly in `/workspace/click`.
2. Do not modify external dependencies or environment configurations.
3. Ensure all existing `click` tests continue to pass without regressions.
4. Your solution will be validated by running the verification suite via `pytest /workspace/tests/test_verifier.py`.

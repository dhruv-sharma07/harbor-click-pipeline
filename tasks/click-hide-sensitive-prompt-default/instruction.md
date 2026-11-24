<!-- CANARY_STRING: harbor_task_click-hide-sensitive-prompt-default_verified -->
# Task Objective: Prevent plaintext display of default values in hide_input prompts
## Background
You are operating inside the repository `pallets/click` checked out at baseline commit `e0d8b5847e2ef30fa27ce803405c19be38d17ba7`.
## Problem Description
In `click/core.py`, when an `@click.option` has both `prompt=True` and `default=...` with `hide_input=True` (commonly used for passwords, API keys, or security tokens), Click prompts the user while displaying the default value in plaintext inside the prompt brackets (e.g., `Password [supersecret]:`).
This poses a security hazard by exposing secret values in terminal output during interactive prompts.
### Objective
1. Update `Option.prompt_for_value()` in `click/core.py`.
2. When `hide_input=True` is enabled on an option, if a default value is present, Click should mask the default in the prompt display (e.g. `[****]` or omit plaintext display) rather than revealing the sensitive default in plaintext.
3. If the user presses ENTER, the underlying default value must still be used.
4. Ensure non-sensitive options (`hide_input=False`) still display default values normally.
## Requirements & Constraints
1. Edit the relevant files directly in `/workspace/click`.
2. Do not modify external dependencies or environment configurations.
3. Ensure all existing `click` tests continue to pass without regressions.
4. Your solution will be validated by running the verification suite via `pytest /workspace/tests/test_verifier.py`.

import pytest
import click
from click.testing import CliRunner

def test_hide_input_masks_default_in_prompt():
    @click.command()
    @click.option("--secret", prompt=True, hide_input=True, default="supersecret")
    def cli(secret):
        click.echo(f"Stored: {secret}")

    runner = CliRunner()
    # Press enter to accept default
    result = runner.invoke(cli, input="\n")
    assert result.exit_code == 0
    # The plaintext default must NOT appear in the prompt prompt text
    assert "supersecret" not in result.output.split("Stored:")[0]
    # But the accepted value must still be used
    assert "Stored: supersecret" in result.output

import pytest
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

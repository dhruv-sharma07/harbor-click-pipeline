import pytest
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

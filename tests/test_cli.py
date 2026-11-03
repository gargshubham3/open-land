from click.testing import CliRunner
from land.cli import cli

def test_cli_convert():
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", "--hec", "1.0", "--are", "20.0"])
    assert result.exit_code == 0
    assert "Square Meters" in result.output
    assert "Gunthas" in result.output

def test_cli_audit():
    runner = CliRunner()
    text = "गाव नमुना ७. जिल्हा: Pune. गट: 50. खातेदार: मारुती पवार."
    result = runner.invoke(cli, ["audit", text, "--state", "Maharashtra"])
    assert result.exit_code == 0
    assert "Marketability Score" in result.output

def test_cli_report():
    runner = CliRunner()
    text = "गाव नमुना ७. जिल्हा: Pune. गट: 50. खातेदार: मारुती पवार."
    result = runner.invoke(cli, ["report", text, "--state", "Maharashtra"])
    assert result.exit_code == 0
    assert "TITLE SEARCH & VERIFICATION REPORT" in result.output

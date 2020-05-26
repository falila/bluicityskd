from click.testing import CliRunner
from bcity.cli import config, login

def test_login():
  runner = CliRunner()
  result = runner.invoke(login)
  assert result.exit_code == 0




def test_config():
    """ Should create a new APi key"""
    pass

def test_report():
    """" Should be able to show the current report file"""
    pass

import typer
from rich import print
from rich.pretty import pprint
from rich.table import Table
import sys

from BrowserApex.cli.main import app
from BrowserApex.cli.utils import get_config_path, get_config


@app.command(name='config')
def project_config(
    ):
    """
    Show project configuration.

    Search `rfapex.toml` in the current project.
    Root of project contains `robot.toml` or `pyproject.toml`
    """

    p = get_config_path()
    if p is None:
        print(f"No configuration found. Exitting...")
        sys.exit(1)

    cnf = get_config(p)
    t = Table("Key", "Value", title='Output')
    for k, v in cnf['output'].items():
        t.add_row(k, v)
    print(t)

    if 'export' in cnf:
        pass

    if 'keywords' in cnf:
        t = Table("Key", "Value", title='Keywords')
        for k, v in cnf['keywords'].items():
            t.add_row(k, v)
        print(t)
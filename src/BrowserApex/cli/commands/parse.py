import typer
from typing import Annotated
import yaml
from rich import print
from pathlib import Path

#from BrowserApex.cli.utils import get_template
from BrowserApex.cli.main import app
from python_oracle_apex import parse_apex_file

@app.command(name='parse')
def project_parse(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml, apx)")]
    ):
    """
    Parse file and dump ast.

    """
    page = None

    fn = Path(pagefile)
    if fn.suffix == '.apx':
        page = parse_apex_file(fn)

    print(page)
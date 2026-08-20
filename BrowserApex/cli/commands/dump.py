import typer
from typing import Annotated
import yaml
from rich import print

#from BrowserApex.cli.utils import get_template
from BrowserApex.cli.main import app

@app.command(name='dump')
def project_dump(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml)")]
    ):
    """
    Dump project raw yaml->dict.

    """
    data = None
    with open(pagefile, 'r') as f:
        data = yaml.safe_load(f)
    # print(data)


    print(data)
import typer
from rich import print


#from BrowserApex.cli.utils import get_template
from BrowserApex.cli.main import app


@app.command(name='config')
def project_config(
    ):
    """
    Show project configuration.

    Search `rfapex.ini` in the current project.
    Root of project contains `robot.toml` or `pyproject.toml`
    """

    print("CONFIG")
import typer
from dotenv import load_dotenv
from BrowserApex import __VERSION__

load_dotenv()

app = typer.Typer(
    help=f"""CLI for supporting development of Page Object Models.

Page exported as readable format (yaml) is used as source for generating POM resources for RobotFramework.

Version: {__VERSION__}
""",
    add_completion=True)

from BrowserApex.cli import commands


def main():                   # pragma: no cover
    app()


if __name__ == '__main__':    # pragma: no cover
    main()
import typer
from typing import Annotated
import yaml
from rich import print

#from BrowserApex.cli.utils import get_template
from BrowserApex.cli.main import app
from BrowserApex.cli.apex.grammar import grammar, ApxNodeVisitor

@app.command(name='parse')
def project_parse(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml, apx)")]
    ):
    """
    Parse file and dump ast.

    """
    data = None
    with open(pagefile, 'r') as f:
        data = f.read()
    # print(data)

    nodes = grammar.parse(data)
    print(nodes)

    visitor = ApxNodeVisitor()
    output = visitor.visit(nodes)
    print(output)
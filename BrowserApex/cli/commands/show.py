import typer
from rich import print
from typing import Annotated
import yaml
from rich import print
from rich.table import Table

#from BrowserApex.cli.utils import get_template
from BrowserApex.cli.main import app

@app.command(name='show')
def project_show(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml)")]
    ):
    """
    Show project.

    """
    data = None
    with open(pagefile, 'r') as f:
        data = yaml.safe_load(f)
    # print(data)

    print("Page:")
    print(f"id: {data['id']}")
    print(f"name: {data['identification']['name']}")
    print(f"alias: {data['identification']['alias']}")


    table = Table(title='Regions')
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Template")
    table.add_column("Parent")

    for region in data['regions']:
        ident = region['identification']
        layout = region['layout']
        appearance = region.get('appearance', dict(template='-'))
        table.add_row(ident['name'], ident['type'], appearance['template'],layout['parent-region'])

    print(table)

    table = Table(title='Page items')
    table.add_column("Seq.")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Label")
    table.add_column("Parent")
    for pageitem in data['page-items']:
        ident = pageitem['identification']
        label = pageitem.get('label', dict(label='-'))
        
        layout = pageitem['layout']

        table.add_row(str(layout['sequence']), ident['name'], ident['type'], label.get('label','[red]?[/red]'), layout['region'])
    print(table)

    table = Table(title='Buttons')
    table.add_column("Seq.")
    table.add_column("Name")
    table.add_column("Label")
    table.add_column("Region")
    for button in data["buttons"]:
        ident = button['identification']
        layout = button['layout']
        table.add_row(str(layout['sequence']), ident['button-name'], ident['label'], layout['region'])
    print(table)
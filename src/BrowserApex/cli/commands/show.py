import typer
from rich import print
from typing import Annotated
from rich.table import Table
from pathlib import Path

from BrowserApex.cli.main import app
from python_oracle_apex import parse_yaml_file, parse_apex_file

@app.command(name='show')
def project_show(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml)")]
    ):
    """
    Show project.

    """
    data = None
    fn = Path(pagefile)
    match fn.suffix:
        case '.apx':
            page = parse_apex_file(fn)
        case '.yaml' | '.yml':
            page = parse_yaml_file(fn)
        case _:
            raise RuntimeWarning("Unsupported file")

    print("Page:")
    print(f"id: {page.component_id}")
    print(f"name: {page.name}")
    print(f"alias: {page.alias}")


    table = Table(title='Regions')
    table.add_column("Component ID")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Template")
    table.add_column("Parent")

    for region in page.regions:
        table.add_row(str(region.component_id), region.name, region.type, region.appearance['template'],region.layout['parentRegion'])

    print(table)
    
    table = Table(title='Page items')
    table.add_column("Seq.")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Label")
    table.add_column("Region")
    for pageitem in page.page_items:
        table.add_row( str(pageitem.layout['sequence']), pageitem.name, pageitem.type, pageitem.label.get('label', '[red]?[/red]'), pageitem.layout['region'] ) 
    print(table)

    table = Table(title='Buttons')
    table.add_column("Seq.")
    table.add_column("Name")
    table.add_column("Label")
    table.add_column("Region")
    for button in page.buttons:
        table.add_row(str(button.layout['sequence']), button['buttonName'], button['label'], button.layout['region'])
    print(table)
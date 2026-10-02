import typer
import sys
from rich import print
from typing import Annotated
from rich.table import Table
from pathlib import Path

from BrowserApex.cli.main import app
from BrowserApex.cli.utils import get_config_path, get_config, get_page_file
from python_oracle_apex import parse_page_file, parse_apex_file

@app.command(name='show')
def project_show(
        pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml or apx)")] = None,
        page_id: Annotated[int, typer.Option("--page", "-p", help="Page ID.")] = None
    ):
    """
    Show project.

    """
    data = None
    p = get_config_path()
    print(f":beer: Reading config from: {p}")
    cnf = get_config(p)
    
    if p is None:
        print(f"No configuration found. Exitting...")
        sys.exit(1)


    if page_id:
        print(f"Page: {page_id}")
        fn = get_page_file(cnf, page_id=page_id)

    elif pagefile is not None:
        fn = Path(pagefile)
        
    else:
        print("No page id or page file found.")
        sys.exit(1)

    match fn.suffix:
        case '.apx':
            page = parse_apex_file(fn)
        case '.yaml' | '.yml':
            page = parse_page_file(fn)
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
    table.add_column("Slot")

    for region in page.regions:
        table.add_row(str(region.component_id), 
                      region.name, 
                      region.type, 
                      region.appearance['template'],
                      region.layout['parentRegion'],
                      region.layout['slot'],
                      )

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


if __name__=='__main__':
    project_show('P:/Downloads/brookstrut_page_1.apx')
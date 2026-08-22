import typer
from rich import print
from typing import Annotated
import yaml
from rich import print
from rich.table import Table
import sys

from BrowserApex.cli.main import app
from BrowserApex.cli.utils import get_config_path, get_config, get_template
from BrowserApex.cli.apex import Page


@app.command(name='generate')
def page_generate(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml)")]
    ):
    """
    Generate page object.

    Existing page will be modified. Please do not remove the special comment lines!
    Outside the special blocks existing code will be preserved.
    Inside the special blocks existing code will be replaced.

    """
    data = None
    p = Page()
    p.load(pagefile)

    with open(pagefile, 'r') as f:
        data = yaml.safe_load(f)
    # print(data)

    page = dict(
        id=data['id'],
        name=data['identification']['name'],
        alias=data['identification']['alias']
    )

    p = get_config_path()
    if p is None:
        print(f"No configuration found. Exitting...")
        sys.exit(1)

    print(f":beer: Reading config from: {p}")

    cnf = get_config(p)
    print(cnf)
    template_path = p
    main_template = get_template("pageobject", template_path)

    pageobject_resource = f"{page['id']}_{page['name'].replace(' ','_')}.resource"
    fn = p / cnf['output']['folder'] / pageobject_resource
    if not fn.exists():
        print(f":floppy_disk: Scaffolding resource {fn}")
        with open(fn, 'w') as f:
            f.write(main_template.render())

        # TODO: Update main resource to include new pageobject resource

    print(f":lab_coat: Processing page {page['id']} - {page['name']}")
    regions = {}
    for pageitem in data['page-items']:
        ident = pageitem['identification']
        label = pageitem.get('label', dict(label='-'))
        
        layout = pageitem['layout']
        region = layout['region']
        if region not in regions:
            regions[region] = dict(
                name=region,
                fields=[],
                page_buttons=[],
                has_classic_report=False,
                is_wizard=False,
                has_tabs=False
            )
        regions[region]['fields'].append(pageitem)

    for name, region in regions.items():
        print(f"{name} nr fields: {len(region['fields'])}")


    print(f":floppy_disk: Reading resource {fn}")
    with open(fn, 'r') as f:
        lines = f.readlines()

    result = []
    inside_block = False
    for line in lines:
        l = line.strip()

        if l.startswith('### PAGEGEN:BEGIN:SETTINGS'):
            inside_block = True

        elif l.startswith('### PAGEGEN:END:SETTINGS'):
            result.append('# TODO: SETTINGS')

            inside_block = False

        elif l.startswith('### PAGEGEN:BEGIN:VARIABLES'):
            inside_block = True

        elif l.startswith('### PAGEGEN:END:VARIABLES'):
            variables_template = get_template('variables', template_path)
            variables_lines = variables_template.render()
            result.extend(variables_lines.split("\n"))
            inside_block = False

        elif l.startswith('### PAGEGEN:BEGIN:KEYWORDS'):
            inside_block = True
            
        elif l.startswith('### PAGEGEN:END:KEYWORDS'):
            result.append('# TODO: KEYWORDS')
            inside_block = False

        elif inside_block:
            continue

        result.append(l)

    print(f":floppy_disk: Writing updated resource {fn}")
    with open(fn, 'w') as f:
        f.write("\n".join(result))
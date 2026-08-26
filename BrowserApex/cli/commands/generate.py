import typer
from rich import print
from typing import Annotated
import yaml
from rich import print
from rich.table import Table
import sys
from operator import itemgetter

from BrowserApex.cli.main import app
from BrowserApex.cli.utils import get_config_path, get_config, get_template
from BrowserApex.cli.apex import *

current_page = None



def build_structure():
    regions = {}
    for pageitem in current_page.page_items:
        region_name = pageitem.layout.region
        r = current_page.get_region(region_name)
        if type(r) is list:
            for reg in r:
                if reg.type in ['Static Content', 'staticContent']:
                    region = reg
        else:
            region = r
        
        name = region.name

        if name not in regions:
            regions[name] = dict(
                region=region,
                name=name,
                fields=[],
                page_buttons=[],
                has_classic_report=False,
                has_form=False,
                is_wizard=False,
                has_tabs=False
            )
        regions[name]['fields'].append(pageitem)

    for button in current_page.buttons:
        region_name = button.layout.region
        r = current_page.get_region(region_name)
        if type(r) is list:
            for reg in r:
                if reg.type in ['Static Content', 'staticContent']:
                    region = reg
        else:
            region = r
        
        name = region.name

        if name not in regions:
            regions[name] = dict(
                region=region,
                name=name,
                fields=[],
                page_buttons=[],
                has_classic_report=False,
                has_form=False,
                is_wizard=False,
                has_tabs=False
            )
        regions[name]['page_buttons'].append(pageitem)

    for r in regions.values():
        # For fields we only need a label, id and type, example:
        # ...    Label=P1_NAME:TextField

        # List is also sorted on sequence

        newlist = [(x.label.label or x.name, x.name, x.type[0].upper() + x.type[1:]) for x in sorted(r['fields'], key=lambda d: d['layout']['sequence'])]
        print(newlist)
        r['fields'] = newlist

    return regions

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
    global current_page

    data = None
    fn = Path(pagefile)
    match fn.suffix:
        case '.apx':
            current_page = parse_apex_file(fn)
        case '.yaml' | '.yml':
            current_page = parse_yaml_file(fn)
        case _:
            raise RuntimeWarning("Unsupported file")

    p = get_config_path()
    if p is None:
        print(f"No configuration found. Exitting...")
        sys.exit(1)

    print(f":beer: Reading config from: {p}")

    cnf = get_config(p)
    print(cnf)
    template_path = p
    main_template = get_template("pageobject", template_path)

    pageobject_resource = f"{current_page.component_id}_{current_page.name.replace(' ','_')}.resource"
    fn = p / cnf['output']['folder'] / pageobject_resource
    if not fn.exists():
        print(f":floppy_disk: Scaffolding resource {fn}")
        with open(fn, 'w') as f:
            f.write(main_template.render())

        # TODO: Update main resource to include new pageobject resource

    print(f":lab_coat: Processing page {current_page.component_id} - {current_page.name}")
    
    regions = build_structure()
    for name, region in regions.items():
        print(f"{name} nr fields: {len(region['fields'])} button: {len(region['page_buttons'])}")


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
            variables_lines = variables_template.render(page=current_page, blocks=regions)
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



if __name__ == '__main__':    # pragma: no cover

    # page_generate('examples/test.apx')
    # page_generate('examples/f300_page_9999.yaml')
    page_generate('examples/f300_page_9999.yaml')
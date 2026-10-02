import typer
import re
from rich import print
from typing import Annotated
from rich import print
import sys
from pathlib import Path

from BrowserApex.cli.main import app
from BrowserApex.cli.utils import get_config_path, get_config, get_template, get_page_file, get_breadcrumb_file
from python_oracle_apex import *

current_page = None


def _get_region(region_ref: str) -> Region:
    pos = region_ref.find('@')
    if pos > 0:  # APEX < 26
        region_ref = region_ref[pos:]

    r = current_page.get_region(region_ref)
    if type(r) is list:
        for reg in r:
            if reg.type in ['Static Content', 'staticContent']:
                region = reg
    else:
        region = r            
    return region
            

def build_structure():
    regions = {}
    for region in current_page.regions:
        name = region.name
        region_type = region.type
        region_template = region.appearance['template']
        has_classic_report = region_type in ['Classic Report']
        regions[str(region.component_id)] = dict(
            region=region,
            slot=region.layout['slot'],
            name=name,
            type=region_type,
            template=region_template,
            fields=[],
            buttons=[],
            locator_path=[],
            has_classic_report=has_classic_report,
            has_form=False,
            is_wizard=False,
            has_tabs=False
        )

    for pageitem in current_page.page_items:
        region_ref = pageitem.layout.region
        region = _get_region(region_ref)
        start_region = region
        while region.appearance['template'] not in ['Standard']:
            region_ref = region.layout['parentRegion']
            if region_ref in [None, '', 'No Parent']:
                region = start_region
                break

            region = _get_region(region_ref)

        
        region_id = str(region.component_id)

        if region_id not in regions:
            raise "Unknown region"
        
        regions[region_id]['fields'].append(pageitem)

    for button in current_page.buttons:
        region_ref = button.layout.region
        region = _get_region(region_ref)
        start_region = region
        while region.appearance['template'] not in ['Standard']:
            region_ref = region.layout['parentRegion']
            if region_ref in [None, '', 'No Parent']:
                region = start_region
                break
            
            region = _get_region(region_ref)

        region_id = str(region.component_id)
        
        if region_id not in regions:
            raise "Unknown region"
        
        regions[region_id]['buttons'].append(button)

    region_names = {}
    for r in regions.values():
        # For fields we only need a label, id and type, example:
        # ...    Label=P1_NAME:TextField

        # List is also sorted on sequence

        newlist = [(x.label.label or x.name, x.name, x.type[0].upper() + x.type[1:]) for x in sorted(r['fields'], key=lambda d: d['layout']['sequence'])]
        r['fields'] = newlist
        r['fullname'] = r['name']
        if len(newlist) > 0:
            region_name = r['name']
            if region_name in region_names:
                if type(region_names[region_name]) is list:
                    region_names[region_name].append(r)
                else:
                    region_names[region_name] = [region_names[region_name], r]
            else:
                region_names[region_name] = r

        # determine locator path
        if r['template'] in ['Standard', 'standard']:
            r['locator_path'].append(('Region', r['name']))

    for k, v in region_names.items():
        if type(v) is list:
            nr = 1
            # name is not unique
            for r in v:
                region_ref = r['region'].layout['parentRegion']
                parent = _get_region(region_ref)

                r['name_rf'] = r['name'].upper() + '_' + parent.name.upper()
                r['fullname'] = r['name'] + ' ' + parent.name
                nr += 1
        else:
            v['name_rf'] = v['name'].upper()

        v['name_rf'] = v['name_rf'].replace(" ", "_")
        v['name_rf'] = v['name_rf'].replace("-", "_")
    return regions


def generate_pageobjects_resource(folder: Path, resource_fn: Path):
    with open(resource_fn, 'r') as f:
        lines = f.readlines()

    result = []
    inside_block = False
    for line in lines:
        l = line.rstrip()

        if l.startswith('### PAGEGEN:BEGIN:RESOURCES'):
            inside_block = True

        elif l.startswith('### PAGEGEN:END:RESOURCES'):
            result.append('# TODO: RESOURCES')

            files = folder.glob('*.resource')
            for fn in files:
                if resource_fn.name != fn.name:
                    if re.search(r'^\d+_.*\.resource$', fn.name):
                        result.append(f"Resource    ./{fn.name}")

            inside_block = False

        elif inside_block:
            continue

        result.append(l)
    
    print(f":floppy_disk: Writing updated pageobjects resource {resource_fn}")
    with open(resource_fn, 'w') as f:
        f.write("\n".join(result))


def read_page_file(fn: Path):
    global current_page
    
    match fn.suffix:
        case '.apx':
            current_page = parse_apex_file(fn)
        case '.yaml' | '.yml':
            current_page = parse_page_file(fn)
        case _:
            raise RuntimeWarning("Unsupported file")




def read_page(cnf, page_id):
    p = get_page_file(cnf, page_id)
    read_page_file(p)


def read_breadcrumbs(cnf):
    p: Path = get_breadcrumb_file(cnf)

    match p.suffix:
        case ".apx":
            return parse_apex_file(p)
        case ".yaml":
            return parse_breadcrumb_file(p)

@app.command(name='generate')
def page_generate(
    pagefile: Annotated[str, typer.Argument(help="The filename of exported page (yaml or apx)")] = None,
    page_id: Annotated[int, typer.Option("--page", "-p", help="Page ID.")] = None
    ):
    """
    Generate page object.

    Existing page will be modified. Please do not remove the special comment lines!
    Outside the special blocks existing code will be preserved.
    Inside the special blocks existing code will be replaced.

    """
    global current_page

    p = get_config_path()
    print(f":beer: Reading config from: {p}")
    cnf = get_config(p)
    
    if p is None:
        print(f"No configuration found. Exitting...")
        sys.exit(1)

    if page_id:
        print(f"Page: {page_id}")
        read_page(cnf, page_id=page_id)

    elif pagefile is not None:
        fn = Path(pagefile)
        read_page_file(fn)
        page_id = current_page.page
    else:
        print("No page id or page file found.")
        sys.exit(1)
    
    
    breadcrumbs: Breadcrumb = read_breadcrumbs(cnf)
    active_breadcrumb = 'CHANGEME'
    if breadcrumbs:
        crumb = breadcrumbs.get_by('pageNumber', page_id)
        if crumb:
            active_breadcrumb = crumb.name
        print(f"active breadcrumb: {active_breadcrumb}")
    

    
    template_path = p
    main_template = get_template("pageobject", template_path)
    resource_template = get_template("pageobjects-resource", template_path)

    pageobject_resource = f"{current_page.component_id}_{current_page.name.replace(' ','_').replace('-','_')}.resource"
    folder: Path = p / cnf['output']['folder']
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    fn = folder / pageobject_resource
    if not fn.exists():
        print(f":floppy_disk: Scaffolding resource {fn}")
        with open(fn, 'w') as f:
            f.write(main_template.render())

        # TODO: Update main resource to include new pageobject resource
        res_fn : Path = folder / cnf['output'].get('mainresource', 'pageobjects.resource')
        if not res_fn.exists():
            print(f":floppy_disk: Scaffolding page objects main resource {res_fn}")
            with res_fn.open('w') as f:
                f.write(resource_template.render())

        generate_pageobjects_resource(folder, res_fn)


    print(f":lab_coat: Processing page {current_page.component_id} - {current_page.name}")
    breadcrumb_region = None
    regions = build_structure()
    for component_id, region in regions.items():
        nr_fields = len(region['fields'])
        nr_buttons = len(region['buttons'])
        if region['type'] in ['Breadcrumb']:
            breadcrumb_region = region
        if nr_fields > 0 or nr_buttons > 0:
            print(f"'{region['name']} ({component_id})' "
                  f"fullname: '{region.get("fullname", "-")}' "
                  f"slot: {region['slot']}  parent: {region['region'].layout.parentRegion}   nr fields: {nr_fields} button: {nr_buttons}")


    keywords = {
        'page_is_shown': "Page Is Shown",
        'press_button': "Page Press Button",
        'fill': "Fill"
    }
    keywords.update(cnf['keywords'])
    print(keywords)

    print(f":floppy_disk: Reading resource {fn}")
    with open(fn, 'r') as f:
        lines = f.readlines()

    result = []
    inside_block = False
    for line in lines:
        l = line.rstrip()

        if l.startswith('### PAGEGEN:BEGIN:SETTINGS'):
            inside_block = True

        elif l.startswith('### PAGEGEN:END:SETTINGS'):
            result.append('# TODO: SETTINGS')

            inside_block = False

        elif l.startswith('### PAGEGEN:BEGIN:VARIABLES'):
            inside_block = True

        elif l.startswith('### PAGEGEN:END:VARIABLES'):
            variables_template = get_template('variables', template_path)
            variables_lines = variables_template.render(page=current_page, regions=regions)
            result.extend(variables_lines.split("\n"))
            inside_block = False

        elif l.startswith('### PAGEGEN:BEGIN:KEYWORDS'):
            inside_block = True
            
        elif l.startswith('### PAGEGEN:END:KEYWORDS'):
            keywords_template = get_template('keywords', template_path)
            keywords_lines = keywords_template.render(page=current_page, regions=regions, breadcrumb=breadcrumb_region, keywords=keywords, active_breadcrumb=active_breadcrumb)
            result.extend(keywords_lines.split("\n"))
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
    # page_generate('examples/f300_page_9999.yaml')
    # page_generate('P:/Downloads/f300_page_1100.yaml')
    page_generate('P:/Downloads/f300_page_2000.yaml')
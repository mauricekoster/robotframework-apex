from pathlib import Path
from BrowserApex.cli.apex import Page, Region, RegionLayout, RegionAppearance
import yaml

"""
Read YAML and transform to Page object.

Property names will be translated to the names used in de APEX Lang spec. (version 26.1)
"""

def make_group(mapper, data):
    d = {}
    for k, v in data.items():
        if k in mapper:
            d[mapper[k]] = v
        else:
            raise AttributeError(f"Unknown layout property '{k}'")
    return d


def make_region_layout(data):
    f = {
        'sequence': 'sequence',
        'parent-region': 'parentRegion',
        'slot': 'slot',
        'start-new-layout': 'startNewLayout',
        'start-new-row': 'startNewRow',
        'column': 'column',
        'new-column': 'newColumn',
        'column-span': 'columnSpan'
    }    
    d = make_group(f, data)
    return RegionLayout(d)



def make_region_appearance(data):
    f = {
        'icon': 'icon',
        'template': 'template',
        'template-options': 'templateOptions',
        'render-components': 'renderComponents',
    }    
    d = make_group(f, data)
    return RegionAppearance(d)


def make_region(region):
    r = Region(region['id'])
    for field in ['name', 'title', 'type']:
        if field in region['identification']:
            r.add_property(field, region['identification'][field])

    if 'layout' in region:
        l = make_region_layout(region['layout'])
        r.add_group('layout',  l)

    if 'appearance' in region:
        a = make_region_appearance(region['appearance'])
        r.add_group('appearance', a)
    return r


def parse_yaml_file(fn: Path) -> Page:

    with open(fn, 'r') as f:
        data = yaml.safe_load(f)

    

    page = Page(data['id'])
    for field in ['name', 'alias', 'title']:
        if field in data['identification']:
            page.add_property(field, data['identification'][field])

    for region in data['regions']:
        r = make_region(region)
        page.add_region(r)


    return page


if __name__ == '__main__':    # pragma: no cover

    page = parse_yaml_file("examples/f300_page_9999.yaml")

    for r in page.regions:
        print(r.component_id, r.name, r.type)
    
    print(page)

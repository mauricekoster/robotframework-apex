from pathlib import Path
from BrowserApex.cli.apex import *
import yaml

"""
Read YAML and transform to Page object.

Property names will be translated to the names used in de APEX Lang spec. (version 26.1)
"""

def make_properties(mapper, data, section, object: ApexObject):
    for field_src, field_dest in mapper.items():
        if field_src in data[section]:
            object.add_property(field_dest, data[section][field_src])

def make_group(mapper, data):
    d = {}
    for k, v in data.items():
        if k in mapper:
            d[mapper[k]] = v
        else:
            raise AttributeError(f"Unknown property '{k}'")
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
        'css-classes': 'cssClasses',
    }    
    d = make_group(f, data)
    return RegionAppearance(d)


def make_region(region):
    r = Region(region['id'])
    make_properties({
                    'name': 'name',
                    'title': 'title',
                    'type': 'type'
                }, 
                region, 'identification', r
                )

    if 'layout' in region:
        l = make_region_layout(region['layout'])
        r.add_group('layout',  l)

    if 'appearance' in region:
        a = make_region_appearance(region['appearance'])
        r.add_group('appearance', a)
    return r


def make_page_item_label(data):
    f = {
        'label': 'label',
        'alignment': 'alignment',
    }
    d = make_group(f, data)
    return PageItemLabel(d)

def make_page_item_layout(data):
    f = {
        'sequence': 'sequence',
        'region': 'region',
        'alignment': 'alignment',
        'slot': 'slot',
        'start-new-layout': 'startNewLayout',
        'start-new-row': 'startNewRow',
        'column': 'column',
        'new-column': 'newColumn',
        'column-span': 'columnSpan',
        'label-column-span': 'labelColumnSpan',
    }    
    d = make_group(f, data)
    return PageItemLayout(d)

def make_page_item_appearance(data):
    return {}


def make_page_item(page_item):
    p = PageItem(page_item['id'])
    make_properties({
                'name': 'name',
                'type': 'type'
            }, 
            page_item, 'identification', p
            )

    if 'label' in page_item:
        l = make_page_item_label(page_item['label'])
        p.add_group('label',  l)
        
    if 'layout' in page_item:
        l = make_page_item_layout(page_item['layout'])
        p.add_group('layout',  l)

    if 'appearance' in page_item:
        a = make_page_item_appearance(page_item['appearance'])
        p.add_group('appearance', a)
    return p


def make_button_layout(data):
    f = {
        'sequence': 'sequence',
        'region': 'region',
        'slot': 'slot',
        'column': 'column',
        'alignment': 'alignment',
        'new-column': 'newColumn',
        'column-span': 'columnSpan',
        'start-new-layout': 'startNewLayout',
        'start-new-row': 'startNewRow',

    }
    d = make_group(f, data)
    return ButtonLayout(d)

def make_button(data):
    b = Button(data['id'])
    make_properties({
        'button-name': 'buttonName',
        'label': 'label'
    }, data, 'identification', b)

    if 'layout' in data:
        l = make_button_layout(data['layout'])
        b.add_group('layout', l)

    return b


def parse_yaml_file(fn: Path) -> Page:

    with open(fn, 'r') as f:
        data = yaml.safe_load(f)

    

    page = Page(data['id'])
    for field in ['name', 'alias', 'title']:
        if field in data['identification']:
            page.add_property(field, data['identification'][field])

    for region in data['regions']:
        r = make_region(region)
        page.add_child(r)

    for page_item in data['page-items']:
        p = make_page_item(page_item)
        page.add_child(p)

    for button in data['buttons']:
        b = make_button(button)
        page.add_child(b)

    return page


if __name__ == '__main__':    # pragma: no cover

    page = parse_yaml_file("examples/f300_page_9999.yaml")

    for r in page.regions:
        print(r.component_id, r.name, r.type)
    
    print(page)

from pathlib import Path


class ApexGroup():
    def __init__(self, initial_data={}):
        self.properties = {}
        self.properties.update(initial_data)

    def __setitem__(self, key, value):
        self.properties[key] = value
    
    def __getitem__(self, key):
        return self.properties.get(key, None)


class ApexObject():
    def __init__(self, component_id=None, initial_data={}):
        self.component_id = component_id
        self.properties = {}
        self.properties.update(initial_data)
        self.groups = {}
        self.children = {}

    def __setitem__(self, key, value):
        if isinstance(value, ApexGroup):
            self.groups[key] = value
        elif isinstance(value, ApexObject):
            self.children[key] = value
        else:
            self.properties[key] = value
    
    def __getitem__(self, key):
        if key in self.groups:
            return self.groups.get(key, None)
        elif key in self.children:
            return self.children.get(key, None)
        else:
            return self.properties.get(key, None)


class RegionLayout(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

    @property
    def sequence(self):
        return self.properties.get('sequence', None)

    @property
    def parentRegion(self):
        return self.properties.get('parentRegion', None)

class RegionAppearance(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)



class Region():
    def __init__(self, component_id=None, initial_data={}):
        self.component_id = component_id
        self.properties = {}
        self.groups = {}
        self.properties.update(initial_data)
    
    def add_property(self, key, value):
        self.properties[key] = value
        
    def add_group(self, key, value):
        self.groups[key] = value

    @property
    def name(self):
        return self.properties.get('name', None)

    @property
    def title(self):
        return self.properties.get('title', None)

    @property
    def type(self):
        return self.properties.get('type', None)

    @property
    def layout(self):
        return self.groups.get('layout', RegionLayout())

    @property
    def appearance(self):
        return self.groups.get('appearance', RegionAppearance())
    


class PageItem:
    def __init__(self, component_id=None, initial_data={}):
        self.component_id = component_id
        self.properties = {}
        self.properties.update(initial_data)
        self.groups = {}

    def add_property(self, key, value):
            self.properties[key] = value
    
    def add_group(self, key, value):
        self.groups[key] = value

    @property
    def name(self):
        return self.properties.get('name', self.component_id)

    @property
    def type(self):
        return self.properties.get('type', None)


    @property
    def layout(self):
        return self.groups.get('layout', {})


class Page():
    def __init__(self, component_id=None, initial_data={}):
        self.component_id = component_id
        self.properties = initial_data
        self.groups = {}
        self.children = {}

    def __str__(self):
        return f"Page<#{self.page} name: {self.name}>"

    @property
    def page(self):
        return self.properties.get('page', self.component_id)

    @property
    def name(self):
        return self.properties['name']

    @property
    def title(self):
        return self.properties['title']

    @property
    def alias(self):
        return self.properties['alias']


    @property
    def appearance(self):
        return self.groups.get('appearance', None)

    @appearance.setter
    def appearance(self, value):
        self.groups['appearance'] = value

    def add_property(self, key, value):
        self.properties[key] = value

    def add_group(self, key, value):
        self.groups[key] = value

    def add_region(self, region: Region):
        self.children[region.component_id] = region
    
    def add_page_item(self, page_item: PageItem):
        self.children[page_item.component_id] = page_item

    @property
    def regions(self):
        return [x for _, x in self.children.items() if isinstance(x, Region)]
    
    @property
    def page_items(self):
        return [x for _, x in self.children.items() if isinstance(x, PageItem)]



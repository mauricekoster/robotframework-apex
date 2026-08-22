from pathlib import Path


class Region():
    def __init__(self, component_id=None):
        self.component_id = component_id
        self.properties = {}

    def __setitem__(self, key, value):
            self.properties[key] = value
    
    def __getitem__(self, key):
        return self.properties.get(key, None)
    

class Page:
    def __init__(self, component_id):
        self.page_id = None
        self.page_name = None
        self.page_alias = None
        self.component_id = component_id
        self.properties = {}
        self.regions = {}

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __getitem__(self, key):
        return self.properties.get(key, None)

    @property
    def appearance(self):
        return self.properties['appearance']

    def add_region(self, region: Region):
        self.regions[region.component_id] = region



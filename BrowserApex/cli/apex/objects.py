from pathlib import Path


class ApexGroup():
    def __init__(self, initial_data={}):
        self.properties = {}
        self.properties.update(initial_data)

    def __setitem__(self, key, value):
        self.properties[key] = value
    
    def __getitem__(self, key):
        return self.properties.get(key, None)

    def get(self, key, default=None):
        return self.properties.get(key, default)


class ApexObject():
    def __init__(self, component_id=None, initial_data={}):
        self.component_id = component_id
        self.properties = {}
        self.properties.update(initial_data)
        self.groups = {}
        self.children = []

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
    
    def add_property(self, key, value):
        self.properties[key] = value
    
    def add_group(self, key, value):
        self.groups[key] = value

    def add_child(self, child):
        self.children.append(child)


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



class Region(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)

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
    

class PageItemLabel(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

    @property
    def label(self):
        return self.properties.get('label', None) 


class PageItemSettings(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)


class PageItemLayout(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

    @property
    def sequence(self):
        return self.properties.get('sequence', None)

    @property
    def region(self):
        return self.properties.get('region', None)


class PageItemAppearance(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

class PageItemValidation(ApexGroup):
    def __init__(self, initial_data={}):
            super().__init__(initial_data)

class PageItemAdvanced(ApexGroup):
    def __init__(self, initial_data={}):
            super().__init__(initial_data)

class PageItemSessionState(ApexGroup):
    def __init__(self, initial_data={}):
            super().__init__(initial_data)

class PageItemSecurity(ApexGroup):
    def __init__(self, initial_data={}):
            super().__init__(initial_data)


class PageItem(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)

    @property
    def name(self):
        return self.properties.get('name', self.component_id)

    @property
    def type(self):
        return self.properties.get('type', None)


    @property
    def layout(self):
        return self.groups.get('layout', PageItemLayout())

    @property
    def label(self):
        return self.groups.get('label', PageItemLabel())
    

class ButtonLayout(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

    @property
    def sequence(self):
        return self.properties.get('sequence', None)

    @property
    def region(self):
        return self.properties.get('region', None)


class ButtonAppearance(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)

class ButtonBehavior(ApexGroup):
    def __init__(self, initial_data={}):
        super().__init__(initial_data)



class Button(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)

    @property
    def button_name(self):
        return self.properties.get('buttonName', None)

    @property
    def label(self):
        return self.properties.get('label', None)

    @property
    def layout(self):
        return self.groups.get('layout', ButtonLayout({}))


class DynamicActionExecution(ApexGroup):
    pass

class DynamicActionWhen(ApexGroup):
    pass

class DynamicActionClientSideCondition(ApexGroup):
    pass

class DynamicAction(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)


class ActionAffectedElements(ApexGroup):
    pass

class Action(ApexObject):
    pass

class Process(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)


class Page(ApexObject):
    def __init__(self, component_id=None, initial_data={}):
        super().__init__(component_id, initial_data)

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

    @property
    def regions(self):
        return [x for x in self.children if isinstance(x, Region)]
    
    @property
    def page_items(self):
        return [x for x in self.children if isinstance(x, PageItem)]

    @property
    def buttons(self):
        return [x for x in self.children if isinstance(x, Button)]

    @property
    def dynamic_actions(self):
        return [x for x in self.children if isinstance(x, DynamicAction)]

    @property
    def processes(self):
        return [x for x in self.children if isinstance(x, Process)]


    def get_region(self, reference_or_name):
        regions = [x for x in self.regions if x.component_id==reference_or_name[1:] or x.name==reference_or_name]
        if len(regions) == 1:
            return regions[0]
        elif len(regions) == 0:
            return None

        return regions
